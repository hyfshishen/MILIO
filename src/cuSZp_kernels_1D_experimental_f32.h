
#ifndef _CUSZP_KERNELS_1D_EXPERIMENTAL_H
#define _CUSZP_KERNELS_1D_EXPERIMENTAL_H

#include <cuda_runtime.h>

__global__ void cuSZp_compress_kernel_1D_wht_f32(
    const float* __restrict__ data,
    unsigned char* __restrict__ output,
    size_t num_elements,
    size_t target_bytes_per_block);

__global__ void cuSZp_compress_kernel_1D_poly_f32(
    const float* __restrict__ data,
    unsigned char* __restrict__ output,
    size_t num_elements,
    size_t target_bytes_per_block);

__global__ void cuSZp_decompress_kernel_1D_wht_f32(
    float* __restrict__ output,
    const unsigned char* __restrict__ input,
    size_t num_elements,
    size_t target_bytes_per_block);

__global__ void cuSZp_decompress_kernel_1D_poly_f32(
    float* __restrict__ output,
    const unsigned char* __restrict__ input,
    size_t num_elements,
    size_t target_bytes_per_block);

#endif
