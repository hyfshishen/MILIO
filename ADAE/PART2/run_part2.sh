#!/bin/bash
# =============================================================================
# ADAE — PART 2: Rate-distortion (quality) evaluation (one-click reproduction)
#
# Builds the fixed-ratio CLIs, then produces two quality artifacts:
#   1. Rate-distortion curves (PSNR / SSIM vs bitrate) for MILIO-o vs cuZFP:
#        results/benchmark_charts/chart_rd_<DATASET>.pdf
#        results/benchmark_charts/chart_ssim_<DATASET>.pdf
#   2. The visual reconstruction comparison on CESM CLDHGH (paper Fig. 15):
#        results/benchmark_charts/chart_visual_comparison.pdf
#
# Usage:
#   ./run_part2.sh              # build + run sweeps + plot
#   ./run_part2.sh --plot-only  # only re-render figures from existing logs/data
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

PART2_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$PART2_DIR/../.." && pwd)"
SCRIPTS="$PART2_DIR/scripts"
OUT="$PART2_DIR/results"
mkdir -p "$OUT/benchmark_charts"

PLOT_ONLY=0
[[ "${1:-}" == "--plot-only" ]] && PLOT_ONLY=1

echo "== ADAE PART2 =="
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
  echo "== [1/5] Building fixed-ratio CLIs =="
  mkdir -p "$REPO_ROOT/build"
  ( cd "$REPO_ROOT/build" && cmake -DCMAKE_BUILD_TYPE=Release .. >/dev/null && \
    make -j"$(nproc)" cuszp_fixed_ratio_cli cuszp_fixed_ratio_cli_2d cuszp_fixed_ratio_cli_3d )

  # ---- 2. Site-configure the sweep drivers (non-destructive copies) -------
  echo "== [2/5] Configuring the sweep drivers for this site =="
  TMP="$PART2_DIR/.tmp_scripts"; mkdir -p "$TMP"
  for s in run_rd_comparison.py run_visual_comparison.py; do
    sed -e "s#/scratch/bfrq/bzhang28#$DATA_ROOT#g" \
        -e "s#/u/bzhang28/zfp/build/bin/zfp#$ZFP_EXE#g" \
        -e "s#bfrq-delta-gpu#$SLURM_ACCOUNT#g" \
        -e "s#gpuA100x4#$SLURM_PARTITION#g" \
        "$SCRIPTS/$s" > "$TMP/$s"
  done

  # ---- 3. Run the rate-distortion sweep (single-GPU Slurm job) ------------
  echo "== [3/5] Running MILIO + cuZFP ratio sweep (targets 2..32) =="
  ( cd "$REPO_ROOT" && python3 "$TMP/run_rd_comparison.py" )
  require_results "$REPO_ROOT/benchmark_rd_comparison.log" \
                  "psnr=" "rate-distortion sweep"
  cp "$REPO_ROOT/benchmark_rd_comparison.log" "$OUT/"

  # ---- 4. Generate the four Fig. 15 reconstructions -----------------------
  echo "== [4/5] Generating CESM CLDHGH reconstructions (cuZFP/MILIO-o, CR 8 & 16) =="
  ( cd "$REPO_ROOT" && FIG15_WORK="$OUT/fig15_data" python3 "$TMP/run_visual_comparison.py" )
  cp "$REPO_ROOT/benchmark_visual_comparison.log" "$OUT/" 2>/dev/null || true
fi

# ---- 5. Render every figure -----------------------------------------------
echo "== [5/5] Rendering figures =="
if [[ ! -f "$OUT/benchmark_rd_comparison.log" ]]; then
  echo "ERROR: $OUT/benchmark_rd_comparison.log not found (run without --plot-only first)." >&2
  exit 1
fi
( cd "$OUT" && python3 "$SCRIPTS/plot_rd_comparison.py" )

if [[ -f "$OUT/fig15_data/milio_cr8.dat" ]]; then
  # label panels with the actually-achieved MILIO ratios
  [[ -f "$OUT/fig15_data/fig15_cr.env" ]] && source "$OUT/fig15_data/fig15_cr.env"
  ( cd "$OUT" && FIG15_DATA="$OUT/fig15_data" \
      FIG15_CR_MILIO8="${FIG15_CR_MILIO8:-8.03}" \
      FIG15_CR_MILIO16="${FIG15_CR_MILIO16:-15.99}" \
      python3 "$SCRIPTS/plot_visual_comparison.py" )
else
  echo "NOTE: $OUT/fig15_data reconstructions not found; skipping visual comparison." >&2
fi

echo "== Done. Figures: =="
ls -1 "$OUT/benchmark_charts/"*.pdf
