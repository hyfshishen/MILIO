
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
  printf("  ./cuSZp_all_eb_check -i <input.f32> [-x <dim_x>] [-y <dim_y>] [-z <dim_z>] [-m <plain|outlier>] [-S <rate>]\n");
}

static void find_min_max(const float* a, size_t n, float& mn, float& mx) {
  if (n == 0) { mn = mx = 0; return; }
  mn = mx = a[0];
  for (size_t i = 1; i < n; ++i) { mn = std::min(mn, a[i]); mx = std::max(mx, a[i]); }
}

float* readFloatData_Yafan_Local(const char* path, size_t* nbEle, int* status) {
    FILE* f = fopen(path, "rb");
    if (!f) { *status = 1; return nullptr; }
    fseek(f, 0, SEEK_END);
    size_t sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    size_t n = sz / sizeof(float);
    *nbEle = n;
    float* d = (float*)malloc(sz);
    if (!d) { *status = 2; fclose(f); return nullptr; }
    size_t r = fread(d, sizeof(float), n, f);
    fclose(f);
    if (r != n) { free(d); *status = 3; return nullptr; }
    *status = 0;
    return d;
}

int main(int argc, char** argv) {
  char* inPath = nullptr;
  int sample_rate = 1000;
  cuszp_mode_t mode = CUSZP_MODE_PLAIN;
  
  size_t arg_x = 0;
  size_t arg_y = 0;
  size_t arg_z = 0;
  
  for (int i = 1; i < argc; ++i) {
    if (!strcmp(argv[i], "-i") && i + 1 < argc) inPath = argv[++i];
    else if (!strcmp(argv[i], "-x") && i + 1 < argc) {
         char* next = argv[i+1];
         if (isdigit(next[0])) { arg_x = atol(argv[++i]); }
    }
    else if (!strcmp(argv[i], "-y") && i + 1 < argc) arg_y = atol(argv[++i]);
    else if (!strcmp(argv[i], "-z") && i + 1 < argc) arg_z = atol(argv[++i]);
    else if (!strcmp(argv[i], "-S") && i + 1 < argc) sample_rate = atoi(argv[++i]);
    else if (!strcmp(argv[i], "-m") && i + 1 < argc) {
        const char* mstr = argv[++i];
        if (!strcmp(mstr, "outlier")) mode = CUSZP_MODE_OUTLIER;
        else if (!strcmp(mstr, "plain")) mode = CUSZP_MODE_PLAIN;
        else { usage(); return EXIT_FAILURE; }
    }
  }

  if (!inPath) { usage(); return EXIT_FAILURE; }

  int status = 0;
  size_t nbEle = 0;
  // Use local read or the one from utility if linked. I'll define local just in case "readFloatData_Yafan" is not available in shared headers (it was extern in .cpp usually or in utility).
  // The original calls readFloatData_Yafan, so it must be in cuSZp_utility.cu
  // I will check linking later. If utility is linked, I can call it.
  // For now, I'll assume I can link utility.
  // float* h_in = readFloatData_Yafan(inPath, &nbEle, &status);
  // Actually, I'll use my local one to be safe and self-contained for file IO.
  float* h_in = readFloatData_Yafan_Local(inPath, &nbEle, &status);
  
  if (!h_in || status != 0 || nbEle == 0) {
    fprintf(stderr, "Failed to read input: %s\n", inPath);
    return EXIT_FAILURE;
  }

  bool is_3d = (arg_y > 1 && arg_z > 1);
  if (!is_3d && arg_x == 0) arg_x = nbEle;

  // range for rel EB
  float mn, mx; find_min_max(h_in, nbEle, mn, mx);
  const float range = mx - mn;
  
  const size_t inBytes = nbEle * sizeof(float);
  const size_t cmpCap  = inBytes + (1u << 20); 
  float* d_in = nullptr; unsigned char* d_cmp = nullptr;
  CHECK_CUDA(cudaMalloc(&d_in,  inBytes));
  CHECK_CUDA(cudaMalloc(&d_cmp, cmpCap));
  CHECK_CUDA(cudaMemcpy(d_in, h_in, inBytes, cudaMemcpyHostToDevice));

  cudaStream_t stream; CHECK_CUDA(cudaStreamCreate(&stream));

  size_t profBytes = 0;
  
  // Profiling
  // No warmup needed for this analysis tool, just run once.
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

  // Determine Sample Stats for Estimation
  int sample_per_eb = 0;
  size_t orig_per_block_bytes = 0;

  size_t total_blocks = 0;

  if (is_3d) {
      uint dimzBlock = (arg_z + 3) / 4;
      uint dimyBlock = (arg_y + 3) / 4;
      uint dimxBlock = (arg_x + 3) / 4;
      total_blocks = (size_t)dimzBlock * dimyBlock * dimxBlock;
      if (total_blocks == 0) total_blocks = 1;
      sample_per_eb = total_blocks / sample_rate;
      if (sample_per_eb < 1) sample_per_eb = 1;
      orig_per_block_bytes = 64 * sizeof(float);
  } else {
      total_blocks = (nbEle + 31) / 32;
      sample_per_eb = std::max(1, (int)total_blocks / sample_rate);
      orig_per_block_bytes = 32 * sizeof(float);
  }
  

  const double total_orig_sample = (double)orig_per_block_bytes * (double)sample_per_eb;

  // Extract estimates
  int bytes_per_eb[128];
  for (int lane = 0; lane < 32; ++lane) {
    const uint4 q = final_row[lane];
    const int base = lane * 4;
    bytes_per_eb[base + 0] = (int)q.x;
    bytes_per_eb[base + 1] = (int)q.y;
    bytes_per_eb[base + 2] = (int)q.z;
    bytes_per_eb[base + 3] = (int)q.w;
  }
  
  // Calculate Padding Correction (Unpadded / Padded)
  // The profiling estimates ratio for Padded data.
  // True ratio is for Unpadded data.
  // We want est_ratio to predict the True Ratio.
  double padded_size = (double)total_blocks * (double)orig_per_block_bytes;
  double unpadded_size = (double)nbEle * sizeof(float);
  double padding_correction = unpadded_size / padded_size;

  // Iterate over all 128 error bounds
  for (int i = 0; i < 128; ++i) {
      int b = bytes_per_eb[i];
      if (b <= 0) continue; // Skip invalid
      
      // Est Ratio (Padded)
      double est_ratio_padded = total_orig_sample / (double)b;
      
      // Est Ratio (Unpadded / User Facing)
      double est_ratio = est_ratio_padded * padding_correction;
      
      // Run Actual Compression

      float rel_eb = PRO_128_REL_EB[i];
      float absEB = rel_eb * range;
      size_t cmpSize = 0;
      
      if (is_3d) {
            uint3 dims = make_uint3(arg_x, arg_y, arg_z);
            if (mode == CUSZP_MODE_PLAIN)
                cuSZp_compress_3D_plain_f32(d_in, d_cmp, nbEle, &cmpSize, dims, absEB, stream);
            else
                cuSZp_compress_3D_outlier_f32(d_in, d_cmp, nbEle, &cmpSize, dims, absEB, stream);
      } else {
           cuSZp_compress((void*)d_in, d_cmp, nbEle, &cmpSize, absEB, CUSZP_TYPE_FLOAT, mode, stream);
      }
      CHECK_CUDA(cudaStreamSynchronize(stream));
      
      double true_ratio = (double)inBytes / (double)cmpSize;
      
      // Output: EB_Index, RelEB, EstRatio, TrueRatio
      printf("DATA:%d:%.6e:%.5f:%.5f\n", i, rel_eb, est_ratio, true_ratio);
  }

  free(h_in);
  cudaFree(d_in); cudaFree(d_cmp);
  cudaStreamDestroy(stream);
  return 0;
}
