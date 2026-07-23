#!/usr/bin/env python3
import argparse
import subprocess
import re
import os
import datetime
import pandas as pd
from typing import List, Dict, Tuple, Optional

# ---- regexes ----
RE_TABLE_LINE    = re.compile(r'^\s*(\d+)\s+([0-9.eE+\-]+)\s+(\d+)\s+([0-9.]+)\s*$')
RE_PICK_LINE     = re.compile(r'pick\s+EB_idx=(\d+)\s+relEB=([0-9.eE+\-]+)', re.IGNORECASE)
RE_COMPRESS_LINE = re.compile(r'\[compress\].*ratio=([0-9.]+)')

def parse_output(text: str) -> Tuple[Optional[int], Optional[float], Dict[int, float], Optional[float]]:
    """Return best_idx, relEB_best, {idx:pred_ratio}, actual_ratio."""
    best_idx: Optional[int] = None
    relEB_best: Optional[float] = None
    actual_ratio: Optional[float] = None
    table_ratios_by_idx: Dict[int, float] = {}

    for line in text.splitlines():
        m = RE_TABLE_LINE.match(line)
        if m:
            eb_idx = int(m.group(1))
            ratio  = float(m.group(4))
            table_ratios_by_idx[eb_idx] = ratio

    m = RE_PICK_LINE.search(text)
    if m:
        best_idx   = int(m.group(1))
        relEB_best = float(m.group(2))

    m = RE_COMPRESS_LINE.search(text)
    if m:
        actual_ratio = float(m.group(1))

    return best_idx, relEB_best, table_ratios_by_idx, actual_ratio

def run_once(exe: str, dataset: str, target_R: float, extra_args: List[str], S: Optional[int] = None):
    cmd = [exe, "-i", dataset, "-R", str(target_R)] + (extra_args or [])
    if S is not None:
        cmd += ["-S", str(S)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = proc.stdout

    best_idx, relEB_best, table_ratios_by_idx, actual_ratio = parse_output(out)
    pred_ratio = table_ratios_by_idx.get(best_idx) if best_idx is not None else None

    return {
        "dataset": os.path.basename(dataset),
        "target_R": float(target_R),
        "S": S,
        "relEB_used": relEB_best,
        "pred_ratio": pred_ratio,
        "actual_ratio": actual_ratio,
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description="Batch runner for cuSZp_fixratio with S sweep; outputs tidy CSV.")
    parser.add_argument("--exe", type=str, default="./cuSZp_fixratio", help="Path to cuSZp_fixratio executable")
    parser.add_argument("--datasets", type=str, nargs="+", required=True, help="List of dataset .f32 files")
    parser.add_argument("--ratios", type=float, nargs="+", required=True, help="Target -R values (e.g., 4 6 8)")
    parser.add_argument("--S", type=int, nargs="*", default=None, help="Values for -S to sweep (e.g., 100 250 500 ...)")
    parser.add_argument("--extra", type=str, nargs="*", default=[], help="Extra flags for the executable (e.g., -x out.cmp -o out.dec)")
    parser.add_argument("--csv", type=str, default=None, help="Output CSV (default: ./mnt/data/cuszp_fixratio_results_<ts>.csv)")
    args = parser.parse_args(argv)

    rows = []
    S_list = args.S if args.S else [None]

    for ds in args.datasets:
        for r in args.ratios:
            for s in S_list:
                try:
                    rows.append(run_once(args.exe, ds, r, args.extra, s))
                except Exception as e:
                    rows.append({
                        "dataset": os.path.basename(ds),
                        "target_R": float(r),
                        "S": s,
                        "relEB_used": None,
                        "pred_ratio": None,
                        "actual_ratio": None,
                    })

    # Build dataframe with exactly the requested columns
    cols = ["dataset", "target_R", "S", "relEB_used", "pred_ratio", "actual_ratio"]
    df = pd.DataFrame(rows, columns=cols)

    # Order target_R as 4 -> 6 -> 8 (others after numerically), and sort by dataset, target_R, then S
    df["target_R"] = pd.to_numeric(df["target_R"], errors="coerce")

    df = df.sort_values(by=["dataset", "target_R", "S"], kind="stable")

    # Output path
    if args.csv is None:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        args.csv = f"./mnt/data/cuszp_fixratio_results_{ts}.csv"
    df.to_csv(args.csv, index=False)
    print(f"Saved results to: {args.csv}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

"""
python run_experiment_batchly.py \
  --exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --datasets \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/PRES-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/QG-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/QR-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/QV-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/T-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/V-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/QC-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/QI-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/QS-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/RH-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/U-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/W-98x1200x1200.f32 \
    /home/bohan/SDRBENCH-QMCPack/dataset/115x69x69x288/einspline_115_69_69_288.f32 \
    /home/bohan/SDRBENCH-QMCPack/dataset/288x115x69x69/einspline_288_115_69_69.pre.f32 \
    /home/bohan/1billionparticles_onesnapshot/vx.f32 \
    /home/bohan/1billionparticles_onesnapshot/vy.f32 \
    /home/bohan/1billionparticles_onesnapshot/vz.f32 \
    /home/bohan/1billionparticles_onesnapshot/xx.f32 \
    /home/bohan/1billionparticles_onesnapshot/yy.f32 \
    /home/bohan/1billionparticles_onesnapshot/zz.f32 \
  --ratios 4 6 8 \
  --S 100 250 500 1000 2000 5000 10000 50000 100000 500000 1000000



python run_experiment_batchly.py \
  --exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --datasets \
    /home/bohan/SDRBENCH-QMCPack/dataset/115x69x69x288/einspline_115_69_69_288.f32 \
    /home/bohan/SDRBENCH-QMCPack/dataset/288x115x69x69/einspline_288_115_69_69.pre.f32 \
  --ratios 4 6 8 \
  --S 100 250 500 1000 2000 5000 10000 50000 100000 500000 1000000


"""