#!/usr/bin/env python3
import argparse
import subprocess
import re
import os
import datetime
import pandas as pd
from typing import List

# Match lines in the profiling table:  idx  EB  bytes  ratio
RE_TABLE_LINE = re.compile(r'^\s*(\d+)\s+([0-9.eE+\-]+)\s+(\d+)\s+([0-9.]+)\s*$')

def run_cmd(cmd: List[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.stdout

def parse_fixratio_table(output: str) -> pd.DataFrame:
    """Return a DataFrame with columns: EB_idx, EB, bytes, pred_ratio."""
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

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Dump all 128 profiling EBs (idx, EB, bytes, predicted ratio) per dataset with S=100."
    )
    ap.add_argument("--datasets", type=str, nargs="+", required=True, help="List of .f32 datasets")
    ap.add_argument("--fixratio-exe", type=str, default="./cuSZp_fixratio", help="Path to cuSZp_fixratio")
    ap.add_argument("--ratio-for-profiling", type=float, default=4.0, help="Dummy -R for cuSZp_fixratio")
    ap.add_argument("--extra-fixratio", type=str, nargs="*", default=[], help="Extra flags passed to cuSZp_fixratio")
    ap.add_argument("--csv", type=str, default=None, help="Output CSV (combined). Default ./eb_full_<ts>.csv")
    args = ap.parse_args(argv)

    all_rows = []
    for dataset in args.datasets:
        # dataset path minus /home/bohan
        ds_rel = os.path.relpath(dataset, "/home/bohan")

        # Run once with S=100
        cmd = [args.fixratio_exe, "-i", dataset, "-R", str(args.ratio_for_profiling), "-S", "100"] + (args.extra_fixratio or [])
        out = run_cmd(cmd)
        df = parse_fixratio_table(out)

        if not df.empty:
            df.insert(0, "dataset", ds_rel)
            df.insert(1, "S", 100)
            all_rows.append(df)
        else:
            all_rows.append(pd.DataFrame(
                [{"dataset": ds_rel, "S": 100, "EB_idx": None, "EB": None, "bytes": None, "pred_ratio": None}],
                columns=["dataset", "S", "EB_idx", "EB", "bytes", "pred_ratio"]
            ))

    out_df = pd.concat(all_rows, ignore_index=True)
    out_df = out_df.sort_values(by=["dataset", "S", "EB_idx"], kind="stable")

    if args.csv is None:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        args.csv = f"./eb_full_{ts}.csv"

    out_df.to_csv(args.csv, index=False)
    print(out_df.to_csv(index=False).rstrip())
    print(f"Saved results to: {args.csv}")
    return 0

if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))





"""
python run_experiment_barchly-range-2.py \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --datasets \
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
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/Z3_1_26_1800_3600.f32 \
    /home/bohan/SDRBENCH-exaalt-copper/dataset1-5423x3137.x.f32.dat \
    /home/bohan/SDRBENCH-exaalt-copper/dataset1-5423x3137.z.f32.dat \
    /home/bohan/SDRBENCH-exaalt-copper/dataset1-5423x3137.y.f32.dat \
    /home/bohan/SDRBENCH-exaalt-copper/dataset2-83x1077290.x.f32.dat \
    /home/bohan/SDRBENCH-exaalt-copper/dataset2-83x1077290.y.f32.dat \
    /home/bohan/SDRBENCH-exaalt-copper/dataset2-83x1077290.z.f32.dat \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 \
    /home/bohan/SDRBENCH-EXAFEL-130x1480x1552/SDRBENCH-EXAFEL-data-130x1480x1552.f32\
    /home/bohan/synthetic_truss_with_five_defects_1200x1200x1200_float32.raw\
    /home/bohan/jicf_q_1408x1080x1100_float32.raw
    
        

"""