# eb_stress.py
import os, ctypes, torch
from pycuSZp import cuSZp

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"   # make errors surface at the right call

codec = cuSZp()

def compress_eb(x: torch.Tensor, eb=1e-3, headroom=8):
    assert x.is_cuda and x.dtype == torch.float32
    # ensure contiguous
    x = x.contiguous()

    # pad length to multiple of 32 (many warp-wide kernels assume this)
    flat = x.view(-1)
    n = flat.numel()
    pad = (-n) & 31
    if pad:
        flat_p = torch.empty(n + pad, dtype=torch.float32, device=flat.device)
        flat_p[:n] = flat
        flat_p[n:] = 0.0
    else:
        flat_p = flat

    # ensure 16B alignment for float4 loads (PyTorch is typically >=256B aligned, but we check)
    if (flat_p.data_ptr() % 16) != 0:
        flat_p = flat_p.clone()

    orig_bytes = flat_p.numel() * 4
    cap = max(orig_bytes * headroom, orig_bytes + (8 << 20))  # generous headroom
    buf = torch.empty(cap, dtype=torch.uint8, device=flat_p.device)

    # call EB compressor
    cmp_size = codec.compress(
        ctypes.c_void_p(flat_p.data_ptr()),
        ctypes.c_void_p(buf.data_ptr()),
        flat_p.numel(),
        eb, data_type=0, mode=0
    )
    torch.cuda.synchronize()
    assert 0 < cmp_size <= cap, f"bad cmp_size={cmp_size} cap={cap}"
    return buf, cmp_size, n, pad

def roundtrip_eb(x_f32: torch.Tensor, eb=1e-3):
    buf, cmp_size, n, pad = compress_eb(x_f32, eb=eb)
    out = torch.empty(n + pad, dtype=torch.float32, device=x_f32.device)
    codec.decompress(
        ctypes.c_void_p(out.data_ptr()),
        ctypes.c_void_p(buf.data_ptr()),
        out.numel(), cmp_size,
        eb, data_type=0, mode=0
    )
    torch.cuda.synchronize()
    out = out[:n].view_as(x_f32)
    max_err = (x_f32 - out).abs().max().item()
    return max_err, cmp_size

def main():
    torch.cuda.synchronize()
    torch.manual_seed(0)
    device = "cuda"
    # test several sizes resembling KV tiles
    shapes = [
        (12, 1, 1, 64),    # tiny tile
        (12, 16, 64),      # heads × seq × dim
        (1, 12, 128, 64),  # typical GPT-2 small step
        (1, 12, 256, 64),
        (1, 12, 512, 64),
    ]
    for shp in shapes:
        x = torch.rand(shp, dtype=torch.float32, device=device)
        try:
            max_err, csz = roundtrip_eb(x, eb=1e-3)
            print(f"shape={shp} ok; cmp={csz/1e6:.2f} MB; max_err={max_err:.3e}")
        except Exception as e:
            print(f"shape={shp} FAILED -> {e}")
            raise

if __name__ == "__main__":
    main()
