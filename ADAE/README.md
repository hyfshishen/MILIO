# Artifact Evaluation — MILIO

Reproducibility package for **"From Error-Bounded to Fixed-Ratio: Efficient
Sampling-Guided GPU Lossy Compression"** (system: **MILIO**, built on cuSZp).

The artifact reproduces the core Section IV results with three self-contained,
one-click packages. Each builds the required CUDA binaries, runs its benchmarks
as single-GPU Slurm jobs, and renders the paper's figures/tables. Every part
also ships pre-generated logs and figures and supports `--plot-only` to
re-render **without a GPU or the datasets**.

| Part | Directory | Reproduces | Paper elements |
| --- | --- | --- | --- |
| 1 | [PART1/](PART1/) | Compression/decompression throughput, stage breakdown, profiling overhead | Figs. 10, 11, 12 |
| 2 | [PART2/](PART2/) | Rate–distortion (PSNR/SSIM) + CESM CLDHGH visual comparison | Figs. 14, 15 |
| 3 | [PART3/](PART3/) | Achieved ratios & selected error bounds; per–error-bound accuracy | Table III |

The formal SC Artifact Description / Artifact Evaluation appendix is in
[AD_AE_Appendix.tex](AD_AE_Appendix.tex) (drop-in `\input` for the paper).

## One-time setup

```bash
export DATA_ROOT=/path/to/scientific-datasets   # SDRBench + Open-SciVis fields (FP32)
export ZFP_EXE=/path/to/zfp/build/bin/zfp        # zfp built with -DZFP_WITH_CUDA=ON
export SLURM_ACCOUNT=<your-account>
export SLURM_PARTITION=<your-a100-partition>
```

## Requirements

- Linux + NVIDIA A100 (40 GB), NVIDIA driver + CUDA ≥ 11.0 (paper: 11.8, `-O3`)
- CMake ≥ 3.21, host GCC compatible with the CUDA toolkit (≤ 11 for CUDA 11.8)
- Python 3 with `numpy` and `matplotlib` (no other packages needed)
- A Slurm single-GPU partition; cuZFP (`zfp` with CUDA) for the baseline

## Run

```bash
cd PART1 && ./run_part1.sh        # then PART2, PART3
# or, with no GPU / no datasets, re-render from the shipped logs:
cd PART1 && ./run_part1.sh --plot-only
```

## Expected results (summary)

- **Part 1:** both MILIO modes exceed cuZFP on every dataset for both
  compression and decompression; profiling is a minor fraction of compression
  time.
- **Part 2:** MILIO-o's PSNR is above cuZFP's at every bitrate and its SSIM
  saturates earlier; in the visual comparison, cuZFP shows block artifacts at
  CR ≈ 16 while MILIO-o stays faithful.
- **Part 3:** achieved ratios cluster close to each target (R = 4, 6, 8) with a
  relative error bound reported per run.

See each part's `README.md` for details, and the per-part `results/` directories
for the shipped logs and figures.

> **Note.** The Section V case studies (LLM KV-cache, 3D CFD, multi-GPU scaling)
> require external model checkpoints and a multi-GPU allocation and are outside
> this package, which covers the core claims evaluated in Section IV.
