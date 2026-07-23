#!/usr/bin/env python3
import argparse
import subprocess
import re
import os
import datetime
import pandas as pd
from typing import List, Tuple, Optional

# Parse profiling table lines: "idx  EB  bytes  ratio"
RE_TABLE_LINE      = re.compile(r'^\s*(\d+)\s+([0-9.eE+\-]+)\s+(\d+)\s+([0-9.]+)\s*$')
# Parse actual compression ratio from cuSZp output
RE_COMPRESS_RATIO  = re.compile(r'(?:\[compress\].*ratio=|ratio\s*[:=]\s*)([0-9.]+)')

def run_cmd(cmd: List[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.stdout

def parse_fixratio_table(output: str) -> pd.DataFrame:
    """Return DataFrame: EB_idx, EB, bytes, pred_ratio."""
    rows = []
    for line in output.splitlines():
        m = RE_TABLE_LINE.match(line)
        if m:
            rows.append((
                int(m.group(1)),       # EB_idx
                float(m.group(2)),     # EB
                int(m.group(3)),       # bytes
                float(m.group(4)),     # pred_ratio
            ))
    return pd.DataFrame(rows, columns=["EB_idx", "EB", "bytes", "pred_ratio"])

def parse_actual_ratio(output: str) -> Optional[float]:
    m = RE_COMPRESS_RATIO.search(output)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None

def profile_dataset(fixratio_exe: str, dataset: str, R_profile: float, S: int, extra_fix: List[str]) -> pd.DataFrame:
    """Run cuSZp_fixratio once to get the 128-row profiling table."""
    cmd = [fixratio_exe, "-i", dataset, "-R", str(R_profile), "-S", str(S)] + (extra_fix or [])
    out = run_cmd(cmd)
    return parse_fixratio_table(out)

def actual_ratio_for_eb(compress_exe: str, dataset: str, eb: float, extra_cmp: List[str]) -> Optional[float]:
    """Run cuSZp once at a given relative EB and parse the actual ratio."""
    cmd = [compress_exe, "-i", dataset, "-t", "f32", "-m", "plain", "-eb", "rel", f"{eb}"] + (extra_cmp or [])
    out = run_cmd(cmd)
    return parse_actual_ratio(out)

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Average predicted vs actual compression ratio over multiple datasets for all 128 EBs (S fixed)."
    )
    ap.add_argument("--datasets", type=str, nargs="+", required=True,
                    help="List of .f32 datasets (full paths).")
    ap.add_argument("--fixratio-exe", type=str, default="/home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio",
                    help="Path to cuSZp_fixratio.")
    ap.add_argument("--compress-exe", type=str, default="/home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp",
                    help="Path to cuSZp.")
    ap.add_argument("--ratio-for-profiling", type=float, default=4.0,
                    help="Dummy -R used when running cuSZp_fixratio.")
    ap.add_argument("--S", type=int, default=100,
                    help="S value used for profiling (default 100).")
    ap.add_argument("--extra-fixratio", type=str, nargs="*", default=[],
                    help="Extra flags passed to cuSZp_fixratio.")
    ap.add_argument("--extra-compress", type=str, nargs="*", default=[],
                    help="Extra flags passed to cuSZp.")
    ap.add_argument("--csv", type=str, default=None,
                    help="Output CSV path; default ./eb_avg_<timestamp>.csv")
    args = ap.parse_args(argv)

    datasets = args.datasets
    S = args.S

    # 1) Profile first dataset to get the canonical EB grid/order (128 rows)
    first_table = profile_dataset(args.fixratio_exe, datasets[0], args.ratio_for_profiling, S, args.extra_fixratio)
    if first_table.empty:
        raise RuntimeError("Failed to parse profiling table from first dataset; no rows found.")
    # Sort by EB_idx to be safe
    first_table = first_table.sort_values(by="EB_idx", kind="stable").reset_index(drop=True)

    # Prepare collectors per EB index
    eb_values      = first_table["EB"].tolist()
    pred_collect   = [[] for _ in range(len(first_table))]
    actual_collect = [[] for _ in range(len(first_table))]

    # 2) For each dataset:
    #    - profile to get predicted ratios on the same EB_idx order
    #    - run cuSZp for each EB to get actual ratios
    for ds in datasets:
        # predicted
        df_tbl = profile_dataset(args.fixratio_exe, ds, args.ratio_for_profiling, S, args.extra_fixratio)
        if df_tbl.empty or len(df_tbl) != len(first_table):
            # attempt to align by EB_idx if possible
            df_tbl = df_tbl.sort_values(by="EB_idx", kind="stable").reset_index(drop=True)

        # sanity: if sizes mismatch, skip this dataset
        if len(df_tbl) != len(first_table):
            # skip but warn (printed to stdout)
            print(f"[WARN] Profiling table for {ds} has {len(df_tbl)} rows; expected {len(first_table)}. Skipping dataset.")
            continue

        # For each EB_idx in order, accumulate predicted and actual
        for i, row in df_tbl.iterrows():
            eb = row["EB"]
            pred = row["pred_ratio"]
            pred_collect[i].append(pred)

            # actual for this dataset and EB
            act = actual_ratio_for_eb(args.compress_exe, ds, eb, args.extra_compress)
            if act is not None:
                actual_collect[i].append(act)

    # 3) Average across datasets per EB_idx
    records = []
    for i, eb in enumerate(eb_values):
        preds = pred_collect[i]
        acts  = actual_collect[i]
        pred_avg = sum(preds)/len(preds) if preds else None
        act_avg  = sum(acts)/len(acts)   if acts  else None
        records.append({
            "EB_idx": i,
            "EB": eb,
            "pred_ratio_avg": pred_avg,
            "actual_ratio_avg": act_avg
        })

    out_df = pd.DataFrame.from_records(records, columns=["EB_idx", "EB", "pred_ratio_avg", "actual_ratio_avg"])
    out_df = out_df.sort_values(by="EB_idx", kind="stable")

    # 4) Write CSV
    if args.csv is None:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        args.csv = f"./eb_avg_{ts}.csv"
    out_df.to_csv(args.csv, index=False)

    # Print concise CSV to stdout
    print(out_df.to_csv(index=False).rstrip())
    print(f"Saved results to: {args.csv}")
    return 0

if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))

"""
python test_ground_truth.py \
  --datasets \
    /home/bohan/1billionparticles_onesnapshot/vx.f32 \
    /home/bohan/1billionparticles_onesnapshot/vy.f32 \
    /home/bohan/1billionparticles_onesnapshot/vz.f32 \
    /home/bohan/1billionparticles_onesnapshot/xx.f32 \
    /home/bohan/1billionparticles_onesnapshot/yy.f32 \
    /home/bohan/1billionparticles_onesnapshot/zz.f32 \
  --S 1000 \
  --ratio-for-profiling 4 \
  --csv ./eb_avg_HACC.csv
"""