// test_multi_gpu_framework.cpp
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

// Command line argument structure
struct Args {
    int num_gpus = 1;
    float target_ratio = 4.0f;
    uint3 global_dims = {128, 128, 128}; // Default 2M elements
    int sample_rate = 500;
};

// Result structure for a worker
struct WorkerResult {
    int worker_id;
    size_t original_size;
    size_t compressed_size;
    float time_sec;
    float abs_error_bound;
    bool success;
};

// Helper: Calculate block dimensions/offset for Worker i
// Assume splitting along slowest dimension (Z for 3D, or just split total elements for 1D)
// For simplicity valid for 1D/2D/3D but logic below is tailored for linear split if Z=1, or Z-split if Z>1
void get_block(const std::vector<float>& global_data, 
               int block_id, int num_blocks, 
               uint3 global_dims,
               std::vector<float>& local_data_out,
               uint3& local_dims_out) 
{
    size_t total_elements = (size_t)global_dims.x * global_dims.y * global_dims.z;
    
    // Simple 1D partitioning strategy for now to support 1D/2D/3D generically
    // Each worker gets a contiguous chunk of elements.
    // For 3D, this means splitting along Z axis essentially (if dims.x/y aligned)
    
    size_t elems_per_block = total_elements / num_blocks;
    size_t remainder = total_elements % num_blocks;
    
    size_t start_idx = block_id * elems_per_block + (block_id < remainder ? block_id : remainder);
    size_t my_count = elems_per_block + (block_id < remainder ? 1 : 0);
    
    local_data_out.resize(my_count);
    // Copy data
    // In a real scenario, this would be a file read at offset.
    // Here we copy from memory.
    std::copy(global_data.begin() + start_idx, 
              global_data.begin() + start_idx + my_count, 
              local_data_out.begin());
              
    // Determine Local Dims
    // Note: cuSZp fixed ratio uses dims for blocking logic.
    // If we split linear array, we might lose 2D/3D topology context at boundaries.
    // For strict correctness in 2D/3D profile, we should split aligned to rows/slices.
    // Let's assume we split along Z for 3D, and Y for 2D. 
    
    if (global_dims.z > 1) {
        // 3D Split along Z
        int slices_per_block = global_dims.z / num_blocks;
        // Handle remainder strictly? Or just assume divisible for this proof of concept?
        // Let's handle simple cases.
        if (block_id == num_blocks - 1) {
             slices_per_block = global_dims.z - block_id * (global_dims.z / num_blocks);
        } else {
             slices_per_block = global_dims.z / num_blocks;
        }
        local_dims_out = make_uint3(global_dims.x, global_dims.y, slices_per_block);
        
        // Recalculate my_count based on exact slices
        size_t slice_size = global_dims.x * global_dims.y;
        start_idx = (size_t)block_id * (global_dims.z / num_blocks) * slice_size;
        
        my_count = slices_per_block * slice_size;
        local_data_out.resize(my_count);
        std::copy(global_data.begin() + start_idx, 
                  global_data.begin() + start_idx + my_count, 
                  local_data_out.begin());
                  
    } else if (global_dims.y > 1) {
        // 2D Split along Y
        int rows_per_block = global_dims.y / num_blocks;
        if (block_id == num_blocks - 1) {
             rows_per_block = global_dims.y - block_id * (global_dims.y / num_blocks);
        }
        local_dims_out = make_uint3(global_dims.x, rows_per_block, 1);
        
        size_t row_size = global_dims.x;
        start_idx = (size_t)block_id * (global_dims.y / num_blocks) * row_size;
        
        my_count = rows_per_block * row_size;
        local_data_out.resize(my_count);
        std::copy(global_data.begin() + start_idx, 
                  global_data.begin() + start_idx + my_count, 
                  local_data_out.begin());
    } else {
        // 1D Linear split
        local_dims_out = make_uint3(my_count, 1, 1);
        // data already copied above
    }
}


std::mutex cout_mutex;

void worker_thread(int worker_id, int gpu_id, Args args, const std::vector<float>& global_data, std::vector<WorkerResult>& results) {
    
    // 1. Bind to GPU
    cudaSetDevice(gpu_id);
    
    // 2. Get Data Block
    std::vector<float> local_data;
    uint3 local_dims;
    get_block(global_data, worker_id, args.num_gpus, args.global_dims, local_data, local_dims);
    
    size_t nbEle = local_data.size();
    size_t size_bytes = nbEle * sizeof(float);
    
    // Determine range for this block
    float min_val = local_data[0];
    float max_val = local_data[0];
    for (float v : local_data) {
        if (v < min_val) min_val = v;
        if (v > max_val) max_val = v;
    }
    float range = max_val - min_val;
    if (range <= 0) range = 1.0f;
    
    // 3. Setup CUDA Resources
    cudaStream_t stream;
    cudaStreamCreate(&stream); // Not strictly needed as APIs accept stream, but good practice
    
    float* d_in = nullptr;
    unsigned char* d_cmp = nullptr;
    size_t cmpSize = 0;
    
    cudaMalloc(&d_in, size_bytes);
    cudaMalloc(&d_cmp, size_bytes * 1.5); // buffer
    
    cudaMemcpyAsync(d_in, local_data.data(), size_bytes, cudaMemcpyHostToDevice, stream);

    // 4. Compress
    float absEB = 0.0f;
    
    // Start timing
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    cudaEventRecord(start, stream);
    
    // Dispatch based on dims (simplified)
    if (local_dims.z > 1) {
        absEB = cuSZp_fixed_ratio_3D(d_in, d_cmp, nbEle, &cmpSize, local_dims, range, args.sample_rate, args.target_ratio);
    } else if (local_dims.y > 1) {
        absEB = cuSZp_fixed_ratio_2D(d_in, d_cmp, nbEle, &cmpSize, local_dims, range, args.sample_rate, args.target_ratio);
    } else {
        // 1D
         absEB = cuSZp_fixed_ratio(d_in, d_cmp, nbEle, &cmpSize, range, args.sample_rate, args.target_ratio);
    }
    
    cudaEventRecord(stop, stream);
    cudaEventSynchronize(stop);
    float ms = 0;
    cudaEventElapsedTime(&ms, start, stop);
    
    // 5. Store Results
    {
        std::lock_guard<std::mutex> lock(cout_mutex);
        WorkerResult res;
        res.worker_id = worker_id;
        res.original_size = size_bytes;
        res.compressed_size = cmpSize; // cmpSize is bytes if we treat it as such? 
        // Note: cmpSize for cuSZp is usually bytes (sizeof(unsigned char)).
        // Verified signatures: unsigned char* d_cmpBytes.
        
        res.time_sec = ms / 1000.0f;
        res.abs_error_bound = absEB;
        res.success = true; // Assuming no crash
        
        results[worker_id] = res;
        
        std::cout << "[Worker " << worker_id << " @ GPU " << gpu_id << "] Finished."
                  << " InSize: " << size_bytes << " B"
                  << " OutSize: " << cmpSize << " B"
                  << " Ratio: " << (float)size_bytes/cmpSize
                  << " EB: " << absEB << std::endl;
    }
    
    // Cleanup
    cudaFree(d_in);
    cudaFree(d_cmp);
    cudaStreamDestroy(stream);
}

int main(int argc, char** argv) {
    // Parse args
    Args args;
    for (int i=1; i<argc; i++) {
        std::string arg = argv[i];
        if (arg.find("--num_gpus=") == 0) {
            args.num_gpus = std::stoi(arg.substr(11));
        }
        else if (arg.find("--target_ratio=") == 0) {
            args.target_ratio = std::stof(arg.substr(15));
        }
         // Add more parsing as needed
    }
    
    printf("Multi-GPU Framework Test\n");
    printf("Workers: %d\n", args.num_gpus);
    printf("Target Ratio: %.2f\n", args.target_ratio);
    
    // Generate Dummy Global Data (3D Gradient)
    size_t total_ele = args.global_dims.x * args.global_dims.y * args.global_dims.z;
    std::vector<float> global_data(total_ele);
    for(size_t i=0; i<total_ele; ++i) {
        int z = i / (args.global_dims.x * args.global_dims.y);
        int rem = i % (args.global_dims.x * args.global_dims.y);
        int y = rem / args.global_dims.x;
        int x = rem % args.global_dims.x;
        global_data[i] = (float)(x+y+z) * 0.01f;
    }
    
    std::vector<std::thread> workers;
    std::vector<WorkerResult> results(args.num_gpus);
    
    // Get visible devices
    int device_count = 0;
    cudaGetDeviceCount(&device_count);
    if (device_count == 0) {
        printf("Error: No CUDA devices found.\n");
        return -1;
    }
    
    // Spawn Workers
    for (int i=0; i<args.num_gpus; ++i) {
        int gpu_id = i % device_count; // Round robin if fewer GPUs than workers
        workers.push_back(std::thread(worker_thread, i, gpu_id, args, std::ref(global_data), std::ref(results)));
    }
    
    // Wait
    for (auto& t : workers) {
        t.join();
    }
    
    // Aggregate
    size_t total_orig = 0;
    size_t total_cmp = 0;
    for (const auto& res : results) {
        total_orig += res.original_size;
        total_cmp += res.compressed_size;
    }
    
    printf("==========================================\n");
    printf("Total Original Size: %zu B\n", total_orig);
    printf("Total Compressed Size: %zu B\n", total_cmp);
    printf("Overall Ratio: %.2f\n", (double)total_orig / total_cmp);
    printf("==========================================\n");
    
    return 0;
}
