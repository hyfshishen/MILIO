// test_fixed_ratio_1D.cpp
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <cuda_runtime.h>
#include "cuSZp.h"

int main() {
    const char* filePath = "/scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vy.f32";
    FILE* fp = fopen(filePath, "rb");
    if(!fp) {
        printf("Error opening file: %s\n", filePath);
        return 1;
    }
    fseek(fp, 0, SEEK_END);
    size_t fileSize = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    
    size_t nbEle = fileSize / sizeof(float);
    size_t size_bytes = fileSize;
    
    printf("Loading %s...\n", filePath);
    printf("Elements: %zu, Size: %zu bytes\n", nbEle, size_bytes);

    std::vector<float> h_in(nbEle);
    size_t readCount = fread(h_in.data(), sizeof(float), nbEle, fp);
    fclose(fp);
    if(readCount != nbEle) {
        printf("Error reading file. Expected %zu, got %zu\n", nbEle, readCount);
        return 1;
    }
    
    float min_val = h_in[0];
    float max_val = h_in[0];
    for(size_t i=0; i<nbEle; ++i) {
        if (h_in[i] < min_val) min_val = h_in[i];
        if (h_in[i] > max_val) max_val = h_in[i];
    }
    float range = max_val - min_val;
    if (range <= 0) range = 1.0f;
    printf("Data Range: [%.6e, %.6e], Range: %.6e\n", min_val, max_val, range);

    float* d_in = nullptr;
    float* d_dec = nullptr;
    unsigned char* d_cmp = nullptr;
    unsigned char* d_cmp_std = nullptr;
    size_t cmpSize = 0;
    
    cudaMalloc(&d_in, size_bytes);
    cudaMalloc(&d_dec, size_bytes);
    cudaMalloc(&d_cmp, size_bytes * 2); // safety buffer
    cudaMalloc(&d_cmp_std, size_bytes * 2);
    
    cudaMemcpy(d_in, h_in.data(), size_bytes, cudaMemcpyHostToDevice);
    
    std::vector<float> testRatios = {4.0f, 6.0f, 8.0f};

    for (float targetRatio : testRatios) {
        printf("\n=======================================================\n");
        printf("Testing cuSZp_fixed_ratio (1D) with target ratio = %.2f\n", targetRatio);
        printf("=======================================================\n");
        
        // --- Test 1: Plain Mode ---
        printf("\n--- Plain Mode ---\n");
        cudaMemset(d_cmp, 0, size_bytes * 2);

        float absEB = cuSZp_fixed_ratio(d_in, d_cmp, nbEle, &cmpSize, range, 500, targetRatio);
        
        double actualRatio = (double)size_bytes / (double)cmpSize;
        printf("Target Ratio: %.2f\n", targetRatio);
        printf("Actual Ratio: %.2f (Size: %zu -> %zu)\n", actualRatio, size_bytes, cmpSize);
        printf("Resulting AbsEB: %.6e\n", absEB);
        
        if (actualRatio >= targetRatio * 0.95) { 
            printf("[PASS] Ratio is acceptable.\n");
        } else {
            printf("[WARN] Ratio is lower than target.\n");
        }

        // --- Correctness Check 1: Decompression Error ---
        cuSZp_decompress_1D_plain_f32(d_dec, d_cmp, nbEle, cmpSize, absEB);
        
        std::vector<float> h_dec(nbEle);
        cudaMemcpy(h_dec.data(), d_dec, size_bytes, cudaMemcpyDeviceToHost);
        
        float max_err = 0.0f;
        for(size_t i=0; i<nbEle; ++i) {
            float err = std::abs(h_in[i] - h_dec[i]);
            if(err > max_err) max_err = err;
        }
        printf("Max Error: %.6e (Bound: %.6e)\n", max_err, absEB);
        
        if (max_err <= absEB * 1.00003f) { 
            printf("[PASS] Error bound respected.\n");
        } else {
            printf("[FAIL] Max error exceeds bound!\n");
        }
        
        // --- Correctness Check 2: Cross-check with Standard cuSZp ---
        size_t cmpSize_std = 0;
        
        // Standard compression
        cuSZp_compress_1D_plain_f32(d_in, d_cmp_std, nbEle, &cmpSize_std, absEB);
        
        printf("Standard cuSZp Size (with AbsEB=%.6e): %zu bytes\n", absEB, cmpSize_std);
        printf("Fixed-Ratio Size: %zu bytes\n", cmpSize);
        
        double size_diff_pct = 100.0 * std::abs((double)cmpSize - (double)cmpSize_std) / (double)cmpSize_std;
        printf("Size Difference: %.2f%%\n", size_diff_pct);
        
        if (size_diff_pct < 5.0) { 
            printf("[PASS] Fixed-Ratio matches standard cuSZp behavior.\n");
        } else {
            printf("[WARN] Significant size difference between fixed-ratio and standard cuSZp.\n");
        }

        // --- Verify Pure Standard Plain Decompression ---
        printf("Verifying Pure Standard cuSZp Plain Decompression...\n");
        float* d_dec_std_plain = nullptr;
        cudaMalloc(&d_dec_std_plain, size_bytes);
        cudaMemset(d_dec_std_plain, 0, size_bytes);
        
        cuSZp_decompress_1D_plain_f32(d_dec_std_plain, d_cmp_std, nbEle, cmpSize_std, absEB);
        
        std::vector<float> h_dec_std_plain(nbEle);
        cudaMemcpy(h_dec_std_plain.data(), d_dec_std_plain, size_bytes, cudaMemcpyDeviceToHost);
        
        float max_err_std_plain = 0.0f;
        float max_diff_fix_std_plain = 0.0f;
        for(size_t i=0; i<nbEle; ++i) {
            float err = std::abs(h_in[i] - h_dec_std_plain[i]);
            if(err > max_err_std_plain) max_err_std_plain = err;

            float diff = std::abs(h_dec[i] - h_dec_std_plain[i]);
            if(diff > max_diff_fix_std_plain) max_diff_fix_std_plain = diff;
        }
        printf("Max Error (Pure Standard Plain): %.6e (Bound: %.6e)\n", max_err_std_plain, absEB);
        if(max_err_std_plain <= absEB * 1.00001f) {
            printf("[PASS] Standard Plain respects error bound.\n");
        } else {
            printf("[FAIL] Standard Plain VIOLATES error bound!\n");
        }
        
        printf("Max Pointwise Diff (Fixed vs Standard Plain): %.6e\n", max_diff_fix_std_plain);
        if(max_diff_fix_std_plain < 1e-9) {
            printf("[PASS] Fixed-Ratio Plain matches Standard Plain pointwise.\n");
        } else {
            printf("[WARN] Fixed-Ratio Plain differs from Standard Plain pointwise.\n");
        }
        cudaFree(d_dec_std_plain);

        // --- Test 2: Outlier Mode ---
        printf("\n--- Outlier Mode ---\n");
        size_t cmpSize_outlier = 0;
        cudaMemset(d_cmp, 0, size_bytes * 2);

        float absEB_outlier = cuSZp_fixed_ratio(d_in, d_cmp, nbEle, &cmpSize_outlier, range, 500, targetRatio, CUSZP_MODE_OUTLIER);
        
        double actualRatio_outlier = (double)size_bytes / (double)cmpSize_outlier;
        printf("Target Ratio: %.2f\n", targetRatio);
        printf("Actual Ratio: %.2f (Size: %zu -> %zu)\n", actualRatio_outlier, size_bytes, cmpSize_outlier);
        printf("Resulting AbsEB: %.6e\n", absEB_outlier);

        // Decompression Check (Outlier)
        cuSZp_decompress_1D_outlier_f32(d_dec, d_cmp, nbEle, cmpSize_outlier, absEB_outlier);
        
        cudaMemcpy(h_dec.data(), d_dec, size_bytes, cudaMemcpyDeviceToHost);
        max_err = 0.0f;
        for(size_t i=0; i<nbEle; ++i) {
            float err = std::abs(h_in[i] - h_dec[i]);
            if(err > max_err) max_err = err;
        }
        printf("Max Error (Outlier): %.6e (Bound: %.6e)\n", max_err, absEB_outlier);
        if (max_err <= absEB_outlier * 1.00001f) {
            printf("[PASS] Outlier mode error bound respected.\n");
        } else {
            printf("[FAIL] Outlier mode max error exceeds bound!\n");
        }

        // Cross-check with Standard Outlier Compression
        size_t cmpSize_std_outlier = 0;
        cuSZp_compress_1D_outlier_f32(d_in, d_cmp_std, nbEle, &cmpSize_std_outlier, absEB_outlier);
        
        printf("Standard cuSZp Outlier Size: %zu\n", cmpSize_std_outlier);
        double size_diff_pct_outlier = 100.0 * std::abs((double)cmpSize_outlier - (double)cmpSize_std_outlier) / (double)cmpSize_std_outlier;
        printf("Size Difference: %.2f%%\n", size_diff_pct_outlier);
        
        if (size_diff_pct_outlier < 5.0) {
            printf("[PASS] Fixed-Ratio Outlier matches standard behavior.\n");
        } else {
            printf("[WARN] Significant size difference in outlier mode.\n");
        }

        // --- Verify Pure Standard Outlier Decompression ---
        printf("Verifying Pure Standard cuSZp Outlier Decompression...\n");
        float* d_dec_std = nullptr;
        cudaMalloc(&d_dec_std, size_bytes);
        cudaMemset(d_dec_std, 0, size_bytes);
        
        cuSZp_decompress_1D_outlier_f32(d_dec_std, d_cmp_std, nbEle, cmpSize_std_outlier, absEB_outlier);
        
        std::vector<float> h_dec_std(nbEle);
        cudaMemcpy(h_dec_std.data(), d_dec_std, size_bytes, cudaMemcpyDeviceToHost);
        
        float max_err_std = 0.0f;
        float max_diff_fix_std_outlier = 0.0f;
        for(size_t i=0; i<nbEle; ++i) {
            float err = std::abs(h_in[i] - h_dec_std[i]);
            if(err > max_err_std) max_err_std = err;

            float diff = std::abs(h_dec[i] - h_dec_std[i]);
            if(diff > max_diff_fix_std_outlier) max_diff_fix_std_outlier = diff;
        }
        printf("Max Error (Pure Standard Outlier): %.6e (Bound: %.6e)\n", max_err_std, absEB_outlier);
        if(max_err_std <= absEB_outlier * 1.00001f) {
            printf("[PASS] Standard Outlier respects error bound.\n");
        } else {
            printf("[FAIL] Standard Outlier VIOLATES error bound!\n");
        }

        printf("Max Pointwise Diff (Fixed vs Standard Outlier): %.6e\n", max_diff_fix_std_outlier);
        if(max_diff_fix_std_outlier < 1e-9) {
            printf("[PASS] Fixed-Ratio Outlier matches Standard Outlier pointwise.\n");
        } else {
            printf("[WARN] Fixed-Ratio Outlier differs from Standard Outlier pointwise.\n");
        }

        cudaFree(d_dec_std);
    }
    
    // Cleanup
    cudaFree(d_in);
    cudaFree(d_dec);
    cudaFree(d_cmp);
    cudaFree(d_cmp_std);
    
    return 0;
}
