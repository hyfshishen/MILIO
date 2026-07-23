#include "cuSZp_entry_1D_f32.h"
#include "cuSZp_kernels_1D_f32.h"
#include <vector>
#include <cstdio>  // or <stdio.h>



void cuSZp_profile_1D_plain_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float range, int sample_rate,cudaStream_t stream)
{
    // Data blocking.
    int bsize = tblock_size; // 32 thread per tblock 


    int total_blocks    = (nbEle + 31) / 32; // how many data block we need  in total                    
    int sample_per_eb   = total_blocks / sample_rate; // how many data block we need for sample
    int stride          = total_blocks / sample_per_eb; // stride for each error bound
    // printf("Total datablocks %d \n",total_blocks);
    // printf("sample_per_eb %d \n",sample_per_eb);
    // printf("stides %d \n",stride);
    int gsize = sample_per_eb;
    int cmpOffSize = (gsize + 1)*32; 
    uint4* d_cmpOffset;
    uint4* d_locOffset;
    int* d_flag;
    //unsigned int glob_sync;
    cudaMalloc((void**)&d_cmpOffset, sizeof(uint4)*cmpOffSize);
    cudaMemset(d_cmpOffset, 0, sizeof(uint4)*cmpOffSize);
    cudaMalloc((void**)&d_locOffset, sizeof(uint4)*cmpOffSize);
    cudaMemset(d_locOffset, 0, sizeof(uint4)*cmpOffSize);
    cudaMalloc((void**)&d_flag, sizeof(int)*cmpOffSize);
    cudaMemset(d_flag, 0, sizeof(int)*cmpOffSize);

    // cuSZp GPU compression.
    dim3 blockSize(bsize);
    dim3 gridSize(gsize);



    //cuSZp_Profiling_kernel_1D_f32<<<gridSize, blockSize, sizeof(unsigned int)*2, stream>>>(d_oriData, d_cmpBytes, d_cmpOffset, d_locOffset, d_flag, nbEle, stride, range);
    cuSZp_Profiling_kernel_iter_1D_f32<<<gridSize, blockSize, sizeof(unsigned int)*2, stream>>>(d_oriData, d_cmpBytes, d_cmpOffset, d_locOffset, d_flag, nbEle, stride, range);
    //cuSZp_Profiling_kernel_iter_1D_outlier_f32<<<gridSize, blockSize, sizeof(unsigned int)*2, stream>>>(d_oriData, d_cmpBytes, d_cmpOffset, d_locOffset, d_flag, nbEle, stride, range);
    cudaStreamSynchronize(stream);
    
    const int final_row_idx  = gsize; 
    uint4 h_final_row[32];
    cudaError_t cuerr = cudaMemcpy(h_final_row,
                                d_cmpOffset + static_cast<size_t>(final_row_idx) * 32,
                                sizeof(h_final_row),
                                cudaMemcpyDeviceToHost);  
                                
    // float host_ebs_128[128] = {
    // // 1e-1 to 5e-2 range
    // 1e-1f, 9.7e-2f, 9.4e-2f, 9.1e-2f, 8.8e-2f, 8.5e-2f, 8.2e-2f, 7.9e-2f,
    // 7.6e-2f, 7.3e-2f, 7.0e-2f, 6.7e-2f, 6.4e-2f, 6.1e-2f, 5.8e-2f, 5.5e-2f,

    // // 5e-2 to 1e-2 range
    // 5.2e-2f, 4.9e-2f, 4.6e-2f, 4.3e-2f, 4.0e-2f, 3.7e-2f, 3.4e-2f, 3.1e-2f,
    // 2.8e-2f, 2.5e-2f, 2.2e-2f, 1.9e-2f, 1.6e-2f, 1.3e-2f, 1.1e-2f, 1e-2f,

    // // 1e-2 to 5e-3 range
    // 9.7e-3f, 9.4e-3f, 9.1e-3f, 8.8e-3f, 8.5e-3f, 8.2e-3f, 7.9e-3f, 7.6e-3f,
    // 7.3e-3f, 7.0e-3f, 6.7e-3f, 6.4e-3f, 6.1e-3f, 5.8e-3f, 5.5e-3f, 5.2e-3f,

    // // 5e-3 to 1e-3 range
    // 4.9e-3f, 4.6e-3f, 4.3e-3f, 4.0e-3f, 3.7e-3f, 3.4e-3f, 3.1e-3f, 2.8e-3f,
    // 2.5e-3f, 2.2e-3f, 1.9e-3f, 1.6e-3f, 1.3e-3f, 1.1e-3f, 1.05e-3f, 1e-3f,

    // // 1e-3 to 5e-4 range
    // 9.7e-4f, 9.4e-4f, 9.1e-4f, 8.8e-4f, 8.5e-4f, 8.2e-4f, 7.9e-4f, 7.6e-4f,
    // 7.3e-4f, 7.0e-4f, 6.7e-4f, 6.4e-4f, 6.1e-4f, 5.8e-4f, 5.5e-4f, 5.2e-4f,

    // // 5e-4 to 1e-4 range
    // 4.9e-4f, 4.6e-4f, 4.3e-4f, 4.0e-4f, 3.7e-4f, 3.4e-4f, 3.1e-4f, 2.8e-4f,
    // 2.5e-4f, 2.2e-4f, 1.9e-4f, 1.6e-4f, 1.3e-4f, 1.1e-4f, 1.05e-4f, 1e-4f,

    // // 1e-4 to 1e-6 range
    // 9.7e-5f, 9.4e-5f, 9.1e-5f, 8.8e-5f, 8.5e-5f, 8.2e-5f, 7.9e-5f, 7.6e-5f,
    // 7.3e-5f, 7.0e-5f, 6.7e-5f, 6.4e-5f, 6.1e-5f, 5.8e-5f, 5.5e-5f, 5.2e-5f,
    // 5.0e-5f, 4.5e-5f, 4.0e-5f, 3.5e-5f, 3.0e-5f, 2.5e-5f, 2.0e-5f, 1.5e-5f,
    // 1.0e-5f, 9.0e-6f, 8.0e-6f, 5.0e-6f, 4.0e-6f, 3.0e-6f, 2.00e-6f, 1e-6f
    // };

    cudaMemcpy(/*dst=*/d_cmpBytes,
                /*src=*/d_cmpOffset + (size_t)final_row_idx * 32,
                /*bytes=*/sizeof(uint4) * 32,
                cudaMemcpyDeviceToDevice);
    *cmpSize = sizeof(uint4) * 32;
    



    // const std::size_t cmpDataSize = static_cast<std::size_t>(sample_per_eb) * 32;
    // std::vector<uint4> h_cmpData(cmpDataSize);
    // const std::size_t orig_bytes_block = 32 * sizeof(float);  
    // const std::size_t total_orig       = orig_bytes_block * sample_per_eb;
    // int bytes_per_eb[128] = {0};
    // for (int lane = 0; lane < 32; ++lane) {
    //     const uint4 q = h_final_row[lane];
    //     const int base = lane * 4;
    //     bytes_per_eb[base + 0] = q.x;
    //     bytes_per_eb[base + 1] = q.y;
    //     bytes_per_eb[base + 2] = q.z;
    //     bytes_per_eb[base + 3] = q.w;
    // }
    // printf("\n======= cuSZp Profiling Result =======\n");
    // printf("total_warps = %d, final_row_idx = %d\n", final_row_idx, final_row_idx);
    // printf("--------------------------------------\n");
    // printf("EB-idx    EB        bytes        ratio\n");
    // printf("--------------------------------------\n");
    // for (int i = 0; i < 128; ++i) {
    //     const double ratio = (bytes_per_eb[i] == 0)
    //         ? 0.0
    //         : static_cast<double>(total_orig) / static_cast<double>(bytes_per_eb[i]);
    //     printf("%3d    %9.3e   %10llu   %8.3f\n",
    //         i,
    //         static_cast<double>(host_ebs_128[i]),
    //         static_cast<unsigned long long>(bytes_per_eb[i]),
    //         ratio);
    // }
    // printf("--------------------------------------\n\n");
    


    // cudaFree(d_cmpOffset);
    // cudaFree(d_locOffset);
    // cudaFree(d_flag);
    

}


/** ************************************************************************
 * @brief cuSZp end-to-end compression API for device pointers
 *        Compression is executed in GPU.
 *        Original data is stored as device pointers (in GPU).
 *        Compressed data is stored back as device pointers (in GPU).
 * 
 * @param   d_oriData       original data (device pointer)
 * @param   d_cmpBytes      compressed data (device pointer)
 * @param   nbEle           original data size (number of floating point)
 * @param   cmpSize         compressed data size (number of unsigned char)
 * @param   errorBound      user-defined error bound
 * @param   stream          CUDA stream for executing compression kernel
 * *********************************************************************** */
void cuSZp_compress_1D_plain_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float errorBound, cudaStream_t stream)
{
    // Data blocking.
    int bsize = tblock_size;
    int gsize = (nbEle + bsize * thread_chunk - 1) / (bsize * thread_chunk);
    int cmpOffSize = gsize + 1;

    // Initializing global memory for GPU compression.
    unsigned int* d_cmpOffset;
    unsigned int* d_locOffset;
    int* d_flag;
    unsigned int glob_sync;
    cudaMalloc((void**)&d_cmpOffset, sizeof(unsigned int)*cmpOffSize);
    cudaMemset(d_cmpOffset, 0, sizeof(unsigned int)*cmpOffSize);
    cudaMalloc((void**)&d_locOffset, sizeof(unsigned int)*cmpOffSize);
    cudaMemset(d_locOffset, 0, sizeof(unsigned int)*cmpOffSize);
    cudaMalloc((void**)&d_flag, sizeof(int)*cmpOffSize);
    cudaMemset(d_flag, 0, sizeof(int)*cmpOffSize);

    // cuSZp GPU compression.
    dim3 blockSize(bsize);
    dim3 gridSize(gsize);
    cuSZp_compress_kernel_1D_plain_f32<<<gridSize, blockSize, sizeof(unsigned int)*2, stream>>>(d_oriData, d_cmpBytes, d_cmpOffset, d_locOffset, d_flag, errorBound, nbEle);

    // Obtain compression ratio and move data back to CPU.  
    cudaMemcpy(&glob_sync, d_cmpOffset+cmpOffSize-1, sizeof(unsigned int), cudaMemcpyDeviceToHost);
    *cmpSize = (size_t)glob_sync + (nbEle+tblock_size*thread_chunk-1)/(tblock_size*thread_chunk)*(tblock_size*thread_chunk)/32;

    // Free memory that is used.
    cudaFree(d_cmpOffset);
    cudaFree(d_locOffset);
    cudaFree(d_flag);
}

 /** ************************************************************************
 * @brief cuSZp end-to-end decompression API for device pointers
 *        Decompression is executed in GPU.
 *        Compressed data is stored as device pointers (in GPU).
 *        Reconstructed data is stored as device pointers (in GPU).
 *        P.S. Reconstructed data and original data have the same shape.
 * 
 * @param   d_decData       reconstructed data (device pointer)
 * @param   d_cmpBytes      compressed data (device pointer)
 * @param   nbEle           reconstructed data size (number of floating point)
 * @param   cmpSize         compressed data size (number of unsigned char)
 * @param   errorBound      user-defined error bound
 * @param   stream          CUDA stream for executing compression kernel
 * *********************************************************************** */
void cuSZp_decompress_1D_plain_f32(float* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float errorBound, cudaStream_t stream)
{
    // Data blocking.
    int bsize = tblock_size;
    int gsize = (nbEle + bsize * thread_chunk - 1) / (bsize * thread_chunk);
    int cmpOffSize = gsize + 1;

    // Initializing global memory for GPU decompression.
    unsigned int* d_cmpOffset;
    unsigned int* d_locOffset;
    int* d_flag;
    cudaMalloc((void**)&d_cmpOffset, sizeof(unsigned int)*cmpOffSize);
    cudaMemset(d_cmpOffset, 0, sizeof(unsigned int)*cmpOffSize);
    cudaMalloc((void**)&d_locOffset, sizeof(unsigned int)*cmpOffSize);
    cudaMemset(d_locOffset, 0, sizeof(unsigned int)*cmpOffSize);
    cudaMalloc((void**)&d_flag, sizeof(int)*cmpOffSize);
    cudaMemset(d_flag, 0, sizeof(int)*cmpOffSize);

    // cuSZp GPU decompression.
    dim3 blockSize(bsize);
    dim3 gridSize(gsize);
    cuSZp_decompress_kernel_1D_plain_f32<<<gridSize, blockSize, sizeof(unsigned int)*2, stream>>>(d_decData, d_cmpBytes, d_cmpOffset, d_locOffset, d_flag, errorBound, nbEle);
    
    // Free memory that is used.
    cudaFree(d_cmpOffset);
    cudaFree(d_locOffset);
    cudaFree(d_flag);
}

/** ************************************************************************
 * @brief cuSZp end-to-end compression API for device pointers
 *        Compression is executed in GPU.
 *        Original data is stored as device pointers (in GPU).
 *        Compressed data is stored back as device pointers (in GPU).
 * 
 * @param   d_oriData       original data (device pointer)
 * @param   d_cmpBytes      compressed data (device pointer)
 * @param   nbEle           original data size (number of floating point)
 * @param   cmpSize         compressed data size (number of unsigned char)
 * @param   errorBound      user-defined error bound
 * @param   stream          CUDA stream for executing compression kernel
 * *********************************************************************** */
void cuSZp_compress_1D_outlier_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float errorBound, cudaStream_t stream)
{
    // Data blocking.
    int bsize = tblock_size;
    int gsize = (nbEle + bsize * thread_chunk - 1) / (bsize * thread_chunk);
    int cmpOffSize = gsize + 1;

    // Initializing global memory for GPU compression.
    unsigned int* d_cmpOffset;
    unsigned int* d_locOffset;
    int* d_flag;
    unsigned int glob_sync;
    cudaMalloc((void**)&d_cmpOffset, sizeof(unsigned int)*cmpOffSize);
    cudaMemset(d_cmpOffset, 0, sizeof(unsigned int)*cmpOffSize);
    cudaMalloc((void**)&d_locOffset, sizeof(unsigned int)*cmpOffSize);
    cudaMemset(d_locOffset, 0, sizeof(unsigned int)*cmpOffSize);
    cudaMalloc((void**)&d_flag, sizeof(int)*cmpOffSize);
    cudaMemset(d_flag, 0, sizeof(int)*cmpOffSize);

    // cuSZp GPU compression.
    dim3 blockSize(bsize);
    dim3 gridSize(gsize);
    cuSZp_compress_kernel_1D_outlier_f32<<<gridSize, blockSize, sizeof(unsigned int)*2, stream>>>(d_oriData, d_cmpBytes, d_cmpOffset, d_locOffset, d_flag, errorBound, nbEle);

    // Obtain compression ratio and move data back to CPU.  
    cudaMemcpy(&glob_sync, d_cmpOffset+cmpOffSize-1, sizeof(unsigned int), cudaMemcpyDeviceToHost);
    *cmpSize = (size_t)glob_sync + (nbEle+tblock_size*thread_chunk-1)/(tblock_size*thread_chunk)*(tblock_size*thread_chunk)/32;

    // Free memory that is used.
    cudaFree(d_cmpOffset);
    cudaFree(d_locOffset);
    cudaFree(d_flag);
}

 /** ************************************************************************
 * @brief cuSZp end-to-end decompression API for device pointers
 *        Decompression is executed in GPU.
 *        Compressed data is stored as device pointers (in GPU).
 *        Reconstructed data is stored as device pointers (in GPU).
 *        P.S. Reconstructed data and original data have the same shape.
 * 
 * @param   d_decData       reconstructed data (device pointer)
 * @param   d_cmpBytes      compressed data (device pointer)
 * @param   nbEle           reconstructed data size (number of floating point)
 * @param   cmpSize         compressed data size (number of unsigned char)
 * @param   errorBound      user-defined error bound
 * @param   stream          CUDA stream for executing compression kernel
 * *********************************************************************** */
void cuSZp_decompress_1D_outlier_f32(float* d_decData, unsigned char* d_cmpBytes, size_t nbEle, size_t cmpSize, float errorBound, cudaStream_t stream)
{
    // Data blocking.
    int bsize = tblock_size;
    int gsize = (nbEle + bsize * thread_chunk - 1) / (bsize * thread_chunk);
    int cmpOffSize = gsize + 1;

    // Initializing global memory for GPU decompression.
    unsigned int* d_cmpOffset;
    unsigned int* d_locOffset;
    int* d_flag;
    cudaMalloc((void**)&d_cmpOffset, sizeof(unsigned int)*cmpOffSize);
    cudaMemset(d_cmpOffset, 0, sizeof(unsigned int)*cmpOffSize);
    cudaMalloc((void**)&d_locOffset, sizeof(unsigned int)*cmpOffSize);
    cudaMemset(d_locOffset, 0, sizeof(unsigned int)*cmpOffSize);
    cudaMalloc((void**)&d_flag, sizeof(int)*cmpOffSize);
    cudaMemset(d_flag, 0, sizeof(int)*cmpOffSize);

    // cuSZp GPU decompression.
    dim3 blockSize(bsize);
    dim3 gridSize(gsize);
    cuSZp_decompress_kernel_1D_outlier_f32<<<gridSize, blockSize, sizeof(unsigned int)*2, stream>>>(d_decData, d_cmpBytes, d_cmpOffset, d_locOffset, d_flag, errorBound, nbEle);
    
    cudaFree(d_cmpOffset);
    cudaFree(d_locOffset);
    cudaFree(d_flag);
}

void cuSZp_profile_1D_outlier_f32(float* d_oriData, unsigned char* d_cmpBytes, size_t nbEle, size_t* cmpSize, float range, int sample_rate,cudaStream_t stream)
{
    // Data blocking.
    int bsize = tblock_size; // 32 thread per tblock 

    int total_blocks    = (nbEle + 31) / 32; // how many data block we need  in total                    
    int sample_per_eb   = total_blocks / sample_rate; // how many data block we need for sample
    int stride          = total_blocks / sample_per_eb; // stride for each error bound
    int gsize = sample_per_eb;
    int cmpOffSize = (gsize + 1)*32; 
    uint4* d_cmpOffset;
    uint4* d_locOffset;
    int* d_flag;
    //unsigned int glob_sync;
    cudaMalloc((void**)&d_cmpOffset, sizeof(uint4)*cmpOffSize);
    cudaMemset(d_cmpOffset, 0, sizeof(uint4)*cmpOffSize);
    cudaMalloc((void**)&d_locOffset, sizeof(uint4)*cmpOffSize);
    cudaMemset(d_locOffset, 0, sizeof(uint4)*cmpOffSize);
    cudaMalloc((void**)&d_flag, sizeof(int)*cmpOffSize);
    cudaMemset(d_flag, 0, sizeof(int)*cmpOffSize);

    // cuSZp GPU compression.
    dim3 blockSize(bsize);
    dim3 gridSize(gsize);

    // Use Outlier Kernel
    cuSZp_Profiling_kernel_iter_1D_outlier_f32<<<gridSize, blockSize, sizeof(unsigned int)*2, stream>>>(d_oriData, d_cmpBytes, d_cmpOffset, d_locOffset, d_flag, nbEle, stride, range);
    cudaStreamSynchronize(stream);
    
    const int final_row_idx  = gsize; 
    
    cudaMemcpy(/*dst=*/d_cmpBytes,
                /*src=*/d_cmpOffset + (size_t)final_row_idx * 32,
                /*bytes=*/sizeof(uint4) * 32,
                cudaMemcpyDeviceToDevice);
    *cmpSize = sizeof(uint4) * 32;

    cudaFree(d_cmpOffset);
    cudaFree(d_locOffset);
    cudaFree(d_flag);
}


