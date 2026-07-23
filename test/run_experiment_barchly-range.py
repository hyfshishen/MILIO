#!/usr/bin/env python3
import argparse
import subprocess
import re
import os
import datetime
import pandas as pd
from typing import List, Tuple, Optional

# Regex to match table lines
RE_TABLE_LINE = re.compile(r'^\s*(\d+)\s+([0-9.eE+\-]+)\s+(\d+)\s+([0-9.]+)\s*$')

def run_cmd(cmd: List[str]) -> str:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.stdout

def parse_fixratio_table(output: str) -> pd.DataFrame:
    """Parse the profiling table printed by cuSZp_fixratio."""
    rows = []
    for line in output.splitlines():
        m = RE_TABLE_LINE.match(line)
        if m:
            eb_idx = int(m.group(1))
            eb_val = float(m.group(2))
            bytes_ = int(m.group(3))
            ratio  = float(m.group(4))
            rows.append((eb_idx, eb_val, bytes_, ratio))
    return pd.DataFrame(rows, columns=["EB_idx", "EB", "bytes", "pred_ratio"])

def main(argv=None):
    ap = argparse.ArgumentParser(description="Find min and max predicted compression ratio for each dataset (S=100).")
    ap.add_argument("--datasets", type=str, nargs="+", required=True, help="List of .f32 datasets")
    ap.add_argument("--fixratio-exe", type=str, default="./cuSZp_fixratio", help="Path to cuSZp_fixratio executable")
    ap.add_argument("--ratio-for-profiling", type=float, default=4.0, help="Dummy -R used when calling cuSZp_fixratio")
    ap.add_argument("--extra-fixratio", type=str, nargs="*", default=[], help="Extra passthrough flags to cuSZp_fixratio")
    ap.add_argument("--csv", type=str, default=None, help="Output CSV path")
    args = ap.parse_args(argv)

    results = []
    for dataset in args.datasets:
        ds_base = os.path.basename(dataset)

        # Run cuSZp_fixratio once with S=100
        cmd_fix = [args.fixratio_exe, "-i", dataset, "-R", str(args.ratio_for_profiling), "-S", "100"] + (args.extra_fixratio or [])
        out_fix = run_cmd(cmd_fix)
        df_table = parse_fixratio_table(out_fix)

        if df_table.empty:
            min_ratio, max_ratio = None, None
        else:
            min_ratio = df_table["pred_ratio"].min()
            max_ratio = df_table["pred_ratio"].max()

        results.append({
            "dataset": ds_base,
            "S": 100,
            "min_pred_ratio": min_ratio,
            "max_pred_ratio": max_ratio
        })

    df_res = pd.DataFrame(results, columns=["dataset", "S", "min_pred_ratio", "max_pred_ratio"])

    if args.csv is None:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        args.csv = f"./eb_minmax_{ts}.csv"
    df_res.to_csv(args.csv, index=False)

    print(df_res.to_csv(index=False).rstrip())
    print(f"Saved results to: {args.csv}")

    return 0

if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))


"""
python run_experiment_barchly-range.py \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
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
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CLDICE_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/GCLDLWP_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/RELHUM_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CLDLIQ_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/ICIMR_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/T_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CLOUD_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/ICLDIWP_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/U_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CMFDQ_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/ICLDTWP_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/UU_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CMFDQR_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CWMR_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/V_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CMFDT_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/OMEGA_1_26_1800_3600.f32  \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/VD01_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CONCLD_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/OMEGAT_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/VQ_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/DCQ_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/Q_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/VT_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/DTCOND_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/QC_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/VU_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/DTV_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/QRL_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/VV_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/FICE_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/QRS_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/Z3_1_26_1800_3600.f32
"""