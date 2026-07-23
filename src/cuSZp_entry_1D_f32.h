#ifndef _CUSZP_ENTRY_1D_F32_H
#define _CUSZP_ENTRY_1D_F32_H

#include <cuda_runtime.h>

void cuSZp_profile_1D_plain_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float range, int sample_rate, cudaStream_t stream);
void cuSZp_profile_1D_outlier_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float range, int sample_rate, cudaStream_t stream);

void cuSZp_compress_1D_plain_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float errorBound, cudaStream_t stream);
void cuSZp_compress_1D_outlier_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float errorBound, cudaStream_t stream);

void cuSZp_decompress_1D_plain_f32(float* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float errorBound, cudaStream_t stream);
void cuSZp_decompress_1D_outlier_f32(float* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float errorBound, cudaStream_t stream);

#endif
