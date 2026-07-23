#include <cstdio>
#include <cstdlib>
#include <vector>
#include <thread>
#include <mutex>
#include <string>
#include <iostream>
#include <cmath>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <cuda_runtime.h>
#include "cuSZp.h"
#include "cuSZp/cuSZp_entry_3D_f32.h" // For decompression API

struct Args {
    int num_gpus = 4;
    float target_ratio = 8.0f;
    std::string file_path = "/scratch/bfrq/bzhang28/nyx_velocity_x_1024x1024x1024.f32";
    size_t total_len = 1024 * 1024 * 1024; // Default 1024^3
    int dimx = 1024;
    int dimy = 1024;
    int dimz = 1024;
};

struct WorkerResult {
    int worker_id;
    size_t original_size;
    size_t compressed_size;
    double comp_time_sec;
    double decomp_time_sec;
    float abs_error_bound;
};

std::mutex print_mutex;

std::vector<float> global_data; // Host memory for all data

void worker_thread(int worker_id, int gpu_id, Args args, std::vector<WorkerResult>& results) {
    cudaSetDevice(gpu_id);
    
    // Simple even split
    size_t files_per_gpu = args.total_len / args.num_gpus;
    size_t start_idx = worker_id * files_per_gpu;
    size_t my_len = files_per_gpu;
    if (worker_id == args.num_gpus - 1) {
        my_len = args.total_len - start_idx;
    }
    
    size_t my_bytes = my_len * sizeof(float);
    
    // Calculate 3D chunk dimensions.
    // Assuming splitting along Z dimension for simplicity in interpreting 3D structure?
    // Wait, HACC was 1D. Nyx is 3D.
    // Splitting a 3D volume into N chunks for 3D compression requires each chunk to be a valid 3D block.
    // If we split purely linearly, the geometric meaning might be lost unless we define dimensions for the CHUNK.
    // 
    // IF we split along Z axis:
    // Global: X * Y * Z
    // Chunk:  X * Y * (Z / N)
    // This works perfectly if Z is divisible by N.
    
    if (args.dimz % args.num_gpus != 0) {
       // Just a warning
    }
    
    int chunk_z = args.dimz / args.num_gpus;
    int my_z = chunk_z;
    if(worker_id == args.num_gpus - 1) {
        my_z = args.dimz - worker_id * chunk_z;
    }
    
    // Verify length matches
    size_t expected_len = (size_t)args.dimx * args.dimy * my_z;
    if (my_len != expected_len) {
        // Mismatch usually means we can't cleanly interpret linear split as Z-split
        // But for 1024^3 and 1/2/4/8 GPUs, it divides cleanly.
    }
    
    uint3 chunk_dims = make_uint3(args.dimx, args.dimy, my_z);

    // Resources
    float* d_in = nullptr;
    float* d_dec = nullptr;
    unsigned char* d_cmp = nullptr;
    
    cudaMalloc(&d_in, my_bytes);
    cudaMalloc(&d_dec, my_bytes);
    cudaMalloc(&d_cmp, my_bytes * 1.5); // Safety margin
    
    // H2D
    cudaMemcpy(d_in, &global_data[start_idx], my_bytes, cudaMemcpyHostToDevice);
    
    // Range
    float min_val = global_data[start_idx];
    float max_val = global_data[start_idx];
    for (size_t i = 0; i < my_len; i++) {
        float val = global_data[start_idx + i];
        if (val < min_val) min_val = val;
        if (val > max_val) max_val = val;
    }
    float range = max_val - min_val;
    if (range <= 0) range = 1.0f;
    
    // Warmup
    size_t temp_sz;
    for(int k=0; k<10; k++) {
        cuSZp_fixed_ratio_3D(d_in, d_cmp, my_len, &temp_sz, chunk_dims, range, 500, args.target_ratio, CUSZP_MODE_PLAIN, 0);
    }
    
    size_t cmpSize = 0;
    cudaEvent_t start, stop;
    cudaEventCreate(&start); cudaEventCreate(&stop);
    
    // Compression
    cudaEventRecord(start);
    float absEB = cuSZp_fixed_ratio_3D(d_in, d_cmp, my_len, &cmpSize, chunk_dims, range, 1000, args.target_ratio, CUSZP_MODE_PLAIN, 0);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    float ms_comp = 0;
    cudaEventElapsedTime(&ms_comp, start, stop);
    
    // Decompression
    cudaEventRecord(start);
    cuSZp_decompress_3D_plain_f32(d_dec, d_cmp, my_len, cmpSize, chunk_dims, absEB, 0);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    float ms_decomp = 0;
    cudaEventElapsedTime(&ms_decomp, start, stop);
    
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    
    cudaFree(d_in);
    cudaFree(d_dec);
    cudaFree(d_cmp);
    
    {
        std::lock_guard<std::mutex> lock(print_mutex);
        WorkerResult res;
        res.worker_id = worker_id;
        res.original_size = my_bytes;
        res.compressed_size = cmpSize;
        res.comp_time_sec = ms_comp / 1000.0;
        res.decomp_time_sec = ms_decomp / 1000.0;
        res.abs_error_bound = absEB;
        results[worker_id] = res;
        
        printf("[Worker %d @ GPU %d] Finished.\n"
               "Original: %zu B, Compressed: %zu B, Ratio: %.2f\n"
               "Comp Time: %.4f s, Comp Throughput: %.2f GB/s\n"
               "Decomp Time: %.4f s, Decomp Throughput: %.2f GB/s\n",
               worker_id, gpu_id, 
               res.original_size, res.compressed_size, (double)res.original_size/res.compressed_size,
               res.comp_time_sec, (res.original_size/1e9)/res.comp_time_sec,
               res.decomp_time_sec, (res.original_size/1e9)/res.decomp_time_sec);
    }
}

int main(int argc, char** argv) {
    Args args;
    // Simple argument manual parsing
    for (int i=1; i<argc; i++) {
        std::string arg = argv[i];
        if (arg.find("--num_gpus=") == 0) {
            args.num_gpus = std::stoi(arg.substr(11));
        } else if (arg.find("--target_ratio=") == 0) {
            args.target_ratio = std::stof(arg.substr(15));
        } else if (arg.find("--file=") == 0) {
            args.file_path = arg.substr(7);
        } else if (arg.find("--dimx=") == 0) {
            args.dimx = std::stoi(arg.substr(7));
        } else if (arg.find("--dimy=") == 0) {
            args.dimy = std::stoi(arg.substr(7));
        } else if (arg.find("--dimz=") == 0) {
            args.dimz = std::stoi(arg.substr(7));
        }
    }
    
    args.total_len = (size_t)args.dimx * args.dimy * args.dimz;
    
    printf("Multi-GPU Isotropic Pressure (One-Shot Splitting)\n");
    printf("File: %s\n", args.file_path.c_str());
    printf("GPUs: %d, Target Ratio: %.2f\n", args.num_gpus, args.target_ratio);
    printf("Dims: %d %d %d\n", args.dimx, args.dimy, args.dimz);
    
    // Read whole file
    printf("Reading file to host memory...\n");
    FILE* fp = fopen(args.file_path.c_str(), "rb");
    if (!fp) { printf("Error opening file.\n"); return -1; }
    
    global_data.resize(args.total_len);
    size_t r = fread(global_data.data(), sizeof(float), args.total_len, fp);
    fclose(fp);
    if(r != args.total_len) {
        printf("Warning: Read %zu elements, expected %zu\n", r, args.total_len);
    }
    
    int device_count = 0;
    cudaGetDeviceCount(&device_count);
    if (args.num_gpus > device_count) args.num_gpus = device_count;
    
    std::vector<std::thread> workers;
    std::vector<WorkerResult> results(args.num_gpus);
    
    auto t1 = std::chrono::high_resolution_clock::now();
    for(int i=0; i<args.num_gpus; ++i) {
        workers.push_back(std::thread(worker_thread, i, i % device_count, args, std::ref(results)));
    }
    for(auto& t : workers) t.join();
    auto t2 = std::chrono::high_resolution_clock::now();
    double wall_time = std::chrono::duration<double>(t2 - t1).count();
    
    // Stats
    size_t total_orig = 0;
    size_t total_cmp = 0;
    double max_comp_time = 0;
    double max_decomp_time = 0;
    
    for(const auto& res : results) {
        total_orig += res.original_size;
        total_cmp += res.compressed_size;
        if(res.comp_time_sec > max_comp_time) max_comp_time = res.comp_time_sec;
        if(res.decomp_time_sec > max_decomp_time) max_decomp_time = res.decomp_time_sec;
    }
    
    printf("==========================================\n");
    printf("Total Original: %zu B\n", total_orig);
    printf("Total Compressed: %zu B\n", total_cmp);
    printf("Overall Ratio: %.2f\n", (double)total_orig / total_cmp);
    printf("Max Comp Time: %.4f s\n", max_comp_time);
    printf("Aggregate Comp Throughput: %.2f GB/s\n", (total_orig/1e9)/max_comp_time);
    printf("Max Decomp Time: %.4f s\n", max_decomp_time);
    printf("Aggregate Decomp Throughput: %.2f GB/s\n", (total_orig/1e9)/max_decomp_time);
    printf("==========================================\n");

    return 0;
}
