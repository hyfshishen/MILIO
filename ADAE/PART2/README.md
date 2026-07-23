# ADAE — Part 2: Rate-Distortion (Quality) Evaluation

One-click reproduction of the rate-distortion figures: reconstruction quality
(PSNR) versus bitrate for MILIO fixed-ratio compression compared with the cuZFP
baseline, across all datasets.

## What it produces

`./run_part2.sh` renders into `results/benchmark_charts/`:

| Figure | Content |
| --- | --- |
| `chart_rd_<DATASET>.pdf`        | PSNR vs bitrate, MILIO-o vs cuZFP (5 datasets) |
| `chart_ssim_<DATASET>.pdf`      | SSIM vs bitrate, MILIO-o vs cuZFP (5 datasets) |
| `chart_visual_comparison.pdf`   | Visual reconstruction comparison on CESM CLDHGH (paper Fig. 15) |

For the rate-distortion curves `<DATASET>` is one of NYX, SYNTHESIS, QMCPACK,
CESM, RTM. SSIM is derived from PSNR via the empirical relation
`SSIM = 1 - 0.5 * 10^(-(PSNR-30)/25)`; `bitrate = 32 / compression_ratio`
(bits per value).

The visual comparison shows the original CESM CLDHGH field (`CLDHGH_1_1800_3600`
from the SDRBench `SDRBENCH-CESM-ATM-1800x3600` archive) next to cuZFP and
MILIO-o reconstructions at CR ≈ 8 and CR ≈ 16, in the `magma` colormap with a
zoom inset per panel; the PSNR/SSIM printed under each panel are computed
directly from the reconstructed field (SSIM is the standard Wang et al. metric
with an 11-tap Gaussian window).

Each compressor runs in its natural mode. MILIO is a 1D streaming compressor, so
it is invoked through the 1D CLI with only the element count (`-n 6480000`, no
logical shape) and dumps its reconstruction via `-D`. cuZFP is a block-transform
compressor that needs the 2D shape, so it is given the field's labelled
dimensions (`zfp -2 1800 3600 -i ... -o ...`). On this field cuZFP degrades
sharply at CR 16 (block artifacts) while MILIO-o stays faithful — reproducing
the paper's figure.

`chart_visual_comparison.pdf` ships pre-generated in `results/benchmark_charts/`.
A full `run_part2.sh` regenerates it from freshly-produced reconstructions; the
large reconstruction arrays under `results/fig15_data/` are git-ignored (25 MB
each) and are recreated on each full run, so `--plot-only` keeps the shipped PDF
rather than re-rendering this figure.

## Requirements

Same as Part 1: Linux + NVIDIA A100, CUDA ≥ 11.0, CMake ≥ 3.21, GCC ≥ 7.3,
Python 3 with `numpy`/`matplotlib`, a Slurm single-GPU partition, the cuZFP
`zfp` binary, and the SDRBench datasets under one directory.

## How to run

```bash
export DATA_ROOT=/path/to/SDRBench
export ZFP_EXE=/path/to/zfp/build/bin/zfp
export SLURM_ACCOUNT=your-account
export SLURM_PARTITION=your-a100-partition

./run_part2.sh                # build + run the ratio sweep + render figures
./run_part2.sh --plot-only    # re-render from the existing log (no GPU needed)
```

## What the script does

1. Builds the fixed-ratio CLIs (`cuszp_fixed_ratio_cli{,_2d,_3d}`).
2. For each dataset, sweeps target compression ratios (2, 3, 4, 5, 6, 7, 8, 10,
   16, 32) with MILIO (`-m outlier`, sampling rate 100) and cuZFP at the
   matching rate (`rate = 32 / ratio`), recording the achieved ratio and PSNR.
3. Generates the four CESM CLDHGH reconstructions for the visual comparison
   (cuZFP and MILIO-o at CR 8 and 16): MILIO via the 1D CLI (`-n 6480000`, `-D`
   to dump the reconstruction), cuZFP via `zfp -2 1800 3600 -i ... -o ...`.
4. Renders the per-dataset PSNR- and SSIM-vs-bitrate figures and the visual
   comparison figure.

The raw sweep outputs are saved to `results/benchmark_rd_comparison.log` and
`results/benchmark_visual_comparison.log`; the reconstructions and the achieved
MILIO ratios live under `results/fig15_data/`.

## Expected results

MILIO-o achieves higher reconstruction quality (PSNR) than cuZFP at every
bitrate on all datasets, i.e. better quality at the same rate. In the visual
comparison, MILIO-o's reconstruction stays visually faithful to the original at
both CR 8 and CR 16, while cuZFP shows visible block artifacts — especially in
the zoom inset at CR 16.
