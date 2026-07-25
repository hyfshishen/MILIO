# MILIO

This repository contains the source code and evaluation scripts for the SC'25
AD/AE process of the paper *From Error-Bounded to Fixed-Ratio: Efficient
Sampling-Guided GPU Lossy Compression*.

MILIO is a GPU lossy compressor that reaches a **user-specified compression
ratio** in a single pass while still reporting a **pointwise error bound** for
every field. It uses sampling-guided error-bound selection: given a target ratio
*R*, MILIO profiles a small sample of the input to estimate the ratio–error
relationship, selects the error bound that meets *R*, and compresses the full
field with that bound — without host-driven trial-and-error re-compression.
Across nine scientific datasets it sustains about 220 GB/s on an NVIDIA A100,
roughly 2.82× the throughput of cuZFP at matched ratios.

The rest of this README has two parts: Section 1 builds MILIO and prepares the
datasets; Section 2 reproduces the paper's results.

## 1. Configuring MILIO and datasets

### 1.1 Software and hardware dependencies

- Linux with the NVIDIA driver and an A100-class GPU (any CUDA GPU works; the
  paper uses a single NVIDIA A100 40 GB)
- CUDA Toolkit ≥ 11.0 (tested with 11.8 and 12.8)
- CMake ≥ 3.21 and a C++17 host compiler compatible with the CUDA toolkit
- Python 3 with `numpy` and `matplotlib`
- For the paper's reproduction: a Slurm single-GPU partition, and the cuZFP
  baseline (`zfp` built with `-DZFP_WITH_CUDA=ON`)

### 1.2 Building MILIO

```bash
git clone https://github.com/hyfshishen/MILIO.git
cd MILIO
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j
```

The command-line tools are written to `build/examples/bin/`. Verify the build by
printing the fixed-ratio CLI usage:

```bash
$ ./build/examples/bin/cuszp_fixed_ratio_cli -h
Usage: cuszp_fixed_ratio_cli [options]
Options:
  -i <input_file>   Path to the input binary file (float32)
  -o <output_file>  Path to output compressed file (optional)
  -D <recon_file>   Path to write reconstructed (decompressed) field (optional)
  -n <num_elements> Number of elements (required)
  -r <ratio>        Target compression ratio (default: 4.0)
  -m <mode>         Compression mode: plain or outlier (default: outlier)
  -h                Show this help message
```

A single compression then runs like the following (1D field of *N* elements at
target ratio 4; use `cuszp_fixed_ratio_cli_3d -x -y -z` for 3D fields). It prints
the selected error bound, the achieved ratio, the throughput, and the PSNR:

```bash
./build/examples/bin/cuszp_fixed_ratio_cli -i field.f32 -n 16777216 -r 4.0 -m outlier
```

Mode `plain`/`outlier` corresponds to MILIO-p/MILIO-o in the paper; `outlier`
generally preserves quality better on sparse fields.

### 1.3 Setting up datasets

The nine evaluation datasets are downloaded and arranged by a helper script:

```bash
python3 download_datasets.py --data-root ./datasets
```

It fetches the seven SDRBench archives and the Open-SciVis SYNTHESIS field over
HTTP, and the RTM fields from a shared Google Drive folder (via `gdown`,
installed on first use). The script is idempotent, so an interrupted run can be
restarted. Compressed archives total ~61 GB to download; allow ~120 GB of free
disk for the extracted data.

## 2. Reproducing the paper

The `ADAE/` directory holds three self-contained one-click packages, one per
result group. Each builds the required binaries, runs its benchmarks as
single-GPU Slurm jobs, and renders the corresponding figures and tables. Point
the scripts at your environment first (defaults match the authors' setup):

```bash
export DATA_ROOT=/path/to/datasets            # from Section 1.3
export ZFP_EXE=/path/to/zfp/build/bin/zfp     # cuda-enabled zfp binary
export SLURM_ACCOUNT=<your-account>
export SLURM_PARTITION=<your-a100-partition>
```

The raw `*.log` files each part writes under `results/` are intermediate; the
outputs to inspect are the figures under `results/benchmark_charts/` and the
tables under `results/`. Absolute throughput depends on the GPU/host, while the
achieved ratios, PSNR/SSIM, and MILIO-vs-cuZFP trends are hardware-independent.
Append `--plot-only` to any script to re-render from the shipped logs without a
GPU or the datasets.

### 2.1 Throughput — Figures 10, 11, 12

```bash
cd ADAE/PART1 && ./run_part1.sh
```

Runs the MILIO fixed-ratio benchmark and the cuZFP baseline over all datasets
(*R* ∈ {4, 6, 8}) and renders the throughput summaries, the profiling/compression
breakdowns, and the normalized profiling-overhead figures. As an example, the
reproduced end-to-end throughput at *R* = 4 averages ~246 GB/s (MILIO-p) and
~205 GB/s (MILIO-o) for compression, both well above the cuZFP baseline
(~78 GB/s); Figures 10–11 plot the average over *R* ∈ {4, 6, 8}.

### 2.2 Reconstruction quality — Figures 14, 15

```bash
cd ADAE/PART2 && ./run_part2.sh
```

Renders the per-dataset PSNR-vs-bitrate and SSIM-vs-bitrate curves and the CESM
CLDHGH visual comparison. The MILIO-o curve lies above cuZFP at every bitrate;
for CESM CLDHGH the visual panels read, for example:

```
cuZFP   CR=8.00  PSNR=41.6  SSIM=0.962
MILIO-o CR=8.06  PSNR=67.5  SSIM=1.000
cuZFP   CR=16.0  PSNR=21.5  SSIM=0.720   (block artifacts)
MILIO-o CR=16.03 PSNR=35.0  SSIM=0.882   (faithful)
```

### 2.3 Ratio accuracy — Table III, Figures 13 and 19

```bash
cd ADAE/PART3 && ./run_part3.sh
```

Emits Table III, the HACC target-vs-achieved ratio trend across its six fields
(Figure 13), and the per-dataset profiled-vs-true error-bound density panels
(Figure 19). Each achieved ratio sits close to its target column; at *R* = 4,
for example, the achieved ratios (MILIO-p / MILIO-o) are:

```
HACC 4.03/4.13   CESM 4.06/4.17   EXAFEL 4.12/4.14
NYX  4.02/4.21   QMCPack 4.11/4.11 SCALE 4.06/4.02
EXAALT 4.03/4.30 RTM 4.01/4.06    SYNTHESIS 3.42/3.47
```
