#include "cuSZp_entry_1D_transformed_f32.h"
#include "cuSZp_kernels_1D_experimental_f32.h"
#include <cstdio>

// WHT Compression tailored to match cuSZp legacy signature style
void cuSZp_compress_1D_transform_wht_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float target_ratio, cudaStream_t stream)
{
    // Optimized launch configuration - Thread Coarsening (32 blocks/warp)
    int bsize = 256; // 8 warps
    // Each warp processes 32 blocks * 32 elems = 1024 elements
    size_t elements_per_warp = 1024;
    int total_warps = (nbEle + elements_per_warp - 1) / elements_per_warp;
    int gsize = (total_warps * 32 + bsize - 1) / bsize; 
    
    size_t target_bytes = (size_t)(32.0f / target_ratio * 4.0f); // 32 floats * 4 bytes / ratio
    if (target_bytes < 4) target_bytes = 4;
    
    // Note: WHT is Fixed-Ratio, so we don't need auxiliary arrays (d_cmpOffset, d_locOffset, d_flag).
    // We can calculate the exact compressed size without prefix-sum or atomicScan.
    // This provides "Zero-Overhead" memory management.

    cuSZp_compress_kernel_1D_wht_f32<<<gsize, bsize, 0, stream>>>(d_oriData, d_cmpBytes, nbEle, target_bytes);
    
    *cmpSize = (nbEle + 31) / 32 * target_bytes;
    
    // Legacy compatibility: synchronize if expected to be blocking (like cudaMemcpy in original)
    // cudaStreamSynchronize(stream); 
}

// Poly Compression tailored to match cuSZp legacy signature style
void cuSZp_compress_1D_transform_poly_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float target_ratio, cudaStream_t stream)
{
    // Optimized launch configuration - Poly
    int bsize = 256;
    size_t elements_per_warp = 1024;
    int total_warps = (nbEle + elements_per_warp - 1) / elements_per_warp;
    int gsize = (total_warps * 32 + bsize - 1) / bsize;
    
    size_t target_bytes = (size_t)(32.0f / target_ratio * 4.0f);
    if (target_bytes < 8) target_bytes = 8; // Poly needs at least 8 bytes
    
    // Note: Poly is Fixed-Ratio, so we don't need auxiliary arrays.
    // Zero-Overhead memory management.
    
    cuSZp_compress_kernel_1D_poly_f32<<<gsize, bsize, 0, stream>>>(d_oriData, d_cmpBytes, nbEle, target_bytes);
    
    *cmpSize = (nbEle + 31) / 32 * target_bytes;
}

void cuSZp_decompress_1D_transform_wht_f32(float* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float target_ratio, cudaStream_t stream)
{
    // Optimized launch configuration - WHT
    int bsize = 256;
    size_t elements_per_warp = 1024;
    int total_warps = (nbEle + elements_per_warp - 1) / elements_per_warp;
    int gsize = (total_warps * 32 + bsize - 1) / bsize;
    
    size_t target_bytes = (size_t)(32.0f / target_ratio * 4.0f);
    if (target_bytes < 4) target_bytes = 4;

    cuSZp_decompress_kernel_1D_wht_f32<<<gsize, bsize, 0, stream>>>(d_decData, d_cmpBytes, nbEle, target_bytes);
}

void cuSZp_decompress_1D_transform_poly_f32(float* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float target_ratio, cudaStream_t stream)
{
    // Optimized launch configuration - Poly
    int bsize = 256;
    size_t elements_per_warp = 1024;
    int total_warps = (nbEle + elements_per_warp - 1) / elements_per_warp;
    int gsize = (total_warps * 32 + bsize - 1) / bsize;
    
    size_t target_bytes = (size_t)(32.0f / target_ratio * 4.0f);
    if (target_bytes < 8) target_bytes = 8;

    cuSZp_decompress_kernel_1D_poly_f32<<<gsize, bsize, 0, stream>>>(d_decData, d_cmpBytes, nbEle, target_bytes);
}
