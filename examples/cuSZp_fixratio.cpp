// main.cpp  -- fix-ratio driver (f32 + relative EB)
// build (example):
//   nvcc -O3 -std=c++17 examples/cuSZp_fixratio.cpp src/cuSZp.cu src/cuSZp_entry_1D_f32.cu src/cuSZp_entry_3D_f32.cu -I include -o cuSZp_fixratio

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#include <cmath>
#include <cctype>
#include <cuda_runtime.h>
#include "cuSZp.h"

#ifndef tblock_size
#define tblock_size 32
#endif

#define CHECK_CUDA(x) do { \
  cudaError_t err__ = (x); \
  if (err__ != cudaSuccess) { \
    fprintf(stderr, "CUDA error %s:%d: %s\n", __FILE__, __LINE__, cudaGetErrorString(err__)); \
    exit(EXIT_FAILURE); \
  } \
} while (0)


static const float PRO_128_REL_EB[128] = {
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

static void usage() {
  printf("Usage:\n");
  printf("  ./cuSZp_fixratio -i <input.f32> -R <target_ratio> [-x <dim_x>] [-y <dim_y>] [-z <dim_z>] [-o <out.cmp>] [-m <plain|outlier>] [-S <rate>]\n");
  printf("  If -y and -z are provided, runs 3D mode. Otherwise runs 1D mode.\n");
}

static void find_min_max(const float* a, size_t n, float& mn, float& mx) {
  if (n == 0) { mn = mx = 0; return; }
  mn = mx = a[0];
  for (size_t i = 1; i < n; ++i) { mn = std::min(mn, a[i]); mx = std::max(mx, a[i]); }
}

// Reconstruct bytes per EB and pick best
// For 1D, orig_per_block = 32 floats
// For 3D, orig_per_block = 64 floats (4x4x4)
// Caller must define what "total_orig" is based on padded/unpadded logic
static int pick_best_eb_from_finalrow_generic(const uint4* final_row,
                                              int sample_per_eb,
                                              double R_target,
                                              size_t orig_per_block_bytes) 
{
  const double total_orig = (double)orig_per_block_bytes * (double)sample_per_eb;

  int bytes_per_eb[128];
  for (int lane = 0; lane < 32; ++lane) {
    const uint4 q = final_row[lane];
    const int base = lane * 4;
    bytes_per_eb[base + 0] = (int)q.x;
    bytes_per_eb[base + 1] = (int)q.y;
    bytes_per_eb[base + 2] = (int)q.z;
    bytes_per_eb[base + 3] = (int)q.w;
  }

  int best = 127; 
  bool found = false;

  for (int i = 127; i >= 0; --i) {
    const int b = bytes_per_eb[i];
    if (b <= 0) { best = i; found = true; break; }
    const double ratio = total_orig / (double)b;
    if (ratio >= R_target) { best = i; found = true; break; }
  }

  if (!found) {
    int min_b = bytes_per_eb[0];
    best = 0;
    for (int i = 1; i < 128; ++i) {
      if (bytes_per_eb[i] > 0 && bytes_per_eb[i] < min_b) {
        min_b = bytes_per_eb[i];
        best = i;
      }
    }
  }
  return best;
}

int main(int argc, char** argv) {
  char* inPath = nullptr;
  char* outCmp = nullptr;
  char* outDec = nullptr;
  double targetR = 0.0;
  int sample_rate = 1000;
  cuszp_mode_t mode = CUSZP_MODE_PLAIN;
  TimingGPU timer_GPU;
  
  size_t arg_x = 0;
  size_t arg_y = 0;
  size_t arg_z = 0;
  
  for (int i = 1; i < argc; ++i) {
    if (!strcmp(argv[i], "-i") && i + 1 < argc) inPath = argv[++i];
    else if (!strcmp(argv[i], "-x") && i + 1 < argc) arg_x = atol(argv[++i]); // Optional output or dim X?
    // Wait, -x was used for out.cmp in original code? 
    // Original code: "-x <out.cmp>".
    // But standard 3D CLI uses -x -y -z for dims.
    // Let's resolve ambiguity. check original: "else if (!strcmp(argv[i], "-x") && i + 1 < argc) outCmp = argv[++i];"
    // User wants "3d input use 3d".
    // I will support BOTH. I'll use `-o <cmp>` for output compressed.
    // I'll check if `-x` looks like a number.
    else if (!strcmp(argv[i], "-x") && i + 1 < argc) {
         // Check if next arg is number
         char* next = argv[i+1];
         if (isdigit(next[0])) { arg_x = atol(argv[++i]); }
         else { outCmp = argv[++i]; }
    }
    else if (!strcmp(argv[i], "-y") && i + 1 < argc) arg_y = atol(argv[++i]);
    else if (!strcmp(argv[i], "-z") && i + 1 < argc) arg_z = atol(argv[++i]);
    else if (!strcmp(argv[i], "-c") && i + 1 < argc) outCmp = argv[++i]; // explicit flag for compressed out
    // else if (!strcmp(argv[i], "-d") && i + 1 < argc) outDec = argv[++i]; // decompression out
    
    // Legacy support for -o being DECOMPRESSED OUT or COMPRESSED?
    // Original: "-o <out.dec>".
    // I'll keep "-o" as decompressed out if user wants verification dump.
    else if (!strcmp(argv[i], "-o") && i + 1 < argc) outDec = argv[++i]; 

    else if (!strcmp(argv[i], "-R") && i + 1 < argc) targetR = atof(argv[++i]);
    else if (!strcmp(argv[i], "-S") && i + 1 < argc) sample_rate = atoi(argv[++i]);
    else if (!strcmp(argv[i], "-m") && i + 1 < argc) {
        const char* mstr = argv[++i];
        if (!strcmp(mstr, "outlier")) mode = CUSZP_MODE_OUTLIER;
        else if (!strcmp(mstr, "plain")) mode = CUSZP_MODE_PLAIN;
        else { usage(); return EXIT_FAILURE; }
    }
  }

  if (!inPath || targetR <= 0.0) { usage(); return EXIT_FAILURE; }

  int status = 0;
  size_t nbEle = 0;
  float* h_in = readFloatData_Yafan(inPath, &nbEle, &status);
  if (!h_in || status != 0 || nbEle == 0) {
    fprintf(stderr, "Failed to read input: %s\n", inPath);
    return EXIT_FAILURE;
  }

  bool is_3d = (arg_y > 1 && arg_z > 1);
  if (!is_3d && arg_x == 0) arg_x = nbEle; // 1D case

  if (is_3d) {
     if (arg_x * arg_y * arg_z != nbEle) {
         printf("Warning: Dimension mismatch %zux%zux%zu != %zu. Using file size.\n", arg_x, arg_y, arg_z, nbEle);
     }
  }

  // range for rel EB
  float mn, mx; find_min_max(h_in, nbEle, mn, mx);
  const float range = mx - mn;
  
  const size_t inBytes = nbEle * sizeof(float);
  const size_t cmpCap  = inBytes + (1u << 20); 
  float* d_in = nullptr; /* float* d_dec = nullptr; */ unsigned char* d_cmp = nullptr;
  CHECK_CUDA(cudaMalloc(&d_in,  inBytes));
  CHECK_CUDA(cudaMalloc(&d_cmp, cmpCap));
  float* d_dec = nullptr;
  CHECK_CUDA(cudaMalloc(&d_dec, inBytes));
  CHECK_CUDA(cudaMemcpy(d_in, h_in, inBytes, cudaMemcpyHostToDevice));

  cudaStream_t stream; CHECK_CUDA(cudaStreamCreate(&stream));

  size_t profBytes = 0;
  
  // --- Warmup ---
  for(int i=0; i<10; i++) {
     if (is_3d) {
         // Profiling warmup? Or just compression warmup using dummy EB?
         // Original used cuSZp_profile wrapper.
         // Let's just warmup profiling kernel.
          uint3 dims = make_uint3(arg_x, arg_y, arg_z);
          if (mode == CUSZP_MODE_PLAIN)
            cuSZp_profile_3D_plain_f32(d_in, d_cmp, nbEle, &profBytes, dims, range, sample_rate, stream);
          else
            cuSZp_profile_3D_outlier_f32(d_in, d_cmp, nbEle, &profBytes, dims, range, sample_rate, stream);
     } else {
        // 1D
        cuSZp_profile_1D_plain_f32(d_in, d_cmp, nbEle, &profBytes, range, sample_rate, stream);
     }
  }
  
  // --- Profiling ---
  timer_GPU.StartCounter(); 
  if (is_3d) {
      uint3 dims = make_uint3(arg_x, arg_y, arg_z);
      if (mode == CUSZP_MODE_PLAIN)
        cuSZp_profile_3D_plain_f32(d_in, d_cmp, nbEle, &profBytes, dims, range, sample_rate, stream);
      else
        cuSZp_profile_3D_outlier_f32(d_in, d_cmp, nbEle, &profBytes, dims, range, sample_rate, stream);
  } else {
      if (mode == CUSZP_MODE_PLAIN)
          cuSZp_profile_1D_plain_f32(d_in, d_cmp, nbEle, &profBytes, range, sample_rate, stream);
      else
          cuSZp_profile_1D_outlier_f32(d_in, d_cmp, nbEle, &profBytes, range, sample_rate, stream);
  }

  uint4 final_row[32]{};
  CHECK_CUDA(cudaMemcpyAsync(final_row, d_cmp , std::min(profBytes, 32*sizeof(uint4)), cudaMemcpyDeviceToHost, stream));
  CHECK_CUDA(cudaStreamSynchronize(stream));

  // Determine Adjusted Target Ratio
  double adjusted_target_ratio = targetR;
  int sample_per_eb = 0;
  size_t orig_per_block_bytes = 0;

  if (is_3d) {
      // 3D Logic (Correction for Padding)
      uint dimzBlock = (arg_z + 3) / 4;
      uint dimyBlock = (arg_y + 3) / 4;
      uint dimxBlock = (arg_x + 3) / 4;
      size_t total_blocks = (size_t)dimzBlock * dimyBlock * dimxBlock;
      if (total_blocks == 0) total_blocks = 1;

      sample_per_eb = total_blocks / sample_rate;
      if (sample_per_eb < 1) sample_per_eb = 1;
      
      orig_per_block_bytes = 64 * sizeof(float);

      double padded_size = (double)total_blocks * (double)orig_per_block_bytes;
      double unpadded_size = (double)nbEle * sizeof(float);
      double ratio_correction = padded_size / unpadded_size;
      adjusted_target_ratio = targetR * ratio_correction;
  } else {
      // 1D Logic
      // 1D uses 32-element blocks
      int total_blocks = (nbEle + 31) / 32;
      sample_per_eb = std::max(1, total_blocks / sample_rate);
      orig_per_block_bytes = 32 * sizeof(float);
      
      // 1D also has minor padding (N -> multiple of 32).
      // If we want perfection, we can apply correction too.
      double padded = (double)total_blocks * 32.0 * 4.0;
      double unpadded = (double)nbEle * 4.0;
      adjusted_target_ratio = targetR * (padded / unpadded);
  }

  const int best_idx = pick_best_eb_from_finalrow_generic(final_row, sample_per_eb, adjusted_target_ratio, orig_per_block_bytes);
  const float best_rel_eb = PRO_128_REL_EB[best_idx];
  const float absEB = best_rel_eb * range;
  float profileTime = timer_GPU.GetCounter();
  
  printf("profile end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/profileTime);
  printf("[fix-ratio] target R=%.3f (adj=%.3f) -> pick EB_idx=%d relEB=%.3e absEB=%.6g\n", targetR, adjusted_target_ratio, best_idx, best_rel_eb, absEB);

  // --- Compression ---
  size_t cmpSize = 0;
  timer_GPU.StartCounter();
  
  if (is_3d) {
        uint3 dims = make_uint3(arg_x, arg_y, arg_z);
        if (mode == CUSZP_MODE_PLAIN)
            cuSZp_compress_3D_plain_f32(d_in, d_cmp, nbEle, &cmpSize, dims, absEB, stream);
        else
            cuSZp_compress_3D_outlier_f32(d_in, d_cmp, nbEle, &cmpSize, dims, absEB, stream);
  } else {
       // 1D uses wrapper
       cuSZp_compress((void*)d_in, d_cmp, nbEle, &cmpSize, absEB, CUSZP_TYPE_FLOAT, mode, stream);
  }
  
  float cmpTime = timer_GPU.GetCounter();

  printf(" compression end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
  printf(" total end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpTime+profileTime));
  CHECK_CUDA(cudaStreamSynchronize(stream));

  const double real_ratio = (double)inBytes / (double)cmpSize;
  printf("[compress] bytes_in=%zu  bytes_cmp=%zu  ratio=%.3f\n",inBytes, cmpSize, real_ratio);

  // --- Decompression ---
  timer_GPU.StartCounter();
  
  if (is_3d) {
        uint3 dims = make_uint3(arg_x, arg_y, arg_z);
        if (mode == CUSZP_MODE_PLAIN)
            cuSZp_decompress_3D_plain_f32(d_dec, d_cmp, nbEle, cmpSize, dims, absEB, stream);
        else
            cuSZp_decompress_3D_outlier_f32(d_dec, d_cmp, nbEle, cmpSize, dims, absEB, stream);
  } else {
       // 1D wrapper
       cuSZp_decompress((void*)d_dec, d_cmp, nbEle, cmpSize, absEB, CUSZP_TYPE_FLOAT, mode, stream);
  }
  
  float decTime = timer_GPU.GetCounter();
  printf(" decompression end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/decTime);
  CHECK_CUDA(cudaStreamSynchronize(stream));

  if (outCmp) {
    CHECK_CUDA(cudaStreamSynchronize(stream));
    std::vector<unsigned char> h_cmp(cmpSize);
    CHECK_CUDA(cudaMemcpy(h_cmp.data(), d_cmp, cmpSize, cudaMemcpyDeviceToHost));
    int wstatus = 0;
    writeByteData_Yafan(h_cmp.data(), cmpSize, outCmp, &wstatus);
    if (wstatus != 0) fprintf(stderr, "[write] failed to write %s\n", outCmp);
    else printf("[write] saved compressed bitstream to %s\n", outCmp);
  }

  free(h_in);
  cudaFree(d_in); cudaFree(d_cmp); cudaFree(d_dec);
  cudaStreamDestroy(stream);
  return 0;
}