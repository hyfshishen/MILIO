
#include "cuSZp_kernels_1D_experimental_f32.h"
#include <cstdio>

// Fast Walsh-Hadamard Transform (WHT) using Warp Shuffle
// Input: 32 floats in registers.
// Output: 32 transformed coefficients in registers.
// Note: This is an unnormalized transform.
__device__ inline void fast_wht_32(float& d, int lane)
{
    float temp;
    
    // Stage 1 (Butterfly stride 1)
    temp = __shfl_xor_sync(0xffffffff, d, 1);
    d = (lane & 1) ? (temp - d) : (d + temp);

    // Stage 2 (Butterfly stride 2)
    temp = __shfl_xor_sync(0xffffffff, d, 2);
    d = (lane & 2) ? (temp - d) : (d + temp);

    // Stage 3 (Butterfly stride 4)
    temp = __shfl_xor_sync(0xffffffff, d, 4);
    d = (lane & 4) ? (temp - d) : (d + temp);

    // Stage 4 (Butterfly stride 8)
    temp = __shfl_xor_sync(0xffffffff, d, 8);
    d = (lane & 8) ? (temp - d) : (d + temp);

    // Stage 5 (Butterfly stride 16)
    temp = __shfl_xor_sync(0xffffffff, d, 16);
    d = (lane & 16) ? (temp - d) : (d + temp);
}

// Simple Linear Regression: y = ax + b
// Returns {a, b}
__device__ inline float2 simple_linear_regression_32(float y, int lane)
{
    float sum_x = 496.0f; // 0+1+...+31
    float sum_x2 = 10416.0f; // 0^2 + ... + 31^2
    float n = 32.0f;

    float sum_y = y;
    float sum_xy = y * (float)lane;

    // Warp Reduce Sum
    for (int offset = 16; offset > 0; offset /= 2) {
        sum_y += __shfl_down_sync(0xffffffff, sum_y, offset);
        sum_xy += __shfl_down_sync(0xffffffff, sum_xy, offset);
    }
    
    // Thread 0 computes coefficients
    float a = 0.0f, b = 0.0f;
    if (lane == 0) {
        float denominator = n * sum_x2 - sum_x * sum_x;
        if (abs(denominator) > 1e-6f) {
            a = (n * sum_xy - sum_x * sum_y) / denominator;
            b = (sum_y - a * sum_x) / n;
        } else {
            // Degenerate case (shouldn't happen with fixed x=0..31)
            b = sum_y / n; 
        }
    }
    
    // Broadcast a and b
    a = __shfl_sync(0xffffffff, a, 0);
    b = __shfl_sync(0xffffffff, b, 0);
    return make_float2(a, b);
}


__global__ void cuSZp_compress_kernel_1D_wht_f32(
    const float* __restrict__ data,
    unsigned char* __restrict__ output,
    size_t num_elements,
    size_t target_bytes_per_block)
{
    int tid = threadIdx.x;
    int bid = blockIdx.x;
    int gid = bid * blockDim.x + tid;
    int lane = tid % 32;
    int warp_id = gid / 32;
    // Thread Coarsening: Each warp processes 32 blocks
    const int BLOCKS_PER_WARP = 32; 

    // Global Block Index Base for this warp
    size_t base_block_idx = (size_t)warp_id * BLOCKS_PER_WARP;

    for (int i = 0; i < BLOCKS_PER_WARP; ++i) {
        size_t block_idx = base_block_idx + i;
        size_t data_idx = block_idx * 32 + lane; // Distributed loading

        if (data_idx >= num_elements) break;

        // 1. Load Data
        float val = data[data_idx];
        
        // 2. Transform (WHT)
        fast_wht_32(val, lane);
        
        // 3. Quantize & Store
        int K = target_bytes_per_block;
        if (K > 32) K = 32;

        float scale = 1.0f; 
        int q = (int)(val * scale);
        if (q > 127) q = 127;
        if (q < -128) q = -128;
        unsigned char out_byte = (unsigned char)(q + 128);

        unsigned char* block_out_ptr = output + block_idx * target_bytes_per_block;
        if (lane < K) {
            block_out_ptr[lane] = out_byte;
        }
    }
}

__global__ void cuSZp_compress_kernel_1D_poly_f32(
    const float* __restrict__ data,
    unsigned char* __restrict__ output,
    size_t num_elements,
    size_t target_bytes_per_block)
{
    int tid = threadIdx.x;
    int bid = blockIdx.x;
    int gid = bid * blockDim.x + tid;
    int lane = tid % 32;
    int warp_id = gid / 32;
    
    const int BLOCKS_PER_WARP = 32; 
    size_t base_block_idx = (size_t)warp_id * BLOCKS_PER_WARP;

    for (int i = 0; i < BLOCKS_PER_WARP; ++i) {
        size_t block_idx = base_block_idx + i;
        size_t data_idx = block_idx * 32 + lane;

        if (data_idx >= num_elements) break;

        // 1. Load Data
        float val = data[data_idx];

        // 2. Linear Regression
        float2 coeffs = simple_linear_regression_32(val, lane);
        float a = coeffs.x;
        float b = coeffs.y;

        // 3. Compute Residual
        float pred = a * (float)lane + b;
        float res = val - pred;

        // 4. Pack
        unsigned char* block_out_ptr = output + block_idx * target_bytes_per_block;
        
        if (target_bytes_per_block >= 8) {
            if (lane == 0) *(float*)(block_out_ptr) = a;
            if (lane == 1) *(float*)(block_out_ptr + 4) = b;
            
            int res_bytes = target_bytes_per_block - 8;
            if (res_bytes > 0 && lane < res_bytes) {
                int q = (int)(res * 10.0f);
                if (q > 127) q = 127;
                if (q < -128) q = -128;
                block_out_ptr[8 + lane] = (unsigned char)(q + 128);
            }
        }
    }
}

// -----------------------------------------------------------------------------
// Decompression Kernels
// -----------------------------------------------------------------------------

__global__ void cuSZp_decompress_kernel_1D_wht_f32(
    float* __restrict__ output,
    const unsigned char* __restrict__ input,
    size_t num_elements,
    size_t target_bytes_per_block)
{
    int tid = threadIdx.x;
    int bid = blockIdx.x;
    int gid = bid * blockDim.x + tid;
    int lane = tid % 32;
    int warp_id = gid / 32;
    const int BLOCKS_PER_WARP = 32;

    size_t base_block_idx = (size_t)warp_id * BLOCKS_PER_WARP;

    for (int i = 0; i < BLOCKS_PER_WARP; ++i) {
        size_t block_idx = base_block_idx + i;
        size_t data_idx = block_idx * 32 + lane;
        
        if (data_idx >= num_elements) break;

        // 1. Read & Dequantize Coeffs
        int K = target_bytes_per_block;
        if (K > 32) K = 32;
        
        const unsigned char* block_in_ptr = input + block_idx * target_bytes_per_block;
        
        float val = 0.0f;
        if (lane < K) {
             unsigned char in_byte = block_in_ptr[lane];
             int q = (int)in_byte - 128;
             float scale = 1.0f; // Must match compression
             val = (float)q / scale;
        }

        // 2. Inverse Transform (WHT)
        // WHT is symmetric (inv = fwd). But we need to normalize by N=32.
        fast_wht_32(val, lane);
        val /= 32.0f;

        // 3. Store
        output[data_idx] = val; // Direct write (no shuffle needed if fast_wht output is distributed)
    }
}

__global__ void cuSZp_decompress_kernel_1D_poly_f32(
    float* __restrict__ output,
    const unsigned char* __restrict__ input,
    size_t num_elements,
    size_t target_bytes_per_block)
{
    int tid = threadIdx.x;
    int bid = blockIdx.x;
    int gid = bid * blockDim.x + tid;
    int lane = tid % 32;
    int warp_id = gid / 32;
    const int BLOCKS_PER_WARP = 32;

    size_t base_block_idx = (size_t)warp_id * BLOCKS_PER_WARP;

    for (int i = 0; i < BLOCKS_PER_WARP; ++i) {
        size_t block_idx = base_block_idx + i;
        size_t data_idx = block_idx * 32 + lane;
        
        if (data_idx >= num_elements) break;

        // 1. Unpack
        const unsigned char* block_in_ptr = input + block_idx * target_bytes_per_block;
        
        float a = 0.0f, b = 0.0f;
        if (target_bytes_per_block >= 8) {
            a = *(float*)(block_in_ptr);
            b = *(float*)(block_in_ptr + 4);
        }
        
        // Broadcast a and b
        a = __shfl_sync(0xffffffff, a, 0); // Assuming stored in byte 0-3 (lane 0?) No
        // Wait, multiple threads might read from global depending on cache line?
        // Actually, easiest is just let all threads read it? 
        // No, redundant reads.
        // Let thread 0 read a, thread 1 read b, then broadcast.
        // Actually, we can just read from global memory directly.
        // But block_in_ptr is char*. Casting to float* might be unaligned?
        // Safe to use memcpy or just assume alignment if target_bytes is multiple of 4?
        // Let's assume standard behavior:
        // Or re-implement broadcasting.
        if (lane == 0) a = *(float*)(block_in_ptr);
        if (lane == 1) b = *(float*)(block_in_ptr + 4);
        a = __shfl_sync(0xffffffff, a, 0);
        b = __shfl_sync(0xffffffff, b, 1);

        float res = 0.0f;
        int res_bytes = target_bytes_per_block - 8;
        if (res_bytes > 0 && lane < res_bytes) {
             unsigned char in_byte = block_in_ptr[8 + lane];
             int q = (int)in_byte - 128;
             res = (float)q / 10.0f; // Fixed scale matching compress
        }

        // 2. Reconstruct
        float pred = a * (float)lane + b;
        float val = pred + res;

        // 3. Store
        output[data_idx] = val;
    }
}
