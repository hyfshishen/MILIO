/**
 * @file cuszp_fixed_ratio_cli.cpp
 * @brief Command-line interface for cuSZp fixed-ratio compression testing with detailed profiling.
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstring>
#include <cmath>
#include <cuda_runtime.h>
#include <unistd.h>
#include "cuSZp.h"

// --- Internal Logic Copied from src/cuSZp.cu to enable separate timing ---

static const float PRO_128_REL_EB_CLI[128] =
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

static inline int pick_best_eb_from_finalrow_CLI(const uint4* final_row,
                                             int sample_per_eb,
                                             double R_target)
{
    // 1D fixed-ratio uses 32 original floats per block.
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

    // Pick the smallest error bound whose estimated ratio still meets the target.
    int best = 127;
    for (int i = 127; i >= 0; --i) {
        const int b = bytes_per_eb[i];
        if (b <= 0) {              
            best = i; break;
        }
        const double ratio = total_orig / (double)b;
        if (ratio >= R_target) {   
            best = i; break;
        }
    }
    return best;
}

// -------------------------------------------------------------------------

// Helper function to print usage
void print_usage(const char* prog_name) {
    printf("Usage: %s [options]\n", prog_name);
    printf("Options:\n");
    printf("  -i <input_file>   Path to the input binary file (float32)\n");
    printf("  -o <output_file>  Path to output compressed file (optional)\n");
    printf("  -D <recon_file>   Path to write reconstructed (decompressed) field (optional)\n");
    printf("  -n <num_elements> Number of elements (required)\n");
    printf("  -r <ratio>        Target compression ratio (default: 4.0)\n");
    printf("  -m <mode>         Compression mode: plain or outlier (default: outlier)\n");
    printf("  -h                Show this help message\n");
}

int main(int argc, char** argv) {
    std::string input_file;
    std::string output_file;
    std::string decomp_file;
    size_t num_elements = 0;
    float target_ratio = 4.0f;
    cuszp_mode_t mode = CUSZP_MODE_OUTLIER;
    std::string mode_str = "outlier";

    int sample_rate = 1000;  

    int opt;
    while ((opt = getopt(argc, argv, "i:o:n:r:m:s:D:h")) != -1) {
        switch (opt) {
            case 'D':
                decomp_file = optarg;
                break;
            case 'i':
                input_file = optarg;
                break;
            case 'o':
                output_file = optarg;
                break;
            case 'n':
                num_elements = std::stoul(optarg);
                break;
            case 'r':
                target_ratio = std::stof(optarg);
                break;
            case 's':
                sample_rate = std::stoi(optarg);
                break;
            case 'm':
                mode_str = optarg;
                if (mode_str == "plain") {
                    mode = CUSZP_MODE_PLAIN;
                } else if (mode_str == "outlier") {
                    mode = CUSZP_MODE_OUTLIER;
                } else {
                    fprintf(stderr, "Invalid mode: %s. Use 'plain' or 'outlier'.\n", mode_str.c_str());
                    return 1;
                }
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }

    if (input_file.empty() || num_elements == 0) {
        fprintf(stderr, "Error: Input file and number of elements are required.\n");
        print_usage(argv[0]);
        return 1;
    }

    printf("Configuration:\n");
    printf("  Input File: %s\n", input_file.c_str());
    printf("  Output File: %s\n", output_file.empty() ? "(none)" : output_file.c_str());
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
    if (infile.gcount() != num_elements * sizeof(float)) {
        fprintf(stderr, "Warning: Read fewer bytes than expected.\n");
    }
    infile.close();

    // Data analysis for range
    float min_val = h_data[0];
    float max_val = h_data[0];
    for (size_t i = 1; i < num_elements; ++i) {
        if (h_data[i] < min_val) min_val = h_data[i];
        if (h_data[i] > max_val) max_val = h_data[i];
    }
    float range = max_val - min_val;
    printf("Data Range: %.6f (Min: %.6f, Max: %.6f)\n", range, min_val, max_val);

    // Device allocation
    float* d_data;
    unsigned char* d_compressed;
    //unsigned char* d_compressed_final; // Only if needed (cuSZp reuses same buffer?)
    // Actually cuSZp_fixed_ratio writes to d_cmpBytes.
    
    // Allocate generous buffer for compression output (original size)
    cudaMalloc(&d_data, num_elements * sizeof(float));
    cudaMalloc(&d_compressed, num_elements * sizeof(float)); 

    cudaMemcpy(d_data, h_data.data(), num_elements * sizeof(float), cudaMemcpyHostToDevice);

    cudaStream_t stream;
    cudaStreamCreate(&stream);

    // Hardcoded default matching library
    // int sample_rate = 1000;  // Now defined at top and parsed from args  

    // Warmup
    printf("Warming up GPU...\n");
    float warmup_eb = range * 1e-4; // Dummy EB for warmup
    size_t w_cmpSize = 0;
    cuszp_type_t dataType = CUSZP_TYPE_FLOAT;
    
    for(int i=0; i<10; i++) {
        cuSZp_compress(d_data, d_compressed, num_elements, &w_cmpSize, warmup_eb, dataType, mode, stream);
    }
    cudaStreamSynchronize(stream);
    printf("Warmup complete.\n");

    // Timing
    TimingGPU timer_GPU;

    // --- Step 1: Profiling ---
    printf("Starting Profiling...\n");
    
    size_t profBytes = 0;
    timer_GPU.StartCounter();
    
    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_profile_1D_plain_f32(d_data, d_compressed, num_elements, &profBytes, range, sample_rate, stream);
    } else {
        cuSZp_profile_1D_outlier_f32(d_data, d_compressed, num_elements, &profBytes, range, sample_rate, stream);
    }
    
    // Profiling also includes fetching the results back
    const size_t needBytes = 32 * sizeof(uint4);
    uint4 h_final_row[32]{};
    const size_t copyBytes = std::min(needBytes, profBytes);
    if (copyBytes > 0) {
        cudaMemcpyAsync(h_final_row, d_compressed, copyBytes, cudaMemcpyDeviceToHost, stream);
    }
    
    
    
    const int total_blocks = static_cast<int>((num_elements + 31) / 32);
    if (sample_rate <= 0) sample_rate = 1;
    int sample_per_eb = total_blocks / sample_rate;
    if (sample_per_eb < 1) sample_per_eb = 1;

    size_t compressed_size = 0;
    if (sample_per_eb <= 0) {
        fprintf(stderr, "Error during profiling setup.\n");
        return 1;
    }

    const int   best_idx = pick_best_eb_from_finalrow_CLI(h_final_row, sample_per_eb, (double)target_ratio);
    const float relEB    = PRO_128_REL_EB_CLI[best_idx];
    const float absEB    = relEB * range;

    float time_profile_ms = timer_GPU.GetCounter();
    
    printf("  Profiling Time: %.3f ms\n", time_profile_ms);
    printf("  Selected AbsEB: %.6e (RelEB: %.6e)\n", absEB, relEB);

    // --- Step 2: Compression ---
    printf("Starting Compression...\n");
    cudaMemcpyAsync(d_data, h_data.data(), num_elements * sizeof(float), cudaMemcpyHostToDevice, stream);
    cudaStreamSynchronize(stream);

    timer_GPU.StartCounter();
    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_compress_1D_plain_f32(d_data, d_compressed, num_elements, &compressed_size, absEB, stream);
    } else {
        cuSZp_compress_1D_outlier_f32(d_data, d_compressed, num_elements, &compressed_size, absEB, stream);
    }
    float time_compress_ms = timer_GPU.GetCounter();
    
    printf("  Compression Time: %.3f ms\n", time_compress_ms);
    printf("  Compressed Size: %zu bytes\n", compressed_size);
    printf("  Achieved Ratio: %.2f\n", (float)(num_elements * sizeof(float)) / compressed_size);

    double data_size_gb = (double)(num_elements * sizeof(float)) / 1e9;
    printf("Throughput Statistics:\n");
    printf("  Profiling Throughput:    %.2f GB/s\n", data_size_gb / (time_profile_ms/1000.0));
    printf("  Compression Throughput:  %.2f GB/s\n", data_size_gb / (time_compress_ms/1000.0));
    printf("  Total (Prof+Comp) Thrpt: %.2f GB/s\n", data_size_gb / ((time_profile_ms + time_compress_ms)/1000.0));


    // Write output if requested
    if (!output_file.empty()) {
        std::vector<unsigned char> h_compressed(compressed_size);
        cudaMemcpy(h_compressed.data(), d_compressed, compressed_size, cudaMemcpyDeviceToHost);
        
        std::ofstream outfile(output_file, std::ios::binary);
        outfile.write(reinterpret_cast<char*>(h_compressed.data()), compressed_size);
        outfile.close();
        printf("Written compressed data to %s\n", output_file.c_str());
    }

    // --- Step 3: Decompression ---
    printf("Starting Decompression...\n");
    float* d_decompressed;
    cudaMalloc(&d_decompressed, num_elements * sizeof(float));

    timer_GPU.StartCounter();
    if (mode == CUSZP_MODE_PLAIN) {
        cuSZp_decompress_1D_plain_f32(d_decompressed, d_compressed, num_elements, compressed_size, absEB, stream);
    } else {
        cuSZp_decompress_1D_outlier_f32(d_decompressed, d_compressed, num_elements, compressed_size, absEB, stream);
    }

    float time_decompress_ms = timer_GPU.GetCounter();
    
    printf("  Decompression Time: %.3f ms\n", time_decompress_ms);
    printf("  Decompression Throughput: %.2f GB/s\n", data_size_gb / (time_decompress_ms/1000.0));


    // Verification
    std::vector<float> h_decompressed(num_elements);
    cudaMemcpy(h_decompressed.data(), d_decompressed, num_elements * sizeof(float), cudaMemcpyDeviceToHost);

    // Optional: write the reconstructed (decompressed) field for visualization
    if (!decomp_file.empty()) {
        std::ofstream decfile(decomp_file, std::ios::binary);
        decfile.write(reinterpret_cast<char*>(h_decompressed.data()), num_elements * sizeof(float));
        decfile.close();
        printf("Written reconstructed data to %s\n", decomp_file.c_str());
    }

    // Compute Error Metrics
    double mse = 0.0;
    double max_err = 0.0;
    for (size_t i = 0; i < num_elements; ++i) {
        double diff = h_decompressed[i] - h_data[i];
        mse += diff * diff;
        if (std::abs(diff) > max_err) max_err = std::abs(diff);
    }
    mse /= num_elements;
    double psnr = 20.0 * log10(range) - 10.0 * log10(mse);

    printf("Verification Results:\n");
    printf("  Max Error: %.6e\n", max_err);
    printf("  PSNR: %.2f dB\n", psnr);
    printf("  Error Bound Compliance: %s\n", max_err <= absEB * 1.1 ? "PASS" : "FAIL (approx)");

    // Cleanup
    cudaFree(d_data);
    cudaFree(d_compressed);
    cudaFree(d_decompressed);
    cudaStreamDestroy(stream);

    return 0;
}
