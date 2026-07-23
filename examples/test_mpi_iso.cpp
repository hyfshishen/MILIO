#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <iostream>
#include <cmath>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <cuda_runtime.h>
#include <mpi.h>
#include "cuSZp.h"
#include "cuSZp/cuSZp_entry_3D_f32.h"

struct Args {
    float target_ratio = 8.0f;
    std::string file_path = "/scratch/bfrq/bzhang28/isotropic_pressure_4096x4096x4096_float32.raw";
    uint3 global_dims = {4096, 4096, 4096};
    int batch_z = 32; // Safe batch size
};

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    Args args;
    for (int i=1; i<argc; i++) {
        std::string arg = argv[i];
        if (arg.find("--target_ratio=") == 0) {
            args.target_ratio = std::stof(arg.substr(15));
        }
        else if (arg.find("--file=") == 0) {
            args.file_path = arg.substr(7);
        }
    }

    if (rank == 0) {
        printf("MPI Multi-GPU Isotropic Pressure (3D) Test\n");
        printf("Total Ranks (GPUs): %d\n", size);
        printf("File: %s\n", args.file_path.c_str());
        printf("Dimensions: %u x %u x %u\n", args.global_dims.x, args.global_dims.y, args.global_dims.z);
        printf("Target Ratio: %.2f\n", args.target_ratio);
    }

    // 1. Assign GPU to Rank
    // Assume 1 Rank per GPU.
    // We need to determine local GPU ID.
    // On Slurm with --gpus-per-task or similar, CUDA_VISIBLE_DEVICES might be set.
    // Or we rely on local rank (rank within node).
    
    // Safer way used in HPC:
    MPI_Comm local_comm;
    MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, rank, MPI_INFO_NULL, &local_comm);
    int local_rank;
    MPI_Comm_rank(local_comm, &local_rank);
    
    int device_count = 0;
    cudaGetDeviceCount(&device_count);
    int gpu_id = local_rank % device_count;
    cudaSetDevice(gpu_id);

    // 2. Data Partitioning (Z-slice based)
    int total_z = args.global_dims.z;
    int slices_per_rank = total_z / size;
    int start_z = rank * slices_per_rank;
    int my_slices = slices_per_rank;
    
    // Handle remainder
    int remainder = total_z % size;
    if (rank < remainder) {
        my_slices++;
        start_z = rank * my_slices;
    } else {
        start_z = rank * slices_per_rank + remainder;
    }

    size_t slice_elements = (size_t)args.global_dims.x * args.global_dims.y;
    size_t slice_bytes = slice_elements * sizeof(float);
    size_t my_total_bytes = (size_t)my_slices * slice_bytes;

    // 3. File I/O
    // Using MPI-IO for reading
    MPI_File fh;
    int err = MPI_File_open(MPI_COMM_WORLD, args.file_path.c_str(), MPI_MODE_RDONLY, MPI_INFO_NULL, &fh);
    if (err) {
        printf("[Rank %d] Error opening file.\n", rank);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    // 4. Processing Loop
    // Allocate GPU buffers (max batch size)
    float* d_in = nullptr;
    float* d_dec = nullptr;
    unsigned char* d_cmp = nullptr;
    
    size_t max_batch_ele = (size_t)args.batch_z * slice_elements;
    size_t max_batch_bytes = max_batch_ele * sizeof(float);
    
    cudaMalloc(&d_in, max_batch_bytes);
    cudaMalloc(&d_dec, max_batch_bytes);
    cudaMalloc(&d_cmp, max_batch_bytes * 1.5);
    
    std::vector<float> h_buffer(max_batch_ele);
    
    double total_comp_time = 0;
    double total_decomp_time = 0;
    size_t total_orig_size = 0;
    size_t total_cmp_size = 0;
    
    // Barrier before timing
    MPI_Barrier(MPI_COMM_WORLD);
    double t_start = MPI_Wtime();

    for (int current_z = 0; current_z < my_slices; current_z += args.batch_z) {
        int actual_batch_z = std::min(args.batch_z, my_slices - current_z);
        size_t batch_bytes = (size_t)actual_batch_z * slice_bytes;
        size_t batch_ele = (size_t)actual_batch_z * slice_elements;
        
        // Read at offset
        MPI_Offset offset = (MPI_Offset)(start_z + current_z) * slice_bytes;
        MPI_Status status;
        MPI_File_read_at(fh, offset, h_buffer.data(), batch_bytes, MPI_BYTE, &status);
        
        // H2D
        cudaMemcpy(d_in, h_buffer.data(), batch_bytes, cudaMemcpyHostToDevice);
        
        // Range
        float min_val = h_buffer[0];
        float max_val = h_buffer[0];
        // Simple range sampling to save CPU time? No, do full scan for correctness.
        // Or construct optimized checking.
        for(size_t k=0; k<batch_ele; k++) {
           if(h_buffer[k] < min_val) min_val = h_buffer[k];
           if(h_buffer[k] > max_val) max_val = h_buffer[k];
        }
        float range = max_val - min_val;
        if(range <= 0) range = 1.0f;
        
        // Run cuSZp
        size_t cmpSize = 0;
        uint3 batch_dims = make_uint3(args.global_dims.x, args.global_dims.y, actual_batch_z);
        
        // Warmup (first batch only)
        if (current_z == 0 && rank == 0) {
             printf("Rank 0 warming up...\n");
             size_t w_sz;
             // CUSZP_MODE_PLAIN assumed for default behavior in this test
             cuSZp_fixed_ratio_3D(d_in, d_cmp, batch_ele, &w_sz, batch_dims, range, 500, args.target_ratio, CUSZP_MODE_PLAIN, 0);
        }

        cudaEvent_t START, STOP;
        cudaEventCreate(&START); cudaEventCreate(&STOP);
        
        cudaEventRecord(START);
        float absEB = cuSZp_fixed_ratio_3D(d_in, d_cmp, batch_ele, &cmpSize, batch_dims, range, 1000, args.target_ratio, CUSZP_MODE_PLAIN, 0);
        cudaEventRecord(STOP);
        cudaEventSynchronize(STOP);
        float ms = 0;
        cudaEventElapsedTime(&ms, START, STOP);
        total_comp_time += (ms/1000.0);
        
        // Decompress
        cudaEventRecord(START);
        cuSZp_decompress_3D_plain_f32(d_dec, d_cmp, batch_ele, cmpSize, batch_dims, absEB, 0);
        cudaEventRecord(STOP);
        cudaEventSynchronize(STOP);
        float ms_dec = 0;
        cudaEventElapsedTime(&ms_dec, START, STOP);
        total_decomp_time += (ms_dec/1000.0);
        
        cudaEventDestroy(START);
        cudaEventDestroy(STOP);
        
        total_orig_size += batch_bytes;
        total_cmp_size += cmpSize;
    }
    
    MPI_File_close(&fh);
    cudaFree(d_in);
    cudaFree(d_dec);
    cudaFree(d_cmp);
    
    // Aggregate Results
    MPI_Barrier(MPI_COMM_WORLD);
    double t_end = MPI_Wtime();
    double total_wall_time = t_end - t_start;
    
    // Reduce stats
    size_t global_orig = 0;
    size_t global_cmp = 0;
    double global_max_comp_time = 0;
    
    MPI_Reduce(&total_orig_size, &global_orig, 1, MPI_UNSIGNED_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);
    MPI_Reduce(&total_cmp_size, &global_cmp, 1, MPI_UNSIGNED_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);
    MPI_Reduce(&total_comp_time, &global_max_comp_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    
    if (rank == 0) {
        printf("==========================================\n");
        printf("Wall Time: %.4f s\n", total_wall_time);
        printf("Total Original: %zu B\n", global_orig);
        printf("Total Compressed: %zu B\n", global_cmp);
        printf("Ratio: %.2f\n", (double)global_orig/global_cmp);
        printf("Max Comp Time (Pure Kernel): %.4f s\n", global_max_comp_time);
        printf("Throughput (Pure Kernel): %.2f GB/s\n", (global_orig/1e9)/global_max_comp_time);
        printf("Throughput (End-to-End): %.2f GB/s\n", (global_orig/1e9)/total_wall_time);
        printf("==========================================\n");
    }

    MPI_Finalize();
    return 0;
}
