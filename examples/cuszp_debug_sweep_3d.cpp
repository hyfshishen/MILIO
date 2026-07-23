/**
 * @file cuszp_debug_sweep_3d.cpp
 * @brief Brute-force sweep tool to verify 3D Profiling vs Compression consistency.
 * 
 * This tool runs the profiling kernel once, then iterates through ALL 128 supported error bounds,
 * running the compression kernel for each. It reports a table comparing:
 * - Estimated Compressed Size (from Profiling)
 * - Actual Compressed Size (from Compression)
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

// --- Internal EB Selection Logic (Copied/Adapted for consistency) ---
static const float PRO_128_REL_EB[128] =
{
    1e-1f, 9.7e-2f, 9.4e-2f, 9.1e-2f, 8.8e-2f, 8.5e-2f, 8.2e-2f, 7.9e-2f,
    7.6e-2f, 7.3e-2f, 7.0e-2f, 6.7e-2f, 6.4e-2f, 6.1e-2f, 5.8e-2f, 5.5e-2f,
    5.2e-2f, 4.9e-2f, 4.6e-2f, 4.3e-2f, 4.0e-2f, 3.7e-2f, 3.4e-2f, 3.1e-2f,
    2.8e-2f, 2.5e-2f, 2.2e-2f, 1.9e-2f, 1.6e-2f, 1.3e-2f, 1.1e-2f, 1e-2f,
    9.7e-3f, 9.4e-3f, 9.1e-3f, 8.8e-3f, 8.5e-3f, 8.2e-3f, 7.9e-3f, 7.6e-3f,
    7.3e-3f, 7.0e-3f, 6.7e-3f, 6.4e-3f, 6.1e-3f, 5.8e-3f, 5.5e-3f, 5.2e-3f,
    4.9e-3f, 4.6e-3f, 4.3e-3f, 4.0e-3f, 3.7e-3f, 3.4e-3f, 3.1e-3f, 2.8e-3f,
    2.5e-3f, 2.2e-3f, 1.9e-3f, 1.6e-3f, 1.3e-3f, 1.1e-3f, 1.05e-3f, 1e-3f,
    9.7e-4f, 9.4e-4f, 9.1e-4f, 8.8e-4f, 8.5e-4f, 8.2e-4f, 7.9e-4f, 7.6e-4f,
    7.3e-4f, 7.0e-4f, 6.7e-4f, 6.4e-4f, 6.1e-4f, 5.8e-4f, 5.5e-4f, 5.2e-4f,
    4.9e-4f, 4.6e-4f, 4.3e-4f, 4.0e-4f, 3.7e-4f, 3.4e-4f, 3.1e-4f, 2.8e-4f,
    2.5e-4f, 2.2e-4f, 1.9e-4f, 1.6e-4f, 1.3e-4f, 1.1e-4f, 1.05e-4f, 1e-4f,
    9.7e-5f, 9.4e-5f, 9.1e-5f, 8.8e-5f, 8.5e-5f, 8.2e-5f, 7.9e-5f, 7.6e-5f,
    7.3e-5f, 7.0e-5f, 6.7e-5f, 6.4e-5f, 6.1e-5f, 5.8e-5f, 5.5e-5f, 5.2e-5f,
    5.0e-5f, 4.5e-5f, 4.0e-5f, 3.5e-5f, 3.0e-5f, 2.5e-5f, 2.0e-5f, 1.5e-5f,
    1.0e-5f, 9.0e-6f, 8.0e-6f, 5.0e-6f, 4.0e-6f, 3.0e-6f, 2.00e-6f, 1e-6f
};

void parse_final_row(const uint4* final_row, int* bytes_per_eb) {
    for (int lane = 0; lane < 32; ++lane) {
        const uint4 q = final_row[lane];
        const int base = lane * 4;
        bytes_per_eb[base + 0] = (int)q.x;
        bytes_per_eb[base + 1] = (int)q.y;
        bytes_per_eb[base + 2] = (int)q.z;
        bytes_per_eb[base + 3] = (int)q.w;
    }
}

void print_usage(const char* prog_name) {
    printf("Usage: %s [options]\n", prog_name);
    printf("Options:\n");
    printf("  -i <input_file>   Path to input binary file (float32)\n");
    printf("  -x <dim_x>        Dimension X (required)\n");
    printf("  -y <dim_y>        Dimension Y (required)\n");
    printf("  -z <dim_z>        Dimension Z (required)\n");
    printf("  -m <mode>         Compression mode: plain or outlier (default: outlier)\n");
    printf("  -s <rate>         Sampling rate (default: 1000)\n");
    printf("  -h                Show help\n");
}

int main(int argc, char** argv) {
    std::string input_file;
    size_t x = 0, y = 0, z = 0;
    cuszp_mode_t mode = CUSZP_MODE_OUTLIER;
    std::string mode_str = "outlier";
    int sample_rate = 1000;

    int opt;
    while ((opt = getopt(argc, argv, "i:x:y:z:m:s:h")) != -1) {
        switch (opt) {
            case 'i': input_file = optarg; break;
            case 'x': x = std::stoul(optarg); break;
            case 'y': y = std::stoul(optarg); break;
            case 'z': z = std::stoul(optarg); break;
            case 's': sample_rate = std::stoi(optarg); break;
            case 'm':
                mode_str = optarg;
                if (mode_str == "plain") mode = CUSZP_MODE_PLAIN;
                else if (mode_str == "outlier") mode = CUSZP_MODE_OUTLIER;
                else { fprintf(stderr, "Invalid mode.\n"); return 1; }
                break;
            case 'h': print_usage(argv[0]); return 0;
            default: print_usage(argv[0]); return 1;
        }
    }

    if (input_file.empty() || x == 0 || y == 0 || z == 0) {
        fprintf(stderr, "Error: Input file and dimensions (x,y,z) are required.\n");
        print_usage(argv[0]);
        return 1;
    }

    size_t num_elements = x * y * z;
    uint3 dims = make_uint3(x, y, z);
    
    // Calculate blocking for estimate
    uint dimzBlock = (dims.z + 3) / 4;
    uint dimyBlock = (dims.y + 3) / 4;
    uint dimxBlock = (dims.x + 3) / 4;
    size_t total_blocks = (size_t)dimzBlock * dimyBlock * dimxBlock;
    if (total_blocks == 0) total_blocks = 1;
    
    int sample_per_eb = total_blocks / sample_rate;
    if (sample_per_eb < 1) sample_per_eb = 1;
    
    // Correction for Padded vs Unpadded Domain
    // Profiling Kernel sums up bytes for PADDED blocks (total_blocks).
    // Actual File uses UNPADDED size (num_elements).
    // If we simply scale 'sampled_bytes' to 'total_blocks', we get Estimated PADDED Size.
    // If we compare Padded Size vs Unpadded Original, Ratio is inflated.
    // Correct logic:
    // Est_Full_Compressed_Bytes (Padded) = (sampled_bytes / sample_per_eb) * total_blocks.
    // Est_Ratio_File = Total_Original_Unpadded / Est_Full_Compressed_Bytes.
    
    double total_original_bytes_full = (double)num_elements * sizeof(float);

    printf("Configuration:\n");
    printf("  Input File: %s\n", input_file.c_str());
    printf("  Dims: %zux%zux%zu\n", x, y, z);
    printf("  Mode: %s\n", mode_str.c_str());
    printf("  Sample Rate: %d (Sampled Blocks: %d / %zu)\n", sample_rate, sample_per_eb, total_blocks);

    // Host Init
    std::vector<float> h_data(num_elements);
    std::ifstream infile(input_file, std::ios::binary);
    if (!infile) { fprintf(stderr, "Error opening input file.\n"); return 1; }
    infile.read(reinterpret_cast<char*>(h_data.data()), num_elements * sizeof(float));
    infile.close();

    // Range calc
    float min_val = h_data[0], max_val = h_data[0];
    for (size_t i = 1; i < num_elements; ++i) {
        if (h_data[i] < min_val) min_val = h_data[i];
        if (h_data[i] > max_val) max_val = h_data[i];
    }
    float range = max_val - min_val;
    printf("Data Range: %.6f\n", range);

    // Device Init
    float *d_data;
    unsigned char *d_compressed;
    // Alloc extra for compressed to avoid overflow
    size_t cmpCap = num_elements * sizeof(float) + 1024*1024;
    cudaMalloc(&d_data, num_elements * sizeof(float));
    cudaMalloc(&d_compressed, cmpCap);
    cudaMemcpy(d_data, h_data.data(), num_elements * sizeof(float), cudaMemcpyHostToDevice);

    cudaStream_t stream;
    cudaStreamCreate(&stream);

    // --- Profiling ---
    printf("\n=== Running Profiling ===\n");
    size_t profBytes = 0;
    if (mode == CUSZP_MODE_PLAIN)
        cuSZp_profile_3D_plain_f32(d_data, d_compressed, num_elements, &profBytes, dims, range, sample_rate, stream);
    else
        cuSZp_profile_3D_outlier_f32(d_data, d_compressed, num_elements, &profBytes, dims, range, sample_rate, stream);
    
    uint4 h_final_row[32]{};
    const size_t needBytes = 32 * sizeof(uint4);
    if (profBytes > 0)
        cudaMemcpyAsync(h_final_row, d_compressed, std::min(needBytes, profBytes), cudaMemcpyDeviceToHost, stream);
    cudaStreamSynchronize(stream);
    
    int bytes_per_eb[128];
    parse_final_row(h_final_row, bytes_per_eb);

    // --- Brute Force Sweep ---
    printf("\n=== Running Compression Sweep (128 EBs) ===\n");
    printf("%-5s | %-12s | %-12s | %-12s | %-12s | %-12s | %-12s\n", 
           "Idx", "RelEB", "Est.Bytes", "Est.Ratio", "Act.Bytes", "Act.Ratio", "Diff(%)");
    printf("---------------------------------------------------------------------------------------------------\n");

    for (int i = 0; i < 128; ++i) {
        float relEB = PRO_128_REL_EB[i];
        float absEB = relEB * range;
        
        // Estimate
        int sampled_bytes = bytes_per_eb[i];
        double est_ratio = 0.0;
        double est_bytes_full = 0.0;
        if (sampled_bytes > 0) {
            est_bytes_full = (double)sampled_bytes / (double)sample_per_eb * (double)total_blocks;
            // Est Ratio (File Domain)
            est_ratio = total_original_bytes_full / est_bytes_full;
        }

        // Action
        size_t act_bytes = 0;
        if (mode == CUSZP_MODE_PLAIN)
            cuSZp_compress_3D_plain_f32(d_data, d_compressed, num_elements, &act_bytes, dims, absEB, stream);
        else
            cuSZp_compress_3D_outlier_f32(d_data, d_compressed, num_elements, &act_bytes, dims, absEB, stream);
        cudaStreamSynchronize(stream);
        
        double act_ratio = (act_bytes > 0) ? (total_original_bytes_full / (double)act_bytes) : 0.0;
        
        // Diff % of Ratio
        double diff = 0.0;
        if (act_ratio > 0) diff = (est_ratio - act_ratio) / act_ratio * 100.0;
        
        printf("%-5d | %-1.4e | %-12.0f | %-12.4f | %-12zu | %-12.4f | %-12.2f%%\n",
               i, relEB, est_bytes_full, est_ratio, act_bytes, act_ratio, diff);
               
        // Flush every line for realtime feedback
        fflush(stdout);
    }
    
    cudaFree(d_data);
    cudaFree(d_compressed);
    cudaStreamDestroy(stream);
    return 0;
}
