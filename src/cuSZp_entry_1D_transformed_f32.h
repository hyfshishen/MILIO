#ifndef _CUSZP_ENTRY_1D_TRANSFORMED_F32_H
#define _CUSZP_ENTRY_1D_TRANSFORMED_F32_H

#include <cuda_runtime.h>

void cuSZp_compress_1D_transform_wht_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float target_ratio, cudaStream_t stream);
void cuSZp_compress_1D_transform_poly_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float target_ratio, cudaStream_t stream);

void cuSZp_decompress_1D_transform_wht_f32(float* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float target_ratio, cudaStream_t stream);
void cuSZp_decompress_1D_transform_poly_f32(float* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float target_ratio, cudaStream_t stream);

#endif
