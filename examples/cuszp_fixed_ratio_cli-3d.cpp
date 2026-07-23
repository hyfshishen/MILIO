/**
 * @file cuszp_fixed_ratio_cli-3d.cpp
 * @brief Command-line interface for cuSZp 3D fixed-ratio compression testing.
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

#define CHECK_CUDA(x) do { \
  cudaError_t err__ = (x); \
  if (err__ != cudaSuccess) { \
    fprintf(stderr, "CUDA error %s:%d: %s\n", __FILE__, __LINE__, cudaGetErrorString(err__)); \
    exit(EXIT_FAILURE); \
  } \
} while (0)

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

// 3D/2D EB picker: 64 original floats per block (4x4x4 for 3D, 8x8 for 2D).
static inline int pick_best_eb_from_finalrow_64(const uint4* final_row,
                                                int sample_per_eb,
                                                double R_target)
{
    // Reconstruct bytes_per_eb from uint4 array (32 uint4 = 128 ints)
    int bytes_per_eb[128];
    for (int lane = 0; lane < 32; ++lane) {
        const uint4 q = final_row[lane];
        const int base = lane * 4;
        bytes_per_eb[base + 0] = (int)q.x;
        bytes_per_eb[base + 1] = (int)q.y;
        bytes_per_eb[base + 2] = (int)q.z;
        bytes_per_eb[base + 3] = (int)q.w;
    }
    
    // This computes the ratio in the PADDED domain (orig_per_block * sample_per_eb).
    // To target a ratio relative to the UNPADDED file size, the caller scales the
    // target ratio by (padded_size / unpadded_size) before calling this.
    const size_t orig_per_block = 64 * sizeof(float);
    const double total_orig     = (double)orig_per_block * (double)sample_per_eb;



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

void print_usage(const char* prog_name) {
    printf("Usage: %s [options]\n", prog_name);
    printf("Options:\n");
    printf("  -i <input_file>   Path to input binary file (float32)\n");
    printf("  -o <output_file>  Path to output compressed file (optional)\n");
    printf("  -x <dim_x>        Dimension X (required)\n");
    printf("  -y <dim_y>        Dimension Y (required)\n");
    printf("  -z <dim_z>        Dimension Z (required)\n");
    printf("  -r <ratio>        Target compression ratio (default: 4.0)\n");
    printf("  -m <mode>         Compression mode: plain or outlier (default: outlier)\n");
    printf("  -s <rate>         Sampling rate (default: 1000)\n");
    printf("  -h                Show help\n");
}

int main(int argc, char** argv) {
    std::string input_file, output_file;
    size_t x = 0, y = 0, z = 0;
    float target_ratio = 4.0f;
    cuszp_mode_t mode = CUSZP_MODE_OUTLIER;
    std::string mode_str = "outlier";
    int sample_rate = 10;

    int opt;
    while ((opt = getopt(argc, argv, "i:o:x:y:z:r:m:s:h")) != -1) {
        switch (opt) {
            case 'i': input_file = optarg; break;
            case 'o': output_file = optarg; break;
            case 'x': x = std::stoul(optarg); break;
            case 'y': y = std::stoul(optarg); break;
            case 'z': z = std::stoul(optarg); break;
            case 'r': target_ratio = std::stof(optarg); break;
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

    printf("Configuration:\n");
    printf("  Input File: %s\n", input_file.c_str());
    printf("  Dims: %zux%zux%zu\n", x, y, z);
    printf("  Elements: %zu\n", num_elements);
    printf("  Target Ratio: %.2f\n", target_ratio);
    printf("  Mode: %s\n", mode_str.c_str());
    printf("  Sample Rate: %d\n", sample_rate);

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
    cudaMalloc(&d_data, num_elements * sizeof(float));
    cudaMalloc(&d_compressed, num_elements * sizeof(float));
    cudaMemcpy(d_data, h_data.data(), num_elements * sizeof(float), cudaMemcpyHostToDevice);



        // Select EB
    // Calculate total blocks (4x4x4)
    uint dimzBlock = (dims.z + 3) / 4;
    uint dimyBlock = (dims.y + 3) / 4;
    uint dimxBlock = (dims.x + 3) / 4;
    size_t total_blocks = (size_t)dimzBlock * dimyBlock * dimxBlock;
    if (total_blocks == 0) total_blocks = 1;
    
    int sample_per_eb = total_blocks / sample_rate;
    if (sample_per_eb < 1) sample_per_eb = 1;
    
    // Adjust Target Ratio to account for Padding
    // Profiler works on Padded Domain (total_blocks * 64 chars).
    // We want Ratio relative to File Domain (num_elements).
    // Target_Ratio_Padded = Target_Ratio_File * (Padded_Size / Unpadded_Size).
    double padded_size = (double)total_blocks * 64.0 * 4.0;
    double unpadded_size = (double)num_elements * 4.0;
    double ratio_correction = padded_size / unpadded_size;
    double adjusted_target_ratio = (double)target_ratio * ratio_correction;


    cudaStream_t stream;
    cudaStreamCreate(&stream);

    // Warmup — use the actual 3D compressor. The previous version called the
    // generic 1D cuSZp_compress() on 3D data, which routed through a 1D kernel
    // that corrupts device state and made later 3D compression non-deterministic
    // (passing on thin fields like CESM but failing on large cubic fields like NYX).
    printf("Warming up GPU...\n");
    float warmup_eb = range * 1e-4; // Dummy EB
    size_t w_cmpSize = 0;
    for(int i=0; i<10; i++) {
        if (mode == CUSZP_MODE_PLAIN)
            cuSZp_compress_3D_plain_f32(d_data, d_compressed, num_elements, &w_cmpSize, dims, warmup_eb, stream);
        else
            cuSZp_compress_3D_outlier_f32(d_data, d_compressed, num_elements, &w_cmpSize, dims, warmup_eb, stream);
    }
    cudaStreamSynchronize(stream);
    printf("Warmup complete.\n");

    TimingGPU timer_GPU;

    // --- Step 1: Profiling ---
    printf("Starting Profiling...\n");
    timer_GPU.StartCounter();
    size_t profBytes = 0;
    if (mode == CUSZP_MODE_PLAIN)
        cuSZp_profile_3D_plain_f32(d_data, d_compressed, num_elements, &profBytes, dims, range, sample_rate, stream);
    else
        cuSZp_profile_3D_outlier_f32(d_data, d_compressed, num_elements, &profBytes, dims, range, sample_rate, stream);
    
    // Fetch profile result
    uint4 h_final_row[32]{};
    const size_t needBytes = 32 * sizeof(uint4);
    if (profBytes > 0)
        cudaMemcpyAsync(h_final_row, d_compressed, std::min(needBytes, profBytes), cudaMemcpyDeviceToHost, stream);
    
    


    
    // printf("Target Ratio: %.2f (Adjusted for Padding: %.2f)\n", target_ratio, adjusted_target_ratio);

    int best_idx = pick_best_eb_from_finalrow_64(h_final_row, sample_per_eb, adjusted_target_ratio);
    float relEB = PRO_128_REL_EB[best_idx];
    float absEB = relEB * range;

    float time_profile = timer_GPU.GetCounter();
    
    // Re-parse to get sampled bytes for the chosen EB to report Estimated Ratio
    // (We could optimize this by efficient helper usage, but simple re-parse is fine for CLI)
    int selected_sampled_bytes = 0;
    {
        uint4 q = h_final_row[best_idx / 4];
        int comp = best_idx % 4;
        if (comp == 0) selected_sampled_bytes = (int)q.x;
        else if (comp == 1) selected_sampled_bytes = (int)q.y;
        else if (comp == 2) selected_sampled_bytes = (int)q.z;
        else selected_sampled_bytes = (int)q.w;
    }
    
    // Calculate Estimated Ratio relative to UNPADDED original
    double est_padded_cmp_size = (double)selected_sampled_bytes / (double)sample_per_eb * (double)total_blocks;
    double est_ratio_unpadded = unpadded_size / est_padded_cmp_size; // unpadded_size is in bytes (num_elements*4)

    printf("  Profiling Time: %.3f ms\n", time_profile);
    printf("  Selected AbsEB: %.6e (RelEB: %.6e)\n", absEB, relEB);
    printf("  Estimated Ratio: %.2f (Target: %.2f)\n", est_ratio_unpadded, target_ratio);

    // --- Step 2: Compression ---
    printf("Starting Compression...\n");
    size_t compressed_size = 0;

    // Prepare inputs outside the timed region: upload the (intact) host data and
    // zero the compressed buffer. The compression timer then measures the fused
    // kernel only — consistent with the profiling/decompression timers above.
    CHECK_CUDA(cudaMemcpyAsync(d_data, h_data.data(), num_elements * sizeof(float), cudaMemcpyHostToDevice, stream));
    CHECK_CUDA(cudaMemsetAsync(d_compressed, 0, num_elements * sizeof(float), stream));
    cudaStreamSynchronize(stream);

    timer_GPU.StartCounter();
    if (mode == CUSZP_MODE_PLAIN)
        cuSZp_compress_3D_plain_f32(d_data, d_compressed, num_elements, &compressed_size, dims, absEB, stream);
    else
        cuSZp_compress_3D_outlier_f32(d_data, d_compressed, num_elements, &compressed_size, dims, absEB, stream);
    float time_compress = timer_GPU.GetCounter();

    printf("  Compression Time: %.3f ms\n", time_compress);
    printf("  Compressed Size: %zu\n", compressed_size);
    printf("  Achieved Ratio: %.2f\n", (float)(num_elements * sizeof(float)) / compressed_size);

    double data_size_gb = (double)(num_elements * sizeof(float)) / 1e9;
    printf("Throughput Statistics:\n");
    printf("  Profiling Throughput:    %.2f GB/s\n", data_size_gb / (time_profile/1000.0));
    printf("  Compression Throughput:  %.2f GB/s\n", data_size_gb / (time_compress/1000.0));
    printf("  Total (Prof+Comp) Thrpt: %.2f GB/s\n", data_size_gb / ((time_profile + time_compress)/1000.0));

    // --- Step 3: Decompression ---
    printf("Starting Decompression...\n");
    float* d_dec;
    cudaMalloc(&d_dec, num_elements * sizeof(float));
    timer_GPU.StartCounter();
    if (mode == CUSZP_MODE_PLAIN)
        cuSZp_decompress_3D_plain_f32(d_dec, d_compressed, num_elements, compressed_size, dims, absEB, stream);
    else
        cuSZp_decompress_3D_outlier_f32(d_dec, d_compressed, num_elements, compressed_size, dims, absEB, stream);
    float time_decomp = timer_GPU.GetCounter();

    printf("  Decompression Time: %.3f ms\n", time_decomp);
    printf("  Decompression Throughput: %.2f GB/s\n", data_size_gb / (time_decomp/1000.0));

    // Verify
    std::vector<float> h_dec(num_elements);
    cudaMemcpy(h_dec.data(), d_dec, num_elements * sizeof(float), cudaMemcpyDeviceToHost);
    double max_err = 0.0;
    double mse = 0.0;
    for(size_t i=0; i<num_elements; ++i) {
        double diff = std::abs(h_dec[i] - h_data[i]);
        if (diff > max_err) max_err = diff;
        mse += diff*diff;
    }
    mse /= num_elements;
    double psnr = 20.0 * log10(range) - 10.0 * log10(mse);

    printf("Verification Results:\n");
    printf("  Max Error: %.6e\n", max_err);
    printf("  PSNR: %.2f dB\n", psnr);
    printf("  Compliance: %s\n", max_err <= absEB * 1.1 ? "PASS" : "FAIL");

    cudaFree(d_data);
    cudaFree(d_compressed);
    cudaFree(d_dec);
    cudaStreamDestroy(stream);
    return 0;
}
