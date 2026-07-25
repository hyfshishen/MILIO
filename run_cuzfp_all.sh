#!/bin/bash
echo 'BENCH_START:CESM:CLDICE_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLDICE_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CLDICE_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLDICE_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CLDICE_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLDICE_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CLDLIQ_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLDLIQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CLDLIQ_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLDLIQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CLDLIQ_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLDLIQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CLOUD_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLOUD_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CLOUD_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLOUD_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CLOUD_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLOUD_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDQR_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDQR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDQR_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDQR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDQR_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDQR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDQ_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDQ_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDQ_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDT_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDT_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CMFDT_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CMFDT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CONCLD_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CONCLD_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CONCLD_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CONCLD_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:CONCLD_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CONCLD_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DCQ_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DCQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DCQ_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DCQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DCQ_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DCQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DTCOND_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DTCOND_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DTCOND_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DTCOND_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DTCOND_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DTCOND_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DTV_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DTV_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DTV_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DTV_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:DTV_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/DTV_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:FICE_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/FICE_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:FICE_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/FICE_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:FICE_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/FICE_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:GCLDLWP_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/GCLDLWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:GCLDLWP_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/GCLDLWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:GCLDLWP_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/GCLDLWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICIMR_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICIMR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICIMR_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICIMR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICIMR_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICIMR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICLDIWP_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICLDIWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICLDIWP_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICLDIWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICLDIWP_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICLDIWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICLDTWP_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICLDTWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICLDTWP_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICLDTWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICLDTWP_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICLDTWP_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICWMR_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICWMR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICWMR_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICWMR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:ICWMR_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/ICWMR_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:OMEGAT_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/OMEGAT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:OMEGAT_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/OMEGAT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:OMEGAT_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/OMEGAT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:OMEGA_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/OMEGA_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:OMEGA_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/OMEGA_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:OMEGA_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/OMEGA_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QC_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QC_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QC_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QC_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QC_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QC_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QRL_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QRL_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QRL_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QRL_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QRL_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QRL_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QRS_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QRS_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QRS_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QRS_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:QRS_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/QRS_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:Q_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/Q_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:Q_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/Q_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:Q_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/Q_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:RELHUM_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/RELHUM_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:RELHUM_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/RELHUM_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:RELHUM_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/RELHUM_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:T_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/T_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:T_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/T_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:T_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/T_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:UU_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/UU_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:UU_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/UU_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:UU_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/UU_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:U_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/U_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:U_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/U_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:U_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/U_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VD01_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VD01_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VD01_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VD01_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VD01_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VD01_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VQ_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VQ_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VQ_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VQ_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VT_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VT_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VT_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VT_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VU_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VU_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VU_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VU_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VU_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VU_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VV_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VV_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VV_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VV_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:VV_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/VV_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:V_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/V_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:V_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/V_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:V_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/V_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:CESM:Z3_1_26_1800_3600.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/Z3_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:CESM:Z3_1_26_1800_3600.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/Z3_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:CESM:Z3_1_26_1800_3600.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/Z3_1_26_1800_3600.f32 -f -3 3600 1800 26 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:NYX:baryon_density.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/baryon_density.f32 -f -3 512 512 512 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:NYX:baryon_density.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/baryon_density.f32 -f -3 512 512 512 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:NYX:baryon_density.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/baryon_density.f32 -f -3 512 512 512 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:NYX:dark_matter_density.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/dark_matter_density.f32 -f -3 512 512 512 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:NYX:dark_matter_density.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/dark_matter_density.f32 -f -3 512 512 512 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:NYX:dark_matter_density.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/dark_matter_density.f32 -f -3 512 512 512 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:NYX:temperature.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/temperature.f32 -f -3 512 512 512 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:NYX:temperature.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/temperature.f32 -f -3 512 512 512 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:NYX:temperature.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/temperature.f32 -f -3 512 512 512 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_x.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 -f -3 512 512 512 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_x.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 -f -3 512 512 512 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_x.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 -f -3 512 512 512 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_y.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 -f -3 512 512 512 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_y.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 -f -3 512 512 512 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_y.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 -f -3 512 512 512 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_z.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 -f -3 512 512 512 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_z.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 -f -3 512 512 512 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:NYX:velocity_z.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 -f -3 512 512 512 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vx.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vx.f32 -f -1 1073726487 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vx.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vx.f32 -f -1 1073726487 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vx.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vx.f32 -f -1 1073726487 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vy.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vy.f32 -f -1 1073726487 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vy.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vy.f32 -f -1 1073726487 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vy.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vy.f32 -f -1 1073726487 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vz.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vz.f32 -f -1 1073726487 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vz.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vz.f32 -f -1 1073726487 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:HACC:vz.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/vz.f32 -f -1 1073726487 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:HACC:xx.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/xx.f32 -f -1 1073726487 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:HACC:xx.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/xx.f32 -f -1 1073726487 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:HACC:xx.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/xx.f32 -f -1 1073726487 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:HACC:yy.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/yy.f32 -f -1 1073726487 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:HACC:yy.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/yy.f32 -f -1 1073726487 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:HACC:yy.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/yy.f32 -f -1 1073726487 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:HACC:zz.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/zz.f32 -f -1 1073726487 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:HACC:zz.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/zz.f32 -f -1 1073726487 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:HACC:zz.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/1billionparticles_onesnapshot/zz.f32 -f -1 1073726487 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:EXAFEL:SDRBENCH-EXAFEL-data-130x1480x1552.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXAFEL-130x1480x1552/SDRBENCH-EXAFEL-data-130x1480x1552.f32 -f -3 1552 1480 130 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:EXAFEL:SDRBENCH-EXAFEL-data-130x1480x1552.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXAFEL-130x1480x1552/SDRBENCH-EXAFEL-data-130x1480x1552.f32 -f -3 1552 1480 130 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:EXAFEL:SDRBENCH-EXAFEL-data-130x1480x1552.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-EXAFEL-130x1480x1552/SDRBENCH-EXAFEL-data-130x1480x1552.f32 -f -3 1552 1480 130 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:QMCPACK:einspline_115_69_69_288.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/dataset/115x69x69x288/einspline_115_69_69_288.f32 -f -1 157684320 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:QMCPACK:einspline_115_69_69_288.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/dataset/115x69x69x288/einspline_115_69_69_288.f32 -f -1 157684320 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:QMCPACK:einspline_115_69_69_288.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/dataset/115x69x69x288/einspline_115_69_69_288.f32 -f -1 157684320 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:QMCPACK:einspline_288_115_69_69.pre.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/dataset/288x115x69x69/einspline_288_115_69_69.pre.f32 -f -1 157684320 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:QMCPACK:einspline_288_115_69_69.pre.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/dataset/288x115x69x69/einspline_288_115_69_69.pre.f32 -f -1 157684320 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:QMCPACK:einspline_288_115_69_69.pre.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/dataset/288x115x69x69/einspline_288_115_69_69.pre.f32 -f -1 157684320 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_1000:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_1000 -f -1 357654528 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_1000:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_1000 -f -1 357654528 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_1000:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_1000 -f -1 357654528 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_2000:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_2000 -f -1 357654528 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_2000:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_2000 -f -1 357654528 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_2000:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_2000 -f -1 357654528 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_3000:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_3000 -f -1 357654528 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_3000:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_3000 -f -1 357654528 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:RTM:pressure_3000:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/pressure_3000 -f -1 357654528 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SYNTHESIS:synthetic_truss_with_five_defects_1200x1200x1200_float32.raw:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/synthetic_truss_with_five_defects_1200x1200x1200_float32.raw -f -3 1200 1200 1200 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SYNTHESIS:synthetic_truss_with_five_defects_1200x1200x1200_float32.raw:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/synthetic_truss_with_five_defects_1200x1200x1200_float32.raw -f -3 1200 1200 1200 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SYNTHESIS:synthetic_truss_with_five_defects_1200x1200x1200_float32.raw:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/synthetic_truss_with_five_defects_1200x1200x1200_float32.raw -f -3 1200 1200 1200 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.x.f32.dat:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.x.f32.dat -f -1 17011951 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.x.f32.dat:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.x.f32.dat -f -1 17011951 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.x.f32.dat:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.x.f32.dat -f -1 17011951 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.y.f32.dat:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.y.f32.dat -f -1 17011951 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.y.f32.dat:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.y.f32.dat -f -1 17011951 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.y.f32.dat:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.y.f32.dat -f -1 17011951 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.z.f32.dat:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.z.f32.dat -f -1 17011951 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.z.f32.dat:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.z.f32.dat -f -1 17011951 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset1-5423x3137.z.f32.dat:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset1-5423x3137.z.f32.dat -f -1 17011951 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.x.f32.dat:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.x.f32.dat -f -1 89415070 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.x.f32.dat:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.x.f32.dat -f -1 89415070 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.x.f32.dat:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.x.f32.dat -f -1 89415070 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.y.f32.dat:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.y.f32.dat -f -1 89415070 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.y.f32.dat:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.y.f32.dat -f -1 89415070 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.y.f32.dat:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.y.f32.dat -f -1 89415070 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.z.f32.dat:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.z.f32.dat -f -1 89415070 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.z.f32.dat:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.z.f32.dat -f -1 89415070 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:EXAALT:dataset2-83x1077290.z.f32.dat:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper/dataset2-83x1077290.z.f32.dat -f -1 89415070 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:PRES-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/PRES-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:PRES-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/PRES-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:PRES-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/PRES-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QC-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QC-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QC-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QC-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QC-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QC-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QG-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QG-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QG-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QG-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QG-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QG-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QI-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QI-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QI-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QI-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QI-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QI-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QR-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QR-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QR-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QR-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QR-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QR-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QS-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QS-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QS-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QS-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QS-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QS-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QV-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QV-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QV-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QV-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:QV-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/QV-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:RH-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/RH-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:RH-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/RH-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:RH-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/RH-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:T-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/T-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:T-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/T-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:T-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/T-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:U-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/U-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:U-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/U-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:U-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/U-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:V-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/V-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:V-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/V-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:V-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/V-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:W-98x1200x1200.f32:4'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/W-98x1200x1200.f32 -f -3 1200 1200 98 -r 8 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:W-98x1200x1200.f32:6'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/W-98x1200x1200.f32 -f -3 1200 1200 98 -r 5.3333 -s || true
sleep 0.1
echo 'BENCH_START:SCALE:W-98x1200x1200.f32:8'
/u/bzhang28/zfp/build/bin/zfp -x cuda -i /scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200/W-98x1200x1200.f32 -f -3 1200 1200 98 -r 4 -s || true
sleep 0.1
