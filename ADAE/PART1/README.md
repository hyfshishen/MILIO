# ADAE — Part 1: Throughput Evaluation

One-click reproduction of the throughput figures: MILIO fixed-ratio compression
(outlier `-o` and plain `-p`) versus the cuZFP baseline, across all datasets.

## What it produces

`./run_part1.sh` renders four figures into `results/benchmark_charts/`:

| Figure | Content |
| --- | --- |
| `chart_summary_compression.pdf`   | Compression throughput: MILIO-o / MILIO-p vs cuZFP, per dataset + average |
| `chart_summary_decompression.pdf` | Decompression throughput: MILIO-o / MILIO-p vs cuZFP, per dataset + average |
| `chart_breakdown_millio_o.pdf`    | MILIO-o throughput broken into Profile / Comp. / Total phases |
| `chart_breakdown_millio_p.pdf`    | MILIO-p throughput broken into Profile / Comp. / Total phases |
| `chart_overhead_normalized.pdf`   | Profiling (sampling) time relative to compression, per dataset |
| `chart_rtm_overhead_trend.pdf`    | Profiling overhead trend across the RTM pressure snapshots |

A pre-generated copy of these figures is already in `results/benchmark_charts/`.

## Requirements

- Linux + NVIDIA A100 GPU, CUDA Toolkit ≥ 11.0, CMake ≥ 3.21, GCC ≥ 7.3 (C++17)
- Python 3 with `numpy` and `matplotlib`
- A Slurm cluster with a single-GPU partition (the drivers submit their own `srun` jobs)
- The cuZFP `zfp` binary built with CUDA (`-DZFP_WITH_CUDA=ON`)
- The SDRBench datasets (CESM, NYX, HACC, EXAFEL, QMCPACK, RTM, SYNTHESIS,
  EXAALT, SCALE) downloaded under one directory

## How to run

Point the script at your environment (defaults match the authors' Delta setup):

```bash
export DATA_ROOT=/path/to/SDRBench            # dir holding the datasets
export ZFP_EXE=/path/to/zfp/build/bin/zfp     # cuda-enabled zfp binary
export SLURM_ACCOUNT=your-account
export SLURM_PARTITION=your-a100-partition

./run_part1.sh                # build + run both benchmarks + render figures
```

To only re-render the figures from logs already in `results/` (no GPU needed):

```bash
./run_part1.sh --plot-only
```

## What the script does

1. Builds the fixed-ratio CLIs (`cuszp_fixed_ratio_cli{,_2d,_3d}`).
2. Runs the MILIO fixed-ratio benchmark over all datasets
   (`-m outlier` and `-m plain`, target ratios 4/6/8, sampling rate 1000).
3. Runs the cuZFP baseline over the same datasets at matching rates.
4. Renders the six figures.

Raw logs are saved to `results/benchmark_fixratio_warmup_output.log` and
`results/benchmark_cuzfp_output.log`.

## Expected results

MILIO's compression and decompression throughput is consistently higher than
cuZFP across all datasets, for both the outlier and plain modes.
