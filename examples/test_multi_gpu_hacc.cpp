// test_multi_gpu_hacc.cpp
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <thread>
#include <mutex>
#include <string>
#include <iostream>
#include <cmath>
#include <cuda_runtime.h>
#include "cuSZp.h"
#include "cuSZp/cuSZp_entry_1D_f32.h" // For decompression

struct Args {
    int num_gpus = 4;
    float target_ratio = 8.0f;
};

struct WorkerResult {
    int worker_id;
    size_t original_size;
    size_t compressed_size;
    float comp_time_sec;
    float decomp_time_sec;
    float abs_error_bound;
};

std::mutex cout_mutex;

// Helper function to split data (assuming 1D splitting for HACC)
void get_block_1d(const std::vector<float>& global_data, 
                  int block_id, int num_blocks, 
                  std::vector<float>& local_data_out) 
{
    size_t total_elements = global_data.size();
    size_t elems_per_block = total_elements / num_blocks;
    size_t remainder = total_elements % num_blocks;
    
    size_t start_idx = block_id * elems_per_block + (block_id < remainder ? block_id : remainder);
    size_t my_count = elems_per_block + (block_id < remainder ? 1 : 0);
    
    local_data_out.resize(my_count);
    std::copy(global_data.begin() + start_idx, 
              global_data.begin() + start_idx + my_count, 
              local_data_out.begin());
}

void worker_thread(int worker_id, int gpu_id, Args args, const std::vector<float>& global_data, std::vector<WorkerResult>& results) {
    cudaSetDevice(gpu_id);
    
    std::vector<float> local_data;
    get_block_1d(global_data, worker_id, args.num_gpus, local_data);
    
    size_t nbEle = local_data.size();
    size_t size_bytes = nbEle * sizeof(float);
    
    // Determine range
    float min_val = local_data[0];
    float max_val = local_data[0];
    for (float v : local_data) {
        if (v < min_val) min_val = v;
        if (v > max_val) max_val = v;
    }
    float range = max_val - min_val;
    if (range <= 0) range = 1.0f;
    
    // Alloc GPU resources
    float* d_in = nullptr;
    float* d_dec = nullptr;
    unsigned char* d_cmp = nullptr;
    size_t cmpSize = 0;
    
    cudaMalloc(&d_in, size_bytes);
    cudaMalloc(&d_dec, size_bytes);
    cudaMalloc(&d_cmp, size_bytes * 1.5);
    cudaMemcpy(d_in, local_data.data(), size_bytes, cudaMemcpyHostToDevice);
    
    // Warmup (10 iterations)
    {
        std::lock_guard<std::mutex> lock(cout_mutex);
        // std::cout << "[Worker " << worker_id << "] Warming up..." << std::endl;
    }
    size_t warmup_cmpSize = 0;
    for(int k=0; k<10; k++) {
        cuSZp_fixed_ratio(d_in, d_cmp, nbEle, &warmup_cmpSize, range, 1000, args.target_ratio);
    }
    
    cudaDeviceSynchronize();
    
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    
    // Compression
    cudaEventRecord(start);
    float absEB = cuSZp_fixed_ratio(d_in, d_cmp, nbEle, &cmpSize, range, 1000, args.target_ratio);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    
    float ms_comp = 0;
    cudaEventElapsedTime(&ms_comp, start, stop);
    
    // Decompression (Assuming PLAIN mode for fixed ratio - usually the default)
    cudaEventRecord(start);
    cuSZp_decompress_1D_plain_f32(d_dec, d_cmp, nbEle, cmpSize, absEB);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    
    float ms_decomp = 0;
    cudaEventElapsedTime(&ms_decomp, start, stop);
    
    {
        std::lock_guard<std::mutex> lock(cout_mutex);
        WorkerResult res;
        res.worker_id = worker_id;
        res.original_size = size_bytes;
        res.compressed_size = cmpSize;
        res.comp_time_sec = ms_comp / 1000.0f;
        res.decomp_time_sec = ms_decomp / 1000.0f;
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
    
    cudaFree(d_in);
    cudaFree(d_dec);
    cudaFree(d_cmp);
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
}

int main(int argc, char** argv) {
    Args args;
    for (int i=1; i<argc; i++) {
        std::string arg = argv[i];
        if (arg.find("--num_gpus=") == 0) {
            args.num_gpus = std::stoi(arg.substr(11));
        } else if (arg.find("--target_ratio=") == 0) {
            args.target_ratio = std::stof(arg.substr(15));
        }
    }
    
    const char* file_path = "/scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vy.f32";
    printf("Multi-GPU HACC Test (Measured Decompression)\n");
    printf("Reading file: %s\n", file_path);
    printf("GPUs: %d, Target Ratio: %.2f\n", args.num_gpus, args.target_ratio);
    
    FILE* fp = fopen(file_path, "rb");
    if (!fp) {
        printf("Error: Cannot open file.\n");
        return -1;
    }
    fseek(fp, 0, SEEK_END);
    size_t file_size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    size_t total_ele = file_size / sizeof(float);
    printf("File size: %zu B, Elements: %zu\n", file_size, total_ele);
    
    std::vector<float> global_data(total_ele);
    size_t read_count = fread(global_data.data(), sizeof(float), total_ele, fp);
    fclose(fp);
    if(read_count != total_ele) {
        printf("Read error.\n");
        return -1;
    }
    
    int device_count = 0;
    cudaGetDeviceCount(&device_count);
    if (device_count == 0) return -1;
    if (args.num_gpus > device_count) {
        printf("Warning: Requested %d GPUs but only %d available. Limiting to %d.\n", args.num_gpus, device_count, device_count);
        args.num_gpus = device_count;
    }

    std::vector<std::thread> workers;
    std::vector<WorkerResult> results(args.num_gpus);
    
    auto t1 = std::chrono::high_resolution_clock::now();
    
    for(int i=0; i<args.num_gpus; ++i) {
        workers.push_back(std::thread(worker_thread, i, i, args, std::ref(global_data), std::ref(results)));
    }
    
    for(auto& t : workers) t.join();
    
    auto t2 = std::chrono::high_resolution_clock::now();
    double total_wall_time = std::chrono::duration<double>(t2 - t1).count();
    
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
