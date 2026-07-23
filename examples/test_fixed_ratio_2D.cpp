// test_fixed_ratio_2D.cpp
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <cuda_runtime.h>
#include "cuSZp.h"

int main() {
    uint3 dims = make_uint3(8192, 8192, 1); // 1M elements (1024*1024)
    size_t nbEle = dims.x * dims.y * dims.z;
    size_t size_bytes = nbEle * sizeof(float);
    
    // Create dummy data: diagonal gradient
    std::vector<float> h_in(nbEle);
    float min_val = 0.0f;
    float max_val = 0.0f;
    for(size_t i=0; i<nbEle; ++i) {
        int y = i / dims.x;
        int x = i % dims.x;
        h_in[i] = (float)(x + y) * 0.01f;
        if (i==0) { min_val = max_val = h_in[i]; }
        else {
            if (h_in[i] < min_val) min_val = h_in[i];
            if (h_in[i] > max_val) max_val = h_in[i];
        }
    }
    float range = max_val - min_val;
    if (range <= 0) range = 1.0f;

    float* d_in = nullptr;
    unsigned char* d_cmp = nullptr;
    size_t cmpSize = 0;
    
    cudaMalloc(&d_in, size_bytes);
    cudaMalloc(&d_cmp, size_bytes * 2); // safety buffer
    
    cudaMemcpy(d_in, h_in.data(), size_bytes, cudaMemcpyHostToDevice);
    
    // Test 1: Ratio 4.0
    float targetRatio = 8.0f;
    printf("Testing cuSZp_fixed_ratio_2D with target ratio = %.2f...\n", targetRatio);
    
    float absEB = cuSZp_fixed_ratio_2D(d_in, d_cmp, nbEle, &cmpSize, dims, range, 500, targetRatio);
    
    double actualRatio = (double)size_bytes / (double)cmpSize;
    printf("Target Ratio: %.2f\n", targetRatio);
    printf("Actual Ratio: %.2f (Size: %zu -> %zu)\n", actualRatio, size_bytes, cmpSize);
    printf("Resulting AbsEB: %.6e\n", absEB);
    
    // 53.. old logging
    if (actualRatio >= targetRatio * 0.95) { // Allow some slack
        printf("[PASS] Ratio is acceptable.\n");
    } else {
        printf("[WARN] Ratio is lower than target.\n");
    }

    // --- Correctness Check 1: Decompression Error ---
    float* d_dec = nullptr;
    cudaMalloc(&d_dec, size_bytes);
    
    // Decompress (Correct signature: d_decData, d_cmpBytes, nbEle, cmpSize, dims, errorBound, stream)
    cuSZp_decompress_2D_plain_f32(d_dec, d_cmp, nbEle, cmpSize, dims, absEB);
    
    std::vector<float> h_dec(nbEle);
    cudaMemcpy(h_dec.data(), d_dec, size_bytes, cudaMemcpyDeviceToHost);
    
    float max_err = 0.0f;
    for(size_t i=0; i<nbEle; ++i) {
        float err = std::abs(h_in[i] - h_dec[i]);
        if(err > max_err) max_err = err;
    }
    printf("Max Error: %.6e (Bound: %.6e)\n", max_err, absEB);
    
    if (max_err <= absEB * 1.00001f) {
        printf("[PASS] Error bound respected.\n");
    } else {
        printf("[FAIL] Max error exceeds bound!\n");
    }

    // --- Correctness Check 2: Cross-check with Standard cuSZp ---
    unsigned char* d_cmp_std = nullptr;
    size_t cmpSize_std = 0;
    cudaMalloc(&d_cmp_std, size_bytes * 2);
    
    // Use standard compress for 2D
    // Signature: (d_oriData, d_cmpBytes, nbEle, cmpSize*, dims, errorBound, stream)
    cuSZp_compress_2D_plain_f32(d_in, d_cmp_std, nbEle, &cmpSize_std, dims, absEB);
    
    printf("Standard cuSZp Size (with AbsEB=%.6e): %zu bytes\n", absEB, cmpSize_std);
    printf("Fixed-Ratio Size: %zu bytes\n", cmpSize);
    
    double size_diff_pct = 100.0 * std::abs((double)cmpSize - (double)cmpSize_std) / (double)cmpSize_std;
    printf("Size Difference: %.2f%%\n", size_diff_pct);
    
    if (size_diff_pct < 5.0) {
        printf("[PASS] Fixed-Ratio matches standard cuSZp behavior.\n");
    } else {
        printf("[WARN] Significant size difference.\n");
    }

    // ... Plain checks done ...

    // --- Test 2: Outlier Mode ---
    printf("\nTesting cuSZp_fixed_ratio_2D OUTLIER Mode with target ratio = %.2f...\n", targetRatio);
    size_t cmpSize_outlier = 0;
    
    float absEB_outlier = cuSZp_fixed_ratio_2D(d_in, d_cmp, nbEle, &cmpSize_outlier, dims, range, 500, targetRatio, CUSZP_MODE_OUTLIER);
    
    double actualRatio_outlier = (double)size_bytes / (double)cmpSize_outlier;
    printf("Target Ratio: %.2f\n", targetRatio);
    printf("Actual Ratio: %.2f (Size: %zu -> %zu)\n", actualRatio_outlier, size_bytes, cmpSize_outlier);
    printf("Resulting AbsEB: %.6e\n", absEB_outlier);

    // Decompression Check (Outlier)
    // cuSZp_decompress_2D_outlier_f32(d_decData, d_cmpBytes, nbEle, cmpSize, dims, errorBound, stream)
    cuSZp_decompress_2D_outlier_f32(d_dec, d_cmp, nbEle, cmpSize_outlier, dims, absEB_outlier);
    
    cudaMemcpy(h_dec.data(), d_dec, size_bytes, cudaMemcpyDeviceToHost);
    max_err = 0.0f;
    for(size_t i=0; i<nbEle; ++i) {
        float err = std::abs(h_in[i] - h_dec[i]);
        if(err > max_err) max_err = err;
    }
    printf("Max Error (Outlier): %.6e (Bound: %.6e)\n", max_err, absEB_outlier);
    if (max_err <= absEB_outlier * 1.1000f) {
        printf("[PASS] Outlier mode error bound respected.\n");
    } else {
        printf("[FAIL] Outlier mode max error exceeds bound!\n");
    }

    // Cross-check with Standard Outlier Compression
    size_t cmpSize_std_outlier = 0;
    // cuSZp_compress_2D_outlier_f32(d_oriData, d_cmpBytes, nbEle, cmpSize, dims, errorBound, stream)
    cuSZp_compress_2D_outlier_f32(d_in, d_cmp_std, nbEle, &cmpSize_std_outlier, dims, absEB_outlier);
    
    printf("Standard cuSZp Outlier Size: %zu\n", cmpSize_std_outlier);
    double size_diff_pct_outlier = 100.0 * std::abs((double)cmpSize_outlier - (double)cmpSize_std_outlier) / (double)cmpSize_std_outlier;
    printf("Size Difference: %.2f%%\n", size_diff_pct_outlier);
    
    if (size_diff_pct_outlier < 5.0) {
        printf("[PASS] Fixed-Ratio Outlier matches standard behavior.\n");
    } else {
        printf("[WARN] Significant size difference in outlier mode.\n");
    }

    cudaFree(d_dec);
    cudaFree(d_cmp_std);
    
    // Cleanup
    cudaFree(d_in);
    cudaFree(d_cmp);
    
    return 0;
}
