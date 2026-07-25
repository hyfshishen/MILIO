#!/bin/bash
# =============================================================================
# ADAE — PART 1: Throughput evaluation (one-click reproduction)
#
# Builds the fixed-ratio CLIs, runs the full MILIO fixed-ratio benchmark and the
# cuZFP baseline over all datasets, and directly renders the four figures:
#   results/benchmark_charts/chart_summary_compression.pdf     (MILIO-o/p vs cuZFP)
#   results/benchmark_charts/chart_summary_decompression.pdf   (MILIO-o/p vs cuZFP)
#   results/benchmark_charts/chart_breakdown_millio_o.pdf       (Profile/Comp/Total)
#   results/benchmark_charts/chart_breakdown_millio_p.pdf       (Profile/Comp/Total)
#
# Usage:
#   ./run_part1.sh              # build + run benchmarks + plot
#   ./run_part1.sh --plot-only  # only re-render figures from existing logs
#
# Configuration (override via environment variables):
#   DATA_ROOT         directory holding the SDRBench datasets
#   ZFP_EXE           path to the cuZFP `zfp` binary (built with -DZFP_WITH_CUDA)
#   SLURM_ACCOUNT     Slurm account for the GPU job
#   SLURM_PARTITION   Slurm partition (A100 GPU)
# =============================================================================
set -euo pipefail

DATA_ROOT="${DATA_ROOT:-/scratch/bfrq/bzhang28}"
ZFP_EXE="${ZFP_EXE:-/u/bzhang28/zfp/build/bin/zfp}"
SLURM_ACCOUNT="${SLURM_ACCOUNT:-bfrq-delta-gpu}"
SLURM_PARTITION="${SLURM_PARTITION:-gpuA100x4}"

PART1_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$PART1_DIR/../.." && pwd)"
SCRIPTS="$PART1_DIR/scripts"
OUT="$PART1_DIR/results"
mkdir -p "$OUT/benchmark_charts"

PLOT_ONLY=0
[[ "${1:-}" == "--plot-only" ]] && PLOT_ONLY=1

echo "== ADAE PART1 =="
echo "  repo      : $REPO_ROOT"
echo "  data root : $DATA_ROOT"
echo "  zfp       : $ZFP_EXE"
echo "  slurm     : $SLURM_ACCOUNT / $SLURM_PARTITION"
echo "  output    : $OUT"

# Fail loudly if a benchmark's Slurm job produced no results (e.g. a transient
# node Prolog/boot failure) instead of silently rendering empty figures.
require_results() {  # <logfile> <result-regex> <human-readable name>
  if ! grep -qE "$2" "$1" 2>/dev/null; then
    echo "ERROR: $3 produced no results in:" >&2
    echo "         $1" >&2
    echo "       The Slurm GPU job likely failed to run (often a transient node" >&2
    echo "       Prolog/boot failure). Re-run this script to retry." >&2
    exit 1
  fi
}

if [[ "$PLOT_ONLY" -eq 0 ]]; then
  # ---- 1. Build the fixed-ratio CLIs --------------------------------------
  echo "== [1/4] Building fixed-ratio CLIs =="
  mkdir -p "$REPO_ROOT/build"
  ( cd "$REPO_ROOT/build" && cmake -DCMAKE_BUILD_TYPE=Release .. >/dev/null && \
    make -j"$(nproc)" cuszp_fixed_ratio_cli cuszp_fixed_ratio_cli_2d cuszp_fixed_ratio_cli_3d )

  # ---- 2. Site-configure the benchmark drivers (non-destructive copies) ---
  echo "== [2/4] Configuring benchmark drivers for this site =="
  TMP="$PART1_DIR/.tmp_scripts"; mkdir -p "$TMP"
  for s in benchmark_fixratio_all.py benchmark_cuzfp_all.py; do
    sed -e "s#/scratch/bfrq/bzhang28#$DATA_ROOT#g" \
        -e "s#/u/bzhang28/zfp/build/bin/zfp#$ZFP_EXE#g" \
        -e "s#bfrq-delta-gpu#$SLURM_ACCOUNT#g" \
        -e "s#gpuA100x4#$SLURM_PARTITION#g" \
        "$SCRIPTS/$s" > "$TMP/$s"
  done

  # ---- 3. Run the benchmarks (each submits its own single-GPU Slurm job) --
  echo "== [3/4] Running MILIO fixed-ratio benchmark (all datasets) =="
  ( cd "$REPO_ROOT" && python3 "$TMP/benchmark_fixratio_all.py" )
  require_results "$REPO_ROOT/benchmark_fixratio_warmup_output.log" \
                  "Total \(Prof\+Comp\) Thrpt:" "MILIO fixed-ratio benchmark"
  echo "== [3/4] Running cuZFP baseline benchmark (all datasets) =="
  ( cd "$REPO_ROOT" && python3 "$TMP/benchmark_cuzfp_all.py" )
  require_results "$REPO_ROOT/benchmark_cuzfp_output.log" \
                  "psnr=" "cuZFP baseline benchmark"

  cp "$REPO_ROOT/benchmark_fixratio_warmup_output.log" "$OUT/"
  cp "$REPO_ROOT/benchmark_cuzfp_output.log"           "$OUT/"
fi

# ---- 4. Render the four figures ------------------------------------------
echo "== [4/4] Rendering figures =="
if [[ ! -f "$OUT/benchmark_fixratio_warmup_output.log" || ! -f "$OUT/benchmark_cuzfp_output.log" ]]; then
  echo "ERROR: benchmark logs not found in $OUT (run without --plot-only first)." >&2
  exit 1
fi
( cd "$OUT" && \
  python3 "$SCRIPTS/plot_combined_summary.py" && \
  python3 "$SCRIPTS/plot_profiling_breakdown.py" && \
  python3 "$SCRIPTS/plot_overhead_normalized.py" && \
  python3 "$SCRIPTS/plot_rtm_overhead_trend.py" )

echo "== Done. Figures: =="
ls -1 "$OUT/benchmark_charts/"*.pdf
