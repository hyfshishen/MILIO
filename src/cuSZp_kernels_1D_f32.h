#ifndef _CUSZP_KERNELS_1D_F32_H
#define _CUSZP_KERNELS_1D_F32_H

#include <cuda_runtime.h>
#include "cuSZp_entry_1D_f32.h"

#define tblock_size 32
#define thread_chunk 1024

__global__ void cuSZp_Profiling_kernel_iter_1D_f32(const float* const __restrict__ oriData, 
                                                unsigned char* const __restrict__ cmpData, 
                                                volatile uint4* const __restrict__ cmpOffset, 
                                                volatile uint4* const __restrict__ locOffset, 
                                                volatile int* const __restrict__ flag, 
                                                const size_t nbEle, 
                                                const int sd,
                                                const float range
                                                );

__global__ void cuSZp_Profiling_kernel_iter_1D_outlier_f32(const float* const __restrict__ oriData, 
                                                unsigned char* const __restrict__ cmpData, 
                                                volatile uint4* const __restrict__ cmpOffset, 
                                                volatile uint4* const __restrict__ locOffset, 
                                                volatile int* const __restrict__ flag, 
                                                const size_t nbEle, 
                                                const int sd,
                                                const float range
                                                );

__global__ void cuSZp_compress_kernel_1D_plain_f32(const float* const __restrict__ oriData, 
                                            unsigned char* const __restrict__ cmpData, 
                                            volatile unsigned int* const __restrict__ cmpOffset, 
                                            volatile unsigned int* const __restrict__ locOffset, 
                                            volatile int* const __restrict__ flag, 
                                            const float eb, 
                                            const size_t nbEle
                                            );

__global__ void cuSZp_compress_kernel_1D_outlier_f32(const float* const __restrict__ oriData, 
                                            unsigned char* const __restrict__ cmpData, 
                                            volatile unsigned int* const __restrict__ cmpOffset, 
                                            volatile unsigned int* const __restrict__ locOffset, 
                                            volatile int* const __restrict__ flag, 
                                            const float eb, 
                                            const size_t nbEle
                                            );

__global__ void cuSZp_decompress_kernel_1D_plain_f32(
    float* const __restrict__ decData, 
    const unsigned char* const __restrict__ cmpData, 
    volatile unsigned int* const __restrict__ cmpOffset, 
    volatile unsigned int* const __restrict__ locOffset, 
    volatile int* const __restrict__ flag, 
    const float eb, 
    const size_t nbEle
);

__global__ void cuSZp_decompress_kernel_1D_outlier_f32(
    float* const __restrict__ decData, 
    const unsigned char* const __restrict__ cmpData, 
    volatile unsigned int* const __restrict__ cmpOffset, 
    volatile unsigned int* const __restrict__ locOffset, 
    volatile int* const __restrict__ flag, 
    const float eb, 
    const size_t nbEle
);

#endif
