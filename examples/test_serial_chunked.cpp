// test_serial_chunked.cpp
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <iostream>
#include <cuda_runtime.h>
#include "cuSZp.h"

// Reusing helper logic from test_multi_gpu_framework.cpp (inline for simplicity)
void get_block(const std::vector<float>& global_data, 
               int block_id, int num_blocks, 
               uint3 global_dims,
               std::vector<float>& local_data_out,
               uint3& local_dims_out) 
{
    size_t total_elements = (size_t)global_dims.x * global_dims.y * global_dims.z;
    size_t elems_per_block = total_elements / num_blocks;
    size_t remainder = total_elements % num_blocks;
    
    size_t start_idx = block_id * elems_per_block + (block_id < remainder ? block_id : remainder);
    size_t my_count = elems_per_block + (block_id < remainder ? 1 : 0);
    
    local_data_out.resize(my_count);
    // Copy data
    std::copy(global_data.begin() + start_idx, 
              global_data.begin() + start_idx + my_count, 
              local_data_out.begin());
              
    if (global_dims.z > 1) {
        // 3D Split along Z
        int slices_per_block = global_dims.z / num_blocks;
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
    }
}

int main(int argc, char** argv) {
    int num_chunks = 4;
    float target_ratio = 8.0f;
    // Read Data from File
    const char* file_path = "/scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vy.f32";
    printf("Reading file: %s\n", file_path);
    
    FILE* fp = fopen(file_path, "rb");
    if (!fp) {
        printf("Error: Cannot open file %s\n", file_path);
        return -1;
    }
    
    fseek(fp, 0, SEEK_END);
    size_t file_size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    
    size_t total_ele = file_size / sizeof(float);
    printf("File size: %zu bytes, Elements: %zu\n", file_size, total_ele);
    
    // Update global_dims to be 1D
    uint3 global_dims = make_uint3(total_ele, 1, 1);
    
    std::vector<float> global_data(total_ele);
    size_t read_count = fread(global_data.data(), sizeof(float), total_ele, fp);
    if (read_count != total_ele) {
        printf("Error: Read mismatch. Expected %zu, got %zu\n", total_ele, read_count);
        fclose(fp);
        return -1;
    }
    fclose(fp);
    
    // Check GPU
    int device_count = 0;
    cudaGetDeviceCount(&device_count);
    if (device_count == 0) {
        printf("Error: No CUDA devices found.\n");
        return -1;
    }
    cudaSetDevice(0);
    
    size_t total_orig = 0;
    size_t total_cmp = 0;

    // Warmup
    {
        printf("Warming up GPU...\n");
        std::vector<float> warmup_data;
        uint3 warmup_dims;
        get_block(global_data, 0, num_chunks, global_dims, warmup_data, warmup_dims);
        size_t w_nbEle = warmup_data.size();
        size_t w_size_bytes = w_nbEle * sizeof(float);
        
        float* d_w_in = nullptr;
        unsigned char* d_w_cmp = nullptr;
        size_t w_cmpSize = 0;
        
        cudaMalloc(&d_w_in, w_size_bytes);
        cudaMalloc(&d_w_cmp, w_size_bytes * 1.5);
        cudaMemcpy(d_w_in, warmup_data.data(), w_size_bytes, cudaMemcpyHostToDevice);
        
        // Simple warmup call
        for(int k=0; k<10; k++)
            cuSZp_fixed_ratio(d_w_in, d_w_cmp, w_nbEle, &w_cmpSize, 1.0f, 500, target_ratio);
        
        cudaFree(d_w_in);
        cudaFree(d_w_cmp);
        printf("Warmup done.\n");
    }

    for (int i=0; i<num_chunks; ++i) {
        std::vector<float> local_data;
        uint3 local_dims;
        get_block(global_data, i, num_chunks, global_dims, local_data, local_dims);
        
        size_t nbEle = local_data.size();
        size_t size_bytes = nbEle * sizeof(float);
        
        // Range
        float min_val = local_data[0];
        float max_val = local_data[0];
        for (float v : local_data) {
            if (v < min_val) min_val = v;
            if (v > max_val) max_val = v;
        }
        float range = max_val - min_val;
        if (range <= 0) range = 1.0f;
        
        // Setup GPU
        float* d_in = nullptr;
        unsigned char* d_cmp = nullptr;
        size_t cmpSize = 0;
        
        cudaMalloc(&d_in, size_bytes);
        cudaMalloc(&d_cmp, size_bytes * 1.5);
        cudaMemcpy(d_in, local_data.data(), size_bytes, cudaMemcpyHostToDevice);
        
        // Compress
        cudaEvent_t start, stop;
        cudaEventCreate(&start);
        cudaEventCreate(&stop);
        cudaEventRecord(start);
        
        float absEB = 0.0f;
        if (local_dims.z > 1) {
            absEB = cuSZp_fixed_ratio_3D(d_in, d_cmp, nbEle, &cmpSize, local_dims, range, 1000, target_ratio);
        } else if (local_dims.y > 1) {
            absEB = cuSZp_fixed_ratio_2D(d_in, d_cmp, nbEle, &cmpSize, local_dims, range, 1000, target_ratio);
        } else {
             absEB = cuSZp_fixed_ratio(d_in, d_cmp, nbEle, &cmpSize, range, 1000, target_ratio);
        }
        
        cudaEventRecord(stop);
        cudaEventSynchronize(stop);
        float ms = 0;
        cudaEventElapsedTime(&ms, start, stop);
        
        float ratio = (float)size_bytes / cmpSize;
        // Throughput in GB/s
        float throughput = (size_bytes / 1e9) / (ms / 1000.0f);
        
        printf("[Chunk %d] Time: %.4f ms | Size: %zu -> %zu | Ratio: %.2f | Throughput: %.2f GB/s\n", 
               i, ms, size_bytes, cmpSize, ratio, throughput);
               
        total_orig += size_bytes;
        total_cmp += cmpSize;
        
        cudaFree(d_in);
        cudaFree(d_cmp);
        cudaEventDestroy(start);
        cudaEventDestroy(stop);
    }
    
    printf("==========================================\n");
    printf("Total Original Size: %zu B\n", total_orig);
    printf("Total Compressed Size: %zu B\n", total_cmp);
    printf("Overall Ratio: %.2f\n", (double)total_orig / total_cmp);
    printf("==========================================\n");

    return 0;
}
