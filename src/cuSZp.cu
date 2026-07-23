#include "cuSZp.h"
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cmath>
#include <cstring> 

// Wrap-up API for cuSZp compression.
void cuSZp_compress(void* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float errorBound, cuszp_type_t type, cuszp_mode_t mode, cudaStream_t stream)
{
    if (type == CUSZP_TYPE_FLOAT) {
        if (mode == CUSZP_MODE_PLAIN) {
            cuSZp_compress_1D_plain_f32((float*)d_oriData, d_cmpBytes, nbEle, cmpSize, errorBound, stream);
        } 
        else if (mode == CUSZP_MODE_OUTLIER) {
            cuSZp_compress_1D_outlier_f32((float*)d_oriData, d_cmpBytes, nbEle, cmpSize, errorBound, stream);
        }
        else {
            printf("Unsupported mode in cuSZp.\n");
        }
    } 
    else if (type == CUSZP_TYPE_DOUBLE) {
        double errorBound_f64 = (double)errorBound;
        if (mode == CUSZP_MODE_PLAIN) {
            cuSZp_compress_1D_plain_f64((double*)d_oriData, d_cmpBytes, nbEle, cmpSize, errorBound_f64, stream);
        } 
        else if (mode == CUSZP_MODE_OUTLIER) {
            cuSZp_compress_1D_outlier_f64((double*)d_oriData, d_cmpBytes, nbEle, cmpSize, errorBound_f64, stream);
        }
        else{
            printf("Unsupported mode in cuSZp.\n");
        }
    }
    else {
        printf("Unsupported type in cuSZp.\n");
    }
}

// Wrap-up API for cuSZp decompression.
void cuSZp_decompress(void* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float errorBound, cuszp_type_t type, cuszp_mode_t mode, cudaStream_t stream)
{
    if (type == CUSZP_TYPE_FLOAT) {
        if (mode == CUSZP_MODE_PLAIN) {
            cuSZp_decompress_1D_plain_f32((float*)d_decData, d_cmpBytes, nbEle, cmpSize, errorBound, stream);
        } 
        else if (mode == CUSZP_MODE_OUTLIER) {
            cuSZp_decompress_1D_outlier_f32((float*)d_decData, d_cmpBytes, nbEle, cmpSize, errorBound, stream);
        }
        else {
            printf("Unsupported mode in cuSZp.\n");
        }
    } 
    else if (type == CUSZP_TYPE_DOUBLE) {
        double errorBound_f64 = (double)errorBound;
        if (mode == CUSZP_MODE_PLAIN) {
            cuSZp_decompress_1D_plain_f64((double*)d_decData, d_cmpBytes, nbEle, cmpSize, errorBound_f64, stream);
        } 
        else if (mode == CUSZP_MODE_OUTLIER) {
            cuSZp_decompress_1D_outlier_f64((double*)d_decData, d_cmpBytes, nbEle, cmpSize, errorBound_f64, stream);
        }
        else {
            printf("Unsupported mode in cuSZp.\n");
        }
    }
    else {
        printf("Unsupported type in cuSZp.\n");
    }
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

static const float PRO_128_REL_EB[128] =
{
    // 1e-1 to 5e-2 range
    1e-1f, 9.7e-2f, 9.4e-2f, 9.1e-2f, 8.8e-2f, 8.5e-2f, 8.2e-2f, 7.9e-2f,
    7.6e-2f, 7.3e-2f, 7.0e-2f, 6.7e-2f, 6.4e-2f, 6.1e-2f, 5.8e-2f, 5.5e-2f,

    // 5e-2 to 1e-2 range
    5.2e-2f, 4.9e-2f, 4.6e-2f, 4.3e-2f, 4.0e-2f, 3.7e-2f, 3.4e-2f, 3.1e-2f,
    2.8e-2f, 2.5e-2f, 2.2e-2f, 1.9e-2f, 1.6e-2f, 1.3e-2f, 1.1e-2f, 1e-2f,

    // 1e-2 to 5e-3 range
    9.7e-3f, 9.4e-3f, 9.1e-3f, 8.8e-3f, 8.5e-3f, 8.2e-3f, 7.9e-3f, 7.6e-3f,
    7.3e-3f, 7.0e-3f, 6.7e-3f, 6.4e-3f, 6.1e-3f, 5.8e-3f, 5.5e-3f, 5.2e-3f,

    // 5e-3 to 1e-3 range
    4.9e-3f, 4.6e-3f, 4.3e-3f, 4.0e-3f, 3.7e-3f, 3.4e-3f, 3.1e-3f, 2.8e-3f,
    2.5e-3f, 2.2e-3f, 1.9e-3f, 1.6e-3f, 1.3e-3f, 1.1e-3f, 1.05e-3f, 1e-3f,

    // 1e-3 to 5e-4 range
    9.7e-4f, 9.4e-4f, 9.1e-4f, 8.8e-4f, 8.5e-4f, 8.2e-4f, 7.9e-4f, 7.6e-4f,
    7.3e-4f, 7.0e-4f, 6.7e-4f, 6.4e-4f, 6.1e-4f, 5.8e-4f, 5.5e-4f, 5.2e-4f,

    // 5e-4 to 1e-4 range
    4.9e-4f, 4.6e-4f, 4.3e-4f, 4.0e-4f, 3.7e-4f, 3.4e-4f, 3.1e-4f, 2.8e-4f,
    2.5e-4f, 2.2e-4f, 1.9e-4f, 1.6e-4f, 1.3e-4f, 1.1e-4f, 1.05e-4f, 1e-4f,

    // 1e-4 to 1e-6 range
    9.7e-5f, 9.4e-5f, 9.1e-5f, 8.8e-5f, 8.5e-5f, 8.2e-5f, 7.9e-5f, 7.6e-5f,
    7.3e-5f, 7.0e-5f, 6.7e-5f, 6.4e-5f, 6.1e-5f, 5.8e-5f, 5.5e-5f, 5.2e-5f,
    5.0e-5f, 4.5e-5f, 4.0e-5f, 3.5e-5f, 3.0e-5f, 2.5e-5f, 2.0e-5f, 1.5e-5f,
    1.0e-5f, 9.0e-6f, 8.0e-6f, 5.0e-6f, 4.0e-6f, 3.0e-6f, 2.00e-6f, 1e-6f
};

static inline int pick_best_eb_from_finalrow(const uint4* final_row,
                                             int sample_per_eb,
                                             double R_target)
{
    const size_t orig_per_block = 32 * sizeof(float);            
    const double total_orig     = (double)orig_per_block * (double)sample_per_eb;

    int bytes_per_eb[128];
    for (int lane = 0; lane < 32; ++lane) {
        const uint4 q = final_row[lane];
        const int base = lane * 4;
        bytes_per_eb[base + 0] = (int)q.x;
        bytes_per_eb[base + 1] = (int)q.y;
        bytes_per_eb[base + 2] = (int)q.z;
        bytes_per_eb[base + 3] = (int)q.w;
    }

    int best = 127;
    for (int i = 127; i >= 0; --i) {
        const int b = bytes_per_eb[i];
        if (b <= 0) {              
            best = i; break;
        }
        const double ratio = total_orig / (double)b;
        if (ratio >= R_target) {   
            best = i; 
            if(best > 0) best--;
            break;
        }
    }
    return best;
}


void cuSZp_profile(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float range, int sample_rate, cudaStream_t stream)
{
    cuSZp_profile_1D_plain_f32((float*)d_oriData, d_cmpBytes, nbEle, cmpSize, range, sample_rate, stream);
}


// 1D Fixed Ratio
// 1D Fixed Ratio
float cuSZp_fixed_ratio(
    float* d_oriData,
    unsigned char* d_cmpBytes,
    size_t nbEle,
    size_t* cmpSize,
    float range,
    int sample_rate,
    float ratio,
    cuszp_mode_t mode,
    cudaStream_t stream)
{
    size_t profBytes = 0;
    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_profile_1D_plain_f32(d_oriData, d_cmpBytes, nbEle, &profBytes, range, sample_rate, stream);
    } else {
        cuSZp_profile_1D_outlier_f32(d_oriData, d_cmpBytes, nbEle, &profBytes, range, sample_rate, stream);
    }

    const size_t needBytes = 32 * sizeof(uint4);
    uint4 h_final_row[32]{};
    const size_t copyBytes = std::min(needBytes, profBytes);
    if (copyBytes > 0) {
        cudaMemcpyAsync(h_final_row, d_cmpBytes, copyBytes,
                        cudaMemcpyDeviceToHost, stream);
    }
    cudaStreamSynchronize(stream);

    const int total_blocks = static_cast<int>((nbEle + 31) / 32);
    if (sample_rate <= 0) sample_rate = 1;
    int sample_per_eb = total_blocks / sample_rate;
    if (sample_per_eb < 1) sample_per_eb = 1;

    if (sample_per_eb <= 0) { *cmpSize = 0; return std::nanf(""); }

    const int   best_idx = pick_best_eb_from_finalrow(h_final_row, sample_per_eb, (double)ratio);
    const float relEB    = PRO_128_REL_EB[best_idx];
    const float absEB    = relEB * range;

    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_compress_1D_plain_f32(d_oriData, d_cmpBytes, nbEle, cmpSize, absEB, stream);
    } else {
        cuSZp_compress_1D_outlier_f32(d_oriData, d_cmpBytes, nbEle, cmpSize, absEB, stream);
    }
    return absEB;
}

static inline int pick_best_eb_from_finalrow_64(const uint4* final_row,
                                             int sample_per_eb,
                                             double R_target)
{
    const size_t orig_per_block = 64 * sizeof(float);            
    const double total_orig     = (double)orig_per_block * (double)sample_per_eb;

    int bytes_per_eb[128];
    for (int lane = 0; lane < 32; ++lane) {
        const uint4 q = final_row[lane];
        const int base = lane * 4;
        bytes_per_eb[base + 0] = (int)q.x;
        bytes_per_eb[base + 1] = (int)q.y;
        bytes_per_eb[base + 2] = (int)q.z;
        bytes_per_eb[base + 3] = (int)q.w;
    }

    int best = 127;
    for (int i = 127; i >= 0; --i) {
        const int b = bytes_per_eb[i];
        if (b <= 0) {              
            best = i; break;
        }
        const double ratio = total_orig / (double)b;
        if (ratio >= R_target) {   
            best = i; 
            if(best > 0) best--;
            break;
        }
    }
    return best;
}

float cuSZp_fixed_ratio_2D(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, uint3 dims, float range, int sample_rate, float ratio, cuszp_mode_t mode, cudaStream_t stream)
{
    size_t profBytes = 0;
    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_profile_2D_plain_f32(d_oriData, d_cmpBytes, nbEle, &profBytes, dims, range, sample_rate, stream);
    } else {
        cuSZp_profile_2D_outlier_f32(d_oriData, d_cmpBytes, nbEle, &profBytes, dims, range, sample_rate, stream);
    }

    const size_t needBytes = 32 * sizeof(uint4);
    uint4 h_final_row[32]{};
    const size_t copyBytes = std::min(needBytes, profBytes);
    if (copyBytes > 0) {
        cudaMemcpyAsync(h_final_row, d_cmpBytes, copyBytes, cudaMemcpyDeviceToHost, stream);
    }
    cudaStreamSynchronize(stream);

    uint dimyBlock = (dims.y + 7) / 8;
    uint dimxBlock = (dims.x + 7) / 8;
    uint blockNum = dims.z * dimyBlock * dimxBlock; 
    
    if(blockNum == 0) blockNum = 1;
    const int total_blocks = blockNum;

    if (sample_rate <= 0) sample_rate = 1;
    int sample_per_eb = total_blocks / sample_rate;
    if (sample_per_eb < 1) sample_per_eb = 1;

    if (sample_per_eb <= 0) { *cmpSize = 0; return std::nanf(""); }

    const int   best_idx = pick_best_eb_from_finalrow_64(h_final_row, sample_per_eb, (double)ratio);
    const float relEB    = PRO_128_REL_EB[best_idx];
    const float absEB    = relEB * range;

    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_compress_2D_plain_f32(d_oriData, d_cmpBytes, nbEle, cmpSize, dims, absEB, stream);
    } else {
        cuSZp_compress_2D_outlier_f32(d_oriData, d_cmpBytes, nbEle, cmpSize, dims, absEB, stream);
    }
    return absEB;
}

float cuSZp_fixed_ratio_3D(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, uint3 dims, float range, int sample_rate, float ratio, cuszp_mode_t mode, cudaStream_t stream)
{
    size_t profBytes = 0;
    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_profile_3D_plain_f32(d_oriData, d_cmpBytes, nbEle, &profBytes, dims, range, sample_rate, stream);
    } else {
        cuSZp_profile_3D_outlier_f32(d_oriData, d_cmpBytes, nbEle, &profBytes, dims, range, sample_rate, stream);
    }

    const size_t needBytes = 32 * sizeof(uint4);
    uint4 h_final_row[32]{};
    const size_t copyBytes = std::min(needBytes, profBytes);
    if (copyBytes > 0) {
        cudaMemcpyAsync(h_final_row, d_cmpBytes, copyBytes, cudaMemcpyDeviceToHost, stream);
    }
    cudaStreamSynchronize(stream);

    uint dimzBlock = (dims.z + 3) / 4;
    uint dimyBlock = (dims.y + 3) / 4;
    uint dimxBlock = (dims.x + 3) / 4;
    uint blockNum = dimzBlock * dimyBlock * dimxBlock;
    
    if(blockNum == 0) blockNum = 1;
    const int total_blocks = blockNum;

    if (sample_rate <= 0) sample_rate = 1;
    int sample_per_eb = total_blocks / sample_rate;
    if (sample_per_eb < 1) sample_per_eb = 1;

    if (sample_per_eb <= 0) { *cmpSize = 0; return std::nanf(""); }

    const int   best_idx = pick_best_eb_from_finalrow_64(h_final_row, sample_per_eb, (double)ratio);
    const float relEB    = PRO_128_REL_EB[best_idx];
    const float absEB    = relEB * range;

    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_compress_3D_plain_f32(d_oriData, d_cmpBytes, nbEle, cmpSize, dims, absEB, stream);
    } else {
        cuSZp_compress_3D_outlier_f32(d_oriData, d_cmpBytes, nbEle, cmpSize, dims, absEB, stream);
    }
    return absEB;
}