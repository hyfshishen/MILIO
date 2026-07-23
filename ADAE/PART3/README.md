# ADAE — Part 3: Error-Bound Accuracy Evaluation

One-click reproduction of the two error-bound accuracy artifacts:

1. **TABLE III** — the compression ratios MILIO actually achieves under the
   target ratios `R = 4, 6, 8`, together with the error bound the
   sampling-guided selection picked for each target, for both MILIO-p (plain)
   and MILIO-o (outlier).
2. The per-dataset **error-bound density** figures used in the paper.

## What it produces

`./run_part3.sh` writes into `results/`:

| Output | Content |
| --- | --- |
| `table3.md` / `table3.tex`                       | TABLE III (Markdown + LaTeX) |
| `benchmark_charts/chart_eb_density_<DATASET>.pdf` | Error-bound density per dataset (9 datasets) |

`<DATASET>` is one of CESM, NYX, HACC, EXAFEL, QMCPACK, RTM, SYNTHESIS, EXAALT,
SCALE. Pre-generated copies are already in `results/`.

In TABLE III the achieved ratio is shown in **bold** and the *error-bound*
column is the relative error bound (RelEB) selected by the profiling sweep.

## Requirements

Same as Part 1: Linux + NVIDIA A100, CUDA ≥ 11.0, CMake ≥ 3.21, GCC ≥ 7.3,
Python 3 with `numpy`/`matplotlib`, a Slurm single-GPU partition, and the
SDRBench datasets under one directory. (Part 3 needs no cuZFP binary.)

## How to run

```bash
export DATA_ROOT=/path/to/SDRBench
export SLURM_ACCOUNT=your-account
export SLURM_PARTITION=your-a100-partition

./run_part3.sh                # build + run both sweeps + regenerate table & figures
./run_part3.sh --plot-only    # regenerate table & figures from the existing logs (no GPU)
```

## What the script does

1. Builds the fixed-ratio CLIs (`cuszp_fixed_ratio_cli{,_2d,_3d}`) and the
   error-bound sweep tool (`cuSZp_all_eb_check`).
2. Runs the MILIO fixed-ratio benchmark at targets `R = 4, 6, 8` for every
   dataset/field (this is the data behind TABLE III).
3. Runs the error-bound accuracy sweep, which evaluates 128 error bounds per
   field (this is the data behind the density figures).
4. Regenerates `table3.md` / `table3.tex` and the per-dataset
   `chart_eb_density_<DATASET>.pdf` figures.

The raw sweep outputs are saved to `results/benchmark_fixratio_warmup_output.log`
and `results/benchmark_eb_accuracy_output.log`.

## Expected results

MILIO's achieved ratios land at (or very close to) each target `R`, and the
selected error bound grows monotonically as the target ratio increases —
i.e. the sampling-guided selection reliably hits the requested ratio.
