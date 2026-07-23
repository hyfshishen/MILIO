#!/usr/bin/env python3
import argparse
import subprocess
import re
import os
import datetime
import pandas as pd
from typing import List, Dict, Tuple, Optional

# ---------- regexes (robust to spacing) ----------
RE_TABLE_LINE      = re.compile(r'^\s*(\d+)\s+([0-9.eE+\-]+)\s+(\d+)\s+([0-9.]+)\s*$')
RE_TOTAL_WARPS     = re.compile(r'total_warps\s*=\s*(\d+)', re.IGNORECASE)
RE_FINAL_ROW_IDX   = re.compile(r'final_row_idx\s*=\s*(\d+)', re.IGNORECASE)
RE_COMPRESS_RATIO  = re.compile(r'(?:\[compress\].*ratio=|ratio\s*[:=]\s*)([0-9.]+)')

def run_cmd(cmd: List[str]) -> str:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.stdout

def parse_fixratio_table(output: str) -> Tuple[pd.DataFrame, Optional[int], Optional[int]]:
    """Parse the profiling table printed by cuSZp_fixratio.
       Returns (df_table, total_warps, final_row_idx) where df_table has columns:
       EB_idx, EB, bytes, pred_ratio
    """
    rows = []
    for line in output.splitlines():
        m = RE_TABLE_LINE.match(line)
        if m:
            eb_idx = int(m.group(1))
            eb_val = float(m.group(2))
            bytes_ = int(m.group(3))
            ratio  = float(m.group(4))
            rows.append((eb_idx, eb_val, bytes_, ratio))
    df = pd.DataFrame(rows, columns=["EB_idx", "EB", "bytes", "pred_ratio"])

    total_warps = None
    final_row_idx = None
    m = RE_TOTAL_WARPS.search(output)
    if m:
        total_warps = int(m.group(1))
    m = RE_FINAL_ROW_IDX.search(output)
    if m:
        final_row_idx = int(m.group(1))
    return df, total_warps, final_row_idx

def find_pred_ratio_for_eb(df_table: pd.DataFrame, eb_target: float) -> Tuple[Optional[int], Optional[float], Optional[float]]:
    """Find the nearest EB in the table to eb_target.
       Returns (EB_idx, EB_in_table, pred_ratio). If df is empty, returns Nones.
    """
    if df_table.empty:
        return None, None, None
    diffs = (df_table["EB"] - eb_target).abs()
    best_i = diffs.idxmin()
    return int(df_table.loc[best_i, "EB_idx"]), float(df_table.loc[best_i, "EB"]), float(df_table.loc[best_i, "pred_ratio"])

def parse_actual_ratio(output: str) -> Optional[float]:
    m = RE_COMPRESS_RATIO.search(output)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None

def main(argv=None):
    ap = argparse.ArgumentParser(description="Probe predicted vs actual compression ratio for chosen relative EBs across multiple datasets and S values.")
    ap.add_argument("--datasets", type=str, nargs="+", required=True, help="List of .f32 datasets")
    ap.add_argument("--S", type=int, nargs="+", required=True, help="One or more S values for cuSZp_fixratio (-S)")
    ap.add_argument("--ebs", type=str, required=True, help="Comma-separated relative EBs, e.g. '1e-2,1e-3,1e-4'")
    ap.add_argument("--fixratio-exe", type=str, default="./cuSZp_fixratio", help="Path to cuSZp_fixratio executable")
    ap.add_argument("--compress-exe", type=str, default="/home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp", help="Path to cuSZp executable")
    ap.add_argument("--ratio-for-profiling", type=float, default=4.0, help="Dummy -R used when calling cuSZp_fixratio")
    ap.add_argument("--extra-fixratio", type=str, nargs="*", default=[], help="Extra passthrough flags to cuSZp_fixratio")
    ap.add_argument("--extra-compress", type=str, nargs="*", default=[], help="Extra passthrough flags to cuSZp")
    ap.add_argument("--csv-table-dir", type=str, default=None, help="Optional dir to save full EB tables per (dataset,S). If omitted, skip saving tables.")
    ap.add_argument("--csv", type=str, default=None, help="Output CSV for requested EB results (default: ./eb_results_<ts>.csv)")
    args = ap.parse_args(argv)

    eb_list = [float(x) for x in args.ebs.split(",") if x.strip()]
    results_rows = []

    # iterate datasets × S
    for dataset in args.datasets:
        ds_base = os.path.basename(dataset)
        for S in args.S:
            # 1) profile once for this dataset+S
            cmd_fix = [args.fixratio_exe, "-i", dataset, "-R", str(args.ratio_for_profiling), "-S", str(S)] + (args.extra_fixratio or [])
            out_fix = run_cmd(cmd_fix)
            df_table, _, _ = parse_fixratio_table(out_fix)

            # optionally save full table
            if args.csv_table_dir:
                os.makedirs(args.csv_table_dir, exist_ok=True)
                table_path = os.path.join(args.csv_table_dir, f"eb_table_{ds_base}_S{S}.csv")
                df_out = df_table.copy()
                df_out.insert(0, "dataset", ds_base)
                df_out.insert(1, "S", S)
                df_out.to_csv(table_path, index=False)

            # 2) for each requested EB: predicted (from table) + actual (run cuSZp)
            for eb in eb_list:
                eb_idx, eb_snap, pred_ratio = find_pred_ratio_for_eb(df_table, eb)
                cmd_cmp = [args.compress_exe, "-i", dataset, "-t", "f32", "-m", "plain", "-eb", "rel", f"{eb}"] + (args.extra_compress or [])
                out_cmp = run_cmd(cmd_cmp)
                actual_ratio = parse_actual_ratio(out_cmp)

                results_rows.append({
                    "dataset": ds_base,
                    "S": S,
                    "EB_requested": eb,
                    "EB_snap_from_table": eb_snap,
                    "pred_ratio": pred_ratio,
                    "actual_ratio": actual_ratio
                })

    # build combined CSV
    df_res = pd.DataFrame(results_rows, columns=["dataset", "S", "EB_requested", "EB_snap_from_table", "pred_ratio", "actual_ratio"])
    df_res = df_res.sort_values(by=["dataset", "S", "EB_requested"], kind="stable")

    if args.csv is None:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        args.csv = f"./eb_results_{ts}.csv"
    df_res.to_csv(args.csv, index=False)

    # also print a concise CSV to stdout
    print(df_res.to_csv(index=False).rstrip())
    print(f"Saved results to: {args.csv}")
    return 0

if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))

"""
python run_experiment_batchly-ratio.py \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --dataset \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 \
  --S 100 250\
  --ebs 1e-2,1e-3

  """