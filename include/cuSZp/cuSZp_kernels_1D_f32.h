#ifndef CUSZP_INCLUDE_CUSZP_CUSZP_KERNELS_1D_F32_H
#define CUSZP_INCLUDE_CUSZP_CUSZP_KERNELS_1D_F32_H

static const int tblock_size = 32; // Fixed to 32, cannot be modified.
static const int thread_chunk = 1024;
static const int sample_ratio = 100; //

__global__ void cuSZp_compress_kernel_1D_outlier_f32(const float* const __restrict__ oriData, unsigned char* const __restrict__ cmpData, volatile unsigned int* const __restrict__ cmpOffset, volatile unsigned int* const __restrict__ locOffset, volatile int* const __restrict__ flag, const float eb, const size_t nbEle);
__global__ void cuSZp_decompress_kernel_1D_outlier_f32(float* const __restrict__ decData, const unsigned char* const __restrict__ cmpData, volatile unsigned int* const __restrict__ cmpOffset, volatile unsigned int* const __restrict__ locOffset, volatile int* const __restrict__ flag, const float eb, const size_t nbEle);
__global__ void cuSZp_compress_kernel_1D_plain_f32(const float* const __restrict__ oriData, unsigned char* const __restrict__ cmpData, volatile unsigned int* const __restrict__ cmpOffset, volatile unsigned int* const __restrict__ locOffset, volatile int* const __restrict__ flag, const float eb, const size_t nbEle);
__global__ void cuSZp_decompress_kernel_1D_plain_f32(float* const __restrict__ decData, const unsigned char* const __restrict__ cmpData, volatile unsigned int* const __restrict__ cmpOffset, volatile unsigned int* const __restrict__ locOffset, volatile int* const __restrict__ flag, const float eb, const size_t nbEle);
__global__ void cuSZp_Profiling_kernel_1D_f32(const float* const __restrict__ oriData, unsigned char* const __restrict__ cmpData, volatile unsigned int* const __restrict__ cmpOffset, volatile unsigned int* const __restrict__ locOffset, volatile int* const __restrict__ flag,  const size_t nbEle, const int sd, float range);
__global__ void cuSZp_Profiling_kernel_iter_1D_f32(const float* const __restrict__ oriData, unsigned char* const __restrict__ cmpData, volatile uint4* const __restrict__ cmpOffset, volatile uint4* const __restrict__ locOffset, volatile int* const __restrict__ flag,  const size_t nbEle, const int sd, float range);
__global__ void cuSZp_Profiling_kernel_iter_1D_outlier_f32(const float* const __restrict__ oriData, unsigned char* const __restrict__ cmpData, volatile uint4* const __restrict__ cmpOffset, volatile uint4* const __restrict__ locOffset, volatile int* const __restrict__ flag,  const size_t nbEle, const int sd, float range);
#endif // CUSZP_INCLUDE_CUSZP_CUSZP_KERNELS_1D_F32_H