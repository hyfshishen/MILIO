#!/bin/bash
# =============================================================================
# ADAE — PART 3: Error-bound accuracy evaluation (one-click reproduction)
#
# Reproduces the two accuracy artifacts of the paper:
#   1. TABLE III  — achieved compression ratios and the selected error bounds
#                   under target ratios R = 4, 6, 8 for MILIO-p / MILIO-o.
#                   Output: results/table3.md and results/table3.tex
#   2. The per-dataset error-bound density figures:
#                   results/benchmark_charts/chart_eb_density_<DATASET>.pdf
#
# Usage:
#   ./run_part3.sh              # build + run benchmarks + regenerate table & figures
#   ./run_part3.sh --plot-only  # only regenerate table & figures from existing logs
#
# Configuration (override via environment variables):
#   DATA_ROOT         directory holding the SDRBench datasets
#   SLURM_ACCOUNT     Slurm account for the GPU job
#   SLURM_PARTITION   Slurm partition (A100 GPU)
# =============================================================================
set -euo pipefail

DATA_ROOT="${DATA_ROOT:-/scratch/bfrq/bzhang28}"
SLURM_ACCOUNT="${SLURM_ACCOUNT:-bfrq-delta-gpu}"
SLURM_PARTITION="${SLURM_PARTITION:-gpuA100x4}"

PART3_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$PART3_DIR/../.." && pwd)"
SCRIPTS="$PART3_DIR/scripts"
OUT="$PART3_DIR/results"
mkdir -p "$OUT/benchmark_charts"

PLOT_ONLY=0
[[ "${1:-}" == "--plot-only" ]] && PLOT_ONLY=1

echo "== ADAE PART3 =="
echo "  repo      : $REPO_ROOT"
echo "  data root : $DATA_ROOT"
echo "  slurm     : $SLURM_ACCOUNT / $SLURM_PARTITION"
echo "  output    : $OUT"

if [[ "$PLOT_ONLY" -eq 0 ]]; then
  # ---- 1. Build the CLIs and the error-bound sweep tool --------------------
  echo "== [1/4] Building fixed-ratio CLIs + error-bound sweep tool =="
  mkdir -p "$REPO_ROOT/build"
  ( cd "$REPO_ROOT/build" && cmake -DCMAKE_BUILD_TYPE=Release .. >/dev/null && \
    make -j"$(nproc)" cuszp_fixed_ratio_cli cuszp_fixed_ratio_cli_2d \
                      cuszp_fixed_ratio_cli_3d cuSZp_all_eb_check )

  # ---- 2. Site-configure the benchmark drivers (non-destructive copies) ----
  echo "== [2/4] Configuring benchmark drivers for this site =="
  TMP="$PART3_DIR/.tmp_scripts"; mkdir -p "$TMP"
  for s in benchmark_fixratio_all.py benchmark_eb_accuracy.py; do
    sed -e "s#/scratch/bfrq/bzhang28#$DATA_ROOT#g" \
        -e "s#bfrq-delta-gpu#$SLURM_ACCOUNT#g" \
        -e "s#gpuA100x4#$SLURM_PARTITION#g" \
        "$SCRIPTS/$s" > "$TMP/$s"
  done

  # ---- 3. Run the benchmarks (each submits its own single-GPU Slurm job) ---
  echo "== [3/4] Running MILIO fixed-ratio benchmark (TABLE III, R=4,6,8) =="
  ( cd "$REPO_ROOT" && python3 "$TMP/benchmark_fixratio_all.py" )
  echo "== [3/4] Running error-bound accuracy sweep (128 error bounds) =="
  ( cd "$REPO_ROOT" && python3 "$TMP/benchmark_eb_accuracy.py" )

  cp "$REPO_ROOT/benchmark_fixratio_warmup_output.log" "$OUT/"
  cp "$REPO_ROOT/benchmark_eb_accuracy_output.log"      "$OUT/"
fi

# ---- 4. Reproduce TABLE III and render the error-bound density figures -----
echo "== [4/4] Reproducing TABLE III and error-bound density figures =="
if [[ ! -f "$OUT/benchmark_fixratio_warmup_output.log" || ! -f "$OUT/benchmark_eb_accuracy_output.log" ]]; then
  echo "ERROR: benchmark logs not found in $OUT (run without --plot-only first)." >&2
  exit 1
fi
( cd "$OUT" && \
  python3 "$SCRIPTS/generate_table3.py" && \
  python3 "$SCRIPTS/plot_eb_density.py" )

echo "== Done. =="
echo "TABLE III : $OUT/table3.md  (LaTeX: $OUT/table3.tex)"
echo "Figures   :"
ls -1 "$OUT/benchmark_charts/"*.pdf
