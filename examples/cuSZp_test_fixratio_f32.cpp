#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include <cuda_runtime.h>
#include <cuSZp.h>

int main()
{

    // // For measuring the end-to-end throughput.
    // TimingGPU timer_GPU;

    // // Initializing CUDA Stream.
    // cudaStream_t stream;
    // cudaStreamCreate(&stream);
    // // timer 
    // cudaEvent_t start, stop;
    // cudaEventCreate(&start);
    // cudaEventCreate(&stop);

    // printf("==================================================\n");
    // printf("=======Testing profiler from HACC dataset=========\n");
    // printf("==================================================\n");


    // int status = 0;
    // char* oriFilePath = "/home/bohan/1billionparticles_onesnapshot/vx.f32";
    // void* ori = NULL;
    // void* dData = NULL;
    // unsigned char* cBytes = NULL;

    // size_t nbEle = 0;
    // ori = (void*)readFloatData_Yafan(oriFilePath, &nbEle, &status);
    // float* f_ori = (float*)ori;

    // float max_val = f_ori[0];
    // float min_val = f_ori[0];
    // for(size_t i=0; i<nbEle; i++)
    // {
    //     if(f_ori[i]>max_val)
    //         max_val = f_ori[i];
    //     else if(f_ori[i]<min_val)
    //         min_val = f_ori[i];
    // }
    // float range = max_val - min_val;

    // float* d_ori_;
    // unsigned char* d_cmp_;

    // cudaMalloc((void**)&d_ori_, sizeof(float)*nbEle);
    // cudaMemcpy(d_ori_, ori, sizeof(float)*nbEle, cudaMemcpyHostToDevice);
    // cudaMalloc((void**)&d_cmp_, sizeof(float)*nbEle);
    // cudaMemset(d_cmp_, 0, sizeof(unsigned char) * nbEle);

    // size_t cmpSize = 0;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_profile_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, range, stream);
    // float cmpTime = timer_GPU.GetCounter();
    // printf("Profiler finished!\n");
    // printf("Profiler time takes %f seconds \n", cmpTime);
    // printf("Profiler end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);


    // printf("==================================================================================\n");

    // float errorBound = 1e-2f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");
    
    // errorBound = 1e-3f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    
    
    // errorBound = 1e-4f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 7.600E-04f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 1.6E-3f * range; 

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // printf("\n");
    // printf("==================================================\n");
    // printf("=======Testing profiler from NYX dataset==========\n");
    // printf("==================================================\n");


    // status = 0;
    // oriFilePath = "/home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32";
    // ori = NULL;
    
    // dData = NULL;
    // cBytes = NULL;

    // nbEle = 0;
    // ori = (void*)readFloatData_Yafan(oriFilePath, &nbEle, &status);
    // f_ori = (float*)ori;
    //     max_val = f_ori[0];
    // min_val = f_ori[0];
    // for(size_t i=0; i<nbEle; i++)
    // {
    //     if(f_ori[i]>max_val)
    //         max_val = f_ori[i];
    //     else if(f_ori[i]<min_val)
    //         min_val = f_ori[i];
    // }
    // range = max_val - min_val;


    // cudaMalloc((void**)&d_ori_, sizeof(float)*nbEle);
    // cudaMemcpy(d_ori_, ori, sizeof(float)*nbEle, cudaMemcpyHostToDevice);
    // cudaMalloc((void**)&d_cmp_, sizeof(float)*nbEle);
    // cudaMemset(d_cmp_, 0, sizeof(unsigned char) * nbEle);

    // cmpSize = 0;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_profile_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, range,stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Profiler finished!\n");
    // printf("Profiler time takes %f seconds \n", cmpTime);
    // printf("Profiler end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);


    // printf("==================================================================================\n");

    // errorBound = 1E-1f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");
    
    // errorBound = 3.400e-04 * range ;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    
    
    // errorBound = 2.200e-03 * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 5.800e-03 * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 5E-5f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");


    // printf("\n");
    // printf("==================================================\n");
    // printf("======Testing profiler from CESM dataset==========\n");
    // printf("==================================================\n");


    // status = 0;
    // oriFilePath = "/home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/FICE_1_26_1800_3600.f32";
    // ori = NULL;
    // dData = NULL;
    // cBytes = NULL;


    // nbEle = 0;
    // ori = (void*)readFloatData_Yafan(oriFilePath, &nbEle, &status);
    // f_ori = (float*)ori;
    //     max_val = f_ori[0];
    // min_val = f_ori[0];
    // for(size_t i=0; i<nbEle; i++)
    // {
    //     if(f_ori[i]>max_val)
    //         max_val = f_ori[i];
    //     else if(f_ori[i]<min_val)
    //         min_val = f_ori[i];
    // }
    // range = max_val - min_val;


    // cudaMalloc((void**)&d_ori_, sizeof(float)*nbEle);
    // cudaMemcpy(d_ori_, ori, sizeof(float)*nbEle, cudaMemcpyHostToDevice);
    // cudaMalloc((void**)&d_cmp_, sizeof(float)*nbEle);
    // cudaMemset(d_cmp_, 0, sizeof(unsigned char) * nbEle);

    // cmpSize = 0;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_profile_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, range, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Profiler finished!\n");
    // printf("Profiler time takes %f seconds \n", cmpTime);
    // printf("Profiler end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);


    // printf("==================================================================================\n");

    // errorBound = 6.100e-02* range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");
    
    // errorBound = 1.600e-02* range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    
    
    // errorBound = 2.200e-03* range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 1E-4f* range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 5E-5f* range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");



    // printf("\n");
    // printf("==================================================\n");
    // printf("===Testing profiler from exaalt-copper dataset====\n");
    // printf("==================================================\n");


    // status = 0;
    // oriFilePath = "/home/bohan/SDRBENCH-exaalt-copper/dataset2-83x1077290.y.f32.dat";
    // ori = NULL;
    
    // dData = NULL;
    // cBytes = NULL;

    // nbEle = 0;
    // ori = (void*)readFloatData_Yafan(oriFilePath, &nbEle, &status);
    // f_ori = (float*)ori;
    //     max_val = f_ori[0];
    // min_val = f_ori[0];
    // for(size_t i=0; i<nbEle; i++)
    // {
    //     if(f_ori[i]>max_val)
    //         max_val = f_ori[i];
    //     else if(f_ori[i]<min_val)
    //         min_val = f_ori[i];
    // }
    // range = max_val - min_val;


    // cudaMalloc((void**)&d_ori_, sizeof(float)*nbEle);
    // cudaMemcpy(d_ori_, ori, sizeof(float)*nbEle, cudaMemcpyHostToDevice);
    // cudaMalloc((void**)&d_cmp_, sizeof(float)*nbEle);
    // cudaMemset(d_cmp_, 0, sizeof(unsigned char) * nbEle);

    // cmpSize = 0;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_profile_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, range,stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Profiler finished!\n");
    // printf("Profiler time takes %f seconds \n", cmpTime);
    // printf("Profiler end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);


    // printf("==================================================================================\n");

    // errorBound = 2.800e-03 * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");
    
    // errorBound = 1.900e-02 * range ;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    
    
    // errorBound = 4.900e-02 * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 1E-4f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 5E-5f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");




    // printf("\n");
    // printf("==================================================\n");
    // printf("===Testing profiler from SCALE dataset====\n");
    // printf("==================================================\n");


    // status = 0;
    // oriFilePath = "/home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/PRES-98x1200x1200.f32";
    // ori = NULL;
    
    // dData = NULL;
    // cBytes = NULL;

    // nbEle = 0;
    // ori = (void*)readFloatData_Yafan(oriFilePath, &nbEle, &status);
    // f_ori = (float*)ori;
    //     max_val = f_ori[0];
    // min_val = f_ori[0];
    // for(size_t i=0; i<nbEle; i++)
    // {
    //     if(f_ori[i]>max_val)
    //         max_val = f_ori[i];
    //     else if(f_ori[i]<min_val)
    //         min_val = f_ori[i];
    // }
    // range = max_val - min_val;


    // cudaMalloc((void**)&d_ori_, sizeof(float)*nbEle);
    // cudaMemcpy(d_ori_, ori, sizeof(float)*nbEle, cudaMemcpyHostToDevice);
    // cudaMalloc((void**)&d_cmp_, sizeof(float)*nbEle);
    // cudaMemset(d_cmp_, 0, sizeof(unsigned char) * nbEle);

    // cmpSize = 0;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_profile_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, range,stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Profiler finished!\n");
    // printf("Profiler time takes %f seconds \n", cmpTime);
    // printf("Profiler end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);


    // printf("==================================================================================\n");

    // errorBound = 3.400e-02 * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");
    
    // errorBound = 1.300e-02 * range ;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    
    
    // errorBound = 2.200e-03 * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 1E-4f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 5E-5f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");



    // printf("\n");
    // printf("==================================================\n");
    // printf("===Testing profiler from QMCPACK dataset====\n");
    // printf("==================================================\n");


    // status = 0;
    // oriFilePath = "/home/bohan/SDRBENCH-QMCPack/dataset/115x69x69x288/einspline_115_69_69_288.f32";
    // ori = NULL;
    
    // dData = NULL;
    // cBytes = NULL;

    // nbEle = 0;
    // ori = (void*)readFloatData_Yafan(oriFilePath, &nbEle, &status);
    // f_ori = (float*)ori;
    //     max_val = f_ori[0];
    // min_val = f_ori[0];
    // for(size_t i=0; i<nbEle; i++)
    // {
    //     if(f_ori[i]>max_val)
    //         max_val = f_ori[i];
    //     else if(f_ori[i]<min_val)
    //         min_val = f_ori[i];
    // }
    // range = max_val - min_val;


    // cudaMalloc((void**)&d_ori_, sizeof(float)*nbEle);
    // cudaMemcpy(d_ori_, ori, sizeof(float)*nbEle, cudaMemcpyHostToDevice);
    // cudaMalloc((void**)&d_cmp_, sizeof(float)*nbEle);
    // cudaMemset(d_cmp_, 0, sizeof(unsigned char) * nbEle);

    // cmpSize = 0;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_profile_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, range,stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Profiler finished!\n");
    // printf("Profiler time takes %f seconds \n", cmpTime);
    // printf("Profiler end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);


    // printf("==================================================================================\n");

    // errorBound = 1.900e-04 * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");
    
    // errorBound = 7.600e-04 * range ;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    
    
    // errorBound = 2.200e-03 * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 1E-4f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");

    // errorBound = 5E-5f * range;

    // timer_GPU.StartCounter(); // set timer
    // cuSZp_compress_1D_plain_f32(d_ori_, d_cmp_, nbEle, &cmpSize, errorBound, stream);
    // cmpTime = timer_GPU.GetCounter();
    // printf("Error bound using for using cuSZP = %f\n", errorBound/range);
    // printf("cuSZp-p compression ratio: %f\n", (nbEle*sizeof(float)/1024.0/1024.0)/(cmpSize*sizeof(unsigned char)/1024.0/1024.0));
    // printf("cuSZp-p finished!\n");
    // printf("cuSZp-p time takes %f seconds \n", cmpTime);
    // printf("cuSZp-p compression   end-to-end speed: %f GB/s\n", (nbEle*sizeof(float)/1024.0/1024.0)/cmpTime);
    // printf("==================================================================================\n");






    // cudaStreamDestroy(stream);
    // return 0;

}