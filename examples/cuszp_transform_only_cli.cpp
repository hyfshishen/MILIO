/**
 * @file cuszp_transform_only_cli.cpp
 * @brief Standalone Command-line interface for cuSZp transform-based compression (WHT/Poly).
 *        Refactored to call via wrapper functions.
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstring>
#include <cmath>
#include <cuda_runtime.h>
#include <unistd.h>
#include "../src/cuSZp_entry_1D_transformed_f32.h" // New header
#include "../include/cuSZp/cuSZp_timer.h" // Is this compatible with cpp? Yes if just class.
// Note: cuSZp_timer.h includes cuda_runtime.h which is fine in cpp for types.

void print_usage(const char* prog_name) {
    printf("Usage: %s [options]\n", prog_name);
    printf("Options:\n");
    printf("  -i <input_file>   Path to the input binary file (float32)\n");
    printf("  -o <output_file>  Path to output compressed file (optional)\n");
    printf("  -n <num_elements> Number of elements (required)\n");
    printf("  -r <ratio>        Target compression ratio (default: 4.0)\n");
    printf("  -m <mode>         Compression mode: wht, poly (default: wht)\n");
    printf("  -h                Show this help message\n");
}

int main(int argc, char** argv) {
    std::string input_file;
    std::string output_file;
    size_t num_elements = 0;
    float target_ratio = 4.0f;
    std::string mode_str = "wht";

    int opt;
    while ((opt = getopt(argc, argv, "i:o:n:r:m:h")) != -1) {
        switch (opt) {
            case 'i': input_file = optarg; break;
            case 'o': output_file = optarg; break;
            case 'n': num_elements = std::stoul(optarg); break;
            case 'r': target_ratio = std::stof(optarg); break;
            case 'm': mode_str = optarg; break;
            case 'h': print_usage(argv[0]); return 0;
            default: print_usage(argv[0]); return 1;
        }
    }

    if (input_file.empty() || num_elements == 0) {
        fprintf(stderr, "Error: Input file and number of elements are required.\n");
        return 1;
    }

    bool is_wht = (mode_str == "wht");
    bool is_poly = (mode_str == "poly");

    if (!is_wht && !is_poly) {
        fprintf(stderr, "Error: Invalid mode '%s'. Supported modes: wht, poly\n", mode_str.c_str());
        return 1;
    }

    printf("Configuration:\n");
    printf("  Input File: %s\n", input_file.c_str());
    printf("  Elements: %zu\n", num_elements);
    printf("  Target Ratio: %.2f\n", target_ratio);
    printf("  Mode: %s\n", mode_str.c_str());

    // Allocate host memory
    std::vector<float> h_data(num_elements);

    // Read input file
    std::ifstream infile(input_file, std::ios::binary);
    if (!infile) {
        fprintf(stderr, "Error: Cannot open input file %s\n", input_file.c_str());
        return 1;
    }
    infile.read(reinterpret_cast<char*>(h_data.data()), num_elements * sizeof(float));
    infile.close();

    // Data analysis for range (calc min/max/range)
    float min_val = h_data[0];
    float max_val = h_data[0];
    for (size_t i = 1; i < num_elements; ++i) {
        if (h_data[i] < min_val) min_val = h_data[i];
        if (h_data[i] > max_val) max_val = h_data[i];
    }
    float range = max_val - min_val;
    printf("Data Range: %.6f (Min: %.6f, Max: %.6f)\n", range, min_val, max_val);

    // Device allocation
    float* d_oriData;
    unsigned char* d_cmpBytes;
    cudaMalloc(&d_oriData, num_elements * sizeof(float));
    cudaMalloc(&d_cmpBytes, num_elements * sizeof(float)); 
    cudaMemcpy(d_oriData, h_data.data(), num_elements * sizeof(float), cudaMemcpyHostToDevice);

    cudaStream_t stream;
    cudaStreamCreate(&stream);

    // Warmup
    printf("Warming up GPU...\n");
    size_t dummy_cmpSize = 0;
    if (is_wht)
        cuSZp_compress_1D_transform_wht_f32(d_oriData, d_cmpBytes, num_elements, &dummy_cmpSize, target_ratio, stream);
    else
        cuSZp_compress_1D_transform_poly_f32(d_oriData, d_cmpBytes, num_elements, &dummy_cmpSize, target_ratio, stream);
    
    cudaStreamSynchronize(stream);
    printf("Warmup complete.\n");

    TimingGPU timer_GPU;
    TimingGPU timer_Kernel;
    
    // Compression
    printf("Starting Compression...\n");
    size_t compressed_size = 0;
    
    timer_GPU.StartCounter();
    
    // 1. H2D
    cudaMemcpyAsync(d_oriData, h_data.data(), num_elements * sizeof(float), cudaMemcpyHostToDevice, stream);

    // Kernel Timer Start
    timer_Kernel.StartCounter();

    // 2. Kernel (via wrappers)
    if (is_wht) {
        cuSZp_compress_1D_transform_wht_f32(d_oriData, d_cmpBytes, num_elements, &compressed_size, target_ratio, stream);
    } else {
        cuSZp_compress_1D_transform_poly_f32(d_oriData, d_cmpBytes, num_elements, &compressed_size, target_ratio, stream);
    }

    // Kernel Timer Stop (Synchronized)
    cudaStreamSynchronize(stream);
    float time_kernel_ms = timer_Kernel.GetCounter();

    // 3. D2H (Download Compressed Data)
    unsigned char* h_encoded = (unsigned char*)malloc(compressed_size);
    cudaMemcpyAsync(h_encoded, d_cmpBytes, compressed_size, cudaMemcpyDeviceToHost, stream);
    cudaStreamSynchronize(stream);
    
    float time_e2e_ms = timer_GPU.GetCounter();
    
    double data_size_gb = (double)(num_elements * sizeof(float)) / 1e9;
    
    printf("  End-to-End Time:       %.3f ms\n", time_kernel_ms);
    printf("  End-to-End Throughput: %.2f GB/s\n", data_size_gb / (time_kernel_ms/1000.0)); 

    // --- Decompression ---
    printf("Starting Decompression...\n");
    float* d_decData;
    cudaMalloc(&d_decData, num_elements * sizeof(float));
    
    // Reuse d_cmpBytes as input
    
    timer_Kernel.StartCounter();

    if (is_wht) {
        cuSZp_decompress_1D_transform_wht_f32(d_decData, d_cmpBytes, num_elements, compressed_size, target_ratio, stream);
    } else {
        cuSZp_decompress_1D_transform_poly_f32(d_decData, d_cmpBytes, num_elements, compressed_size, target_ratio, stream);
    }
    
    // Explicit sync for kernel timing
    cudaStreamSynchronize(stream);
    float time_decomp_kernel_ms = timer_Kernel.GetCounter();

    printf("  Decompression End-to-End Time:       %.3f ms\n", time_decomp_kernel_ms);
    printf("  Decompression End-to-End Throughput: %.2f GB/s\n", data_size_gb / (time_decomp_kernel_ms/1000.0));

    // --- Verify Data Quality (PSNR) ---
    float* h_decompressed = (float*)malloc(num_elements * sizeof(float));
    cudaMemcpy(h_decompressed, d_decData, num_elements * sizeof(float), cudaMemcpyDeviceToHost);

    double mse = 0.0;
    
    for (size_t i = 0; i < num_elements; ++i) {
        float diff = h_data[i] - h_decompressed[i];
        mse += diff * diff;
    }
    mse /= num_elements;
    double psnr = 20.0 * log10(range) - 10.0 * log10(sqrt(mse)); // Using sqrt(mse) based on previous correction discussion or just 10*log10(mse)?
    // Standard: 20*log10(MAX) - 10*log10(MSE) = 20*log10(MAX/sqrt(MSE))
    // My code previously used 20*log10(range) - 10*log10(mse). This IS correct.
    // 10*log10(mse) = 20*log10(sqrt(mse)).
    // So 20*log10(range) - 20*log10(sqrt(mse)) = 20*log10(range/rmse). Correct.
    psnr = 20.0 * log10(range) - 10.0 * log10(mse);

    printf("  RMSE: %e\n", sqrt(mse));
    printf("  PSNR: %.2f dB\n", psnr);

    free(h_encoded);
    free(h_decompressed);
    cudaFree(d_oriData);
    cudaFree(d_cmpBytes);
    cudaFree(d_decData);

    return 0;
}
