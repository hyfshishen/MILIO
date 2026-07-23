# kv_compress_baseline.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import ctypes
from pycuSZp import cuSZp  # must expose .compress and .compress_fixed_ratio
import torch, ctypes


torch.set_grad_enabled(False)

class CuSZpKVCodec:
    def __init__(self, mode="fixed_ratio", eb=1e-2, ratio=4.0, sample_rate=500):
        self.lib = cuSZp()
        self.mode = mode
        self.eb = float(eb)
        self.ratio = float(ratio)
        self.sample_rate = int(sample_rate)

    @staticmethod
    def _to_fp32_contig(x: torch.Tensor) -> torch.Tensor:
        return x.contiguous().to(torch.float32)

# inside CuSZpKVCodec

    def _pad_to32(self, x32: torch.Tensor):
        flat = x32.view(-1)
        pad = (-flat.numel()) & 31  # next multiple of 32
        if pad:
            flat_padded = torch.empty(flat.numel() + pad, dtype=torch.float32, device=flat.device)
            flat_padded[:flat.numel()] = flat
            flat_padded[flat.numel():] = 0.0
            return flat_padded, flat.numel(), flat_padded.numel()
        else:
            return flat, flat.numel(), flat.numel()

    def compress_tensor(self, x: torch.Tensor):
        # Upcast & pad
        x32 = x.contiguous().to(torch.float32)
        flat, numel_orig, numel_padded = self._pad_to32(x32)
        if numel_padded < 32:
            # Too small for kernel assumptions; store raw
            return x32.view(torch.uint8), numel_orig * 4, {"shape": x.shape, "dtype": x.dtype, "raw": True}

        orig_bytes = numel_padded * 4  # we compress the padded length
        if self.mode == "error_bound":
            cap = max(orig_bytes * 6, orig_bytes + (8 << 20))
        else:
            cap = max(orig_bytes * 2, orig_bytes + (1 << 20))

        buf = torch.empty(cap, dtype=torch.uint8, device=flat.device)

        try:
            if self.mode == "fixed_ratio":
                rng = float((flat.max() - flat.min()).item())
                if not (rng > 0.0):
                    return x32.view(torch.uint8), numel_orig * 4, {"shape": x.shape, "dtype": x.dtype, "raw": True}
                cmp_size = self.lib.compress_fixed_ratio(
                    ctypes.c_void_p(flat.data_ptr()),
                    ctypes.c_void_p(buf.data_ptr()),
                    numel_padded, rng, self.sample_rate, self.ratio
                )
            else:  # error_bound
                cmp_size = self.lib.compress(
                    ctypes.c_void_p(flat.data_ptr()),
                    ctypes.c_void_p(buf.data_ptr()),
                    numel_padded, self.eb, data_type=0, mode=0
                )

            torch.cuda.synchronize()

        except RuntimeError as e:
            print(f"[cuSZp] compress kernel failed: {e}")
            # Abort run; context is poisoned. Better to exit than keep going.
            raise SystemExit(1)

        if cmp_size <= 0 or cmp_size > cap:
            # Defensive fallback to raw
            return x32.view(torch.uint8), numel_orig * 4, {"shape": x.shape, "dtype": x.dtype, "raw": True}

        return buf, int(cmp_size), {
            "shape": x.shape,
            "dtype": x.dtype,
            "raw": False,
            "numel_orig": numel_orig,
            "numel_padded": numel_padded
        }

    def decompress_tensor(self, buf: torch.Tensor, cmp_size: int, meta: dict, device):
        if meta.get("raw", False):
            out32 = buf.view(torch.float32).clone()
            return out32.view(meta["shape"]).to(meta["dtype"])

        numel_orig = int(meta["numel_orig"])
        numel_padded = int(meta["numel_padded"])
        out32_pad = torch.empty(numel_padded, dtype=torch.float32, device=device)

        self.lib.decompress(
            ctypes.c_void_p(out32_pad.data_ptr()),
            ctypes.c_void_p(buf.data_ptr()),
            numel_padded,  # must match what we used during compress
            cmp_size,
            self.eb, data_type=0, mode=0
        )
        torch.cuda.synchronize()

        out32 = out32_pad[:numel_orig]  # drop padding
        return out32.view(meta["shape"]).to(meta["dtype"])


class KVStore:
    def __init__(self, n_layers):
        self.K = [None] * n_layers
        self.V = [None] * n_layers

    def put(self, i, k, v, codec: CuSZpKVCodec):
        kb, ks, km = codec.compress_tensor(k)
        vb, vs, vm = codec.compress_tensor(v)
        self.K[i] = (kb, ks, km)
        self.V[i] = (vb, vs, vm)

    def get_past(self, codec: CuSZpKVCodec, device):
        past = []
        for (kb, ks, km), (vb, vs, vm) in zip(self.K, self.V):
            k = codec.decompress_tensor(kb, ks, km, device)
            v = codec.decompress_tensor(vb, vs, vm, device)
            past.append((k, v))
        return tuple(past)

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = "distilgpt2"  # you can switch to "facebook/opt-125m" etc.

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device).eval()
    # (optional) cast to fp16 after moving to device:
    model = model.to(dtype=torch.float32).eval()
    print("yes")

    #codec = CuSZpKVCodec(mode="fixed_ratio", ratio=4.0, sample_rate=500)
    codec = CuSZpKVCodec(mode="error_bound", eb=1e-3)

    prompt = "The quick brown fox"
    x = tok(prompt, return_tensors="pt").to(device)

    with torch.inference_mode():
        out = model(**x, use_cache=True)
        logits = out.logits[:, -1, :]
        past = out.past_key_values
        n_layers = len(past)
        store = KVStore(n_layers)

        # compress initial cache
        for i, (k, v) in enumerate(past):
            store.put(i, k, v, codec)

        max_new_tokens = 64
        gen_ids = [torch.argmax(logits, dim=-1)]
        total_raw = 0
        total_cmp = 0

        for _ in range(max_new_tokens - 1):
            # 1) decompress past
            past_dec = store.get_past(codec, device)
            # 2) one-step forward
            nxt = {"input_ids": gen_ids[-1].unsqueeze(0)}
            out = model(**nxt, use_cache=True, past_key_values=past_dec)
            next_id = torch.argmax(out.logits[:, -1, :], dim=-1)
            gen_ids.append(next_id)
            # 3) recompress new cache; track sizes
            for i, (k, v) in enumerate(out.past_key_values):
                total_raw += (k.numel() + v.numel()) * 2  # fp16 bytes approx
                store.put(i, k, v, codec)
                (kb, ks, _), (vb, vs, _) = store.K[i], store.V[i]
                total_cmp += ks + vs

        ids = torch.cat(gen_ids, dim=-1)[0]
        text = tok.decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        print("\n=== Generated ===\n", text)
        if total_cmp > 0:
            print(f"[KV] raw ~ {total_raw/1e6:.1f} MB, compressed ~ {total_cmp/1e6:.1f} MB, ratio ~ {total_raw/total_cmp:.2f}x")

if __name__ == "__main__":
    main()
