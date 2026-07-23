import torch
import pycuda.driver as cuda
import pycuda.autoinit  # init CUDA context once
import ctypes
from pycuSZp import cuSZp  # must include .compress_fixed_ratio as we discussed

def devptr(x):
    # Convert PyCUDA DeviceAllocation to integer pointer for ctypes
    try:
        return ctypes.c_void_p(int(x))
    except TypeError:
        # Some pycuda versions use .ptr
        return ctypes.c_void_p(x.ptr)

def main():
    # --------------------------
    # Parameters
    # --------------------------
    error_bound   = 1e-2
    target_ratio  = 4.0       # fixed-ratio target
    sample_rate   = 500
    tensor_size   = int(1 * 1024**3 / 4)  # 4GB / 4 bytes per float32

    device = torch.device('cuda')
    compressor = cuSZp()

    # --------------------------
    # Generate 4GB tensor
    # --------------------------
    data = torch.rand(tensor_size, dtype=torch.float32, device=device)
    torch.cuda.synchronize()

    original_size = data.numel() * data.element_size()

    # For safety, give compressed buffer a tiny slack (+1MB).
    # You can use original_size if your codec guarantees no expansion.
    cap_bytes = original_size + (1 << 20)

    # Allocate a single compressed buffer we can reuse
    d_cmpBytes = cuda.mem_alloc(cap_bytes)

    # --------------------------
    # 1) Error-bound compression
    # --------------------------
    print("\n=== Error-bound path ===")
    cmp_size = compressor.compress(
        ctypes.c_void_p(data.data_ptr()),   # GPU in
        devptr(d_cmpBytes),                 # GPU out
        data.numel(),
        error_bound,
        data_type=0,   # 0=float32
        mode=0         # 0=plain
    )
    torch.cuda.synchronize()

    print(f"Original data size:   {original_size} bytes")
    print(f"Compressed data size: {cmp_size} bytes")
    print(f"Compression Ratio:    {original_size / cmp_size:.2f}x")

    # Decompress to a fresh tensor
    d_dec = torch.empty_like(data, device=device)
    compressor.decompress(
        ctypes.c_void_p(d_dec.data_ptr()),
        devptr(d_cmpBytes),
        data.numel(),
        cmp_size,
        error_bound,
        data_type=0,
        mode=0
    )
    torch.cuda.synchronize()

    ok = torch.allclose(data, d_dec, atol=error_bound)
    print(f"Decompressed within EB ({error_bound}): {ok}")

    # --------------------------
    # 2) Fixed-ratio compression
    # --------------------------
    print("\n=== Fixed-ratio path ===")
    # Compute range on GPU (scalar sync to host only)
    data_min = torch.min(data).item()
    data_max = torch.max(data).item()
    data_range = float(data_max - data_min)
    if not (data_range > 0.0):
        raise RuntimeError(f"Invalid data range={data_range}; cannot use relative EB.")

    cmp_size_fr = compressor.compress_fixed_ratio(
        ctypes.c_void_p(data.data_ptr()),
        devptr(d_cmpBytes),
        data.numel(),
        data_range,
        sample_rate=sample_rate,
        ratio=target_ratio
    )
    torch.cuda.synchronize()

    print(f"[Fixed-ratio] Target ratio: {target_ratio:.2f}x")
    print(f"[Fixed-ratio] Compressed size: {cmp_size_fr} bytes")
    print(f"[Fixed-ratio] Achieved ratio: {original_size / cmp_size_fr:.2f}x")

    # Decompress (fixed-ratio path used an internally-chosen EB; we don't need it for decode)
    d_dec2 = torch.empty_like(data, device=device)
    # You can pass any EB to the current API if your decoder ignores it,
    # but we'll pass the same EB as in (1) just to satisfy the signature.
    compressor.decompress(
        ctypes.c_void_p(d_dec2.data_ptr()),
        devptr(d_cmpBytes),
        data.numel(),
        cmp_size_fr,
        error_bound,    # not used by fixed-ratio decode; kept for API compatibility
        data_type=0,
        mode=0
    )
    torch.cuda.synchronize()

    # Since we don't know the internally-chosen EB here, check the actual max error
    max_abs_err = (data - d_dec2).abs().max().item()
    print(f"[Fixed-ratio] Max |x - x̂| after decode: {max_abs_err:.3e}")

    # Cleanup
    d_cmpBytes.free()

if __name__ == "__main__":
    main()
