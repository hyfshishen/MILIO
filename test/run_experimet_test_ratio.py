#!/usr/bin/env python3
"""
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
Run a fixed-ratio compressor at target ratios {4,6,8}, parse cuSZp metrics,
compute true ratios and bpp, save CSV, and print per-R averages.




Example:
  python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs     /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/dark_matter_density.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/baryon_density.f32\
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/temperature.f32 \
    --csv results_fixed_ratio_nyx.csv

  python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs         /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CLDICE_1_26_1800_3600.f32 \
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
    /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/Z3_1_26_1800_3600.f32\
    --csv results_fixed_ratio_CESM-ATM.csv

    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs         /home/bohan/SDRBENCH-QMCPack/dataset/115x69x69x288/einspline_115_69_69_288.f32 \
    /home/bohan/SDRBENCH-QMCPack/dataset/288x115x69x69/einspline_288_115_69_69.pre.f32 \
    --csv results_fixed_ratio_QMCPack.csv

    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs      /home/bohan/1billionparticles_onesnapshot/vx.f32 \
    /home/bohan/1billionparticles_onesnapshot/vy.f32 \
    /home/bohan/1billionparticles_onesnapshot/vz.f32 \
    /home/bohan/1billionparticles_onesnapshot/xx.f32 \
    /home/bohan/1billionparticles_onesnapshot/yy.f32 \
    /home/bohan/1billionparticles_onesnapshot/zz.f32 \
        --csv results_fixed_ratio_hacc.csv

    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs          /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/PRES-98x1200x1200.f32 \
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
        --csv results_fixed_ratio_scale.csv


    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs         /home/bohan/jicf_q_1408x1080x1100_float32.raw \
    --csv results_fixed_ratio_jetlin.csv

    
    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs     /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/GCLDLWP_1_26_1800_3600.f32 \
        /home/bohan/1billionparticles_onesnapshot/vy.f32 \
        /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/PRES-98x1200x1200.f32 \
        /home/bohan/SDRBENCH-QMCPack/dataset/288x115x69x69/einspline_288_115_69_69.pre.f32 \
        /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 \
        /home/bohan/SDRBENCH-exaalt-copper/dataset1-5423x3137.x.f32.dat\
        /home/bohan/SDRBENCH-EXAFEL-130x1480x1552/SDRBENCH-EXAFEL-data-130x1480x1552.f32\
        /home/bohan/pressure_3000\
        /home/bohan/synthetic_truss_with_five_defects_1200x1200x1200_float32.raw\
            --csv results_fixed_ratio_10_dataset.csv

    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/dark_matter_density.f32 \
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/baryon_density.f32\
    /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/temperature.f32 \
    
    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs     /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 \
    --csv results_fixed_ratio_nyx_velocity_x.csv

    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs     /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 \
    --csv results_fixed_ratio_nyx_velocity_y.csv

    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs     /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 \
    --csv results_fixed_ratio_nyx_velocity_z.csv

    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs     /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/temperature.f32 \
    --csv results_fixed_ratio_nyx_temperature.f32.csv

    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs     /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/dark_matter_density.f32 \
    --csv results_fixed_ratio_nyx_dark_matter_density.f32.csv

    python run_experimet_test_ratio.py\
      --compressor /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
      --inputs     /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/baryon_density.f32 \
    --csv results_fixed_ratio_nyx_baryon_density.f32.csv



    



Or with a list file (one path per line):
  python run_fixed_ratio_batch.py --compressor ./cuszp_cli --input-list datasets.txt
"""

import argparse
import csv
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean

DEFAULT_TARGETS = [4, 6, 8]

# ---- argparse ----
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--compressor", required=True,
                   help="Path to compressor executable (e.g., ./cuszp_cli)")
    p.add_argument("--inputs", nargs="*", default=[],
                   help="List of dataset files to compress")
    p.add_argument("--input-list", type=str, default=None,
                   help="Text file containing dataset paths (one per line)")
    p.add_argument("--out-dir", default="cmp_out",
                   help="Directory to place compressed outputs")
    p.add_argument("--targets", type=str, default="25,50,75",
                   help="Comma-separated target ratios (default: 25,50,75)")
    p.add_argument("--dtype-bits", type=int, default=32,
                   help="Datatype bit width of input (default: 32 for float32)")
    p.add_argument("--extra-args", type=str, default="",
                   help="Extra args for compressor, e.g. '--gpu 0 --stream 4'")
    p.add_argument("--csv", default="results_fixed_ratio.csv",
                   help="Output CSV path")
    return p.parse_args()

def read_input_list(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                items.append(s)
    return items

def ensure_dir(d):
    Path(d).mkdir(parents=True, exist_ok=True)

# ---- command build (edit flags here if your CLI differs) ----
def build_cmd(compressor, infile, outfile, target_ratio, extra_args):
    """
    Edit if your CLI uses different flags.
    Assumed:
      - input:  -i
      - output: -o
      - target ratio: -R
    """
    cmd = [
        compressor,
        "-i", str(infile),
        "-o", str(outfile),
        "-R", str(target_ratio),
    ]
    if extra_args:
        cmd += shlex.split(extra_args)
    return cmd

# ---- cuSZp metrics parsing ----
CUSZP_BYTES_LINE = re.compile(
    r"\[compress\]\s*bytes_in\s*=\s*(\d+)\s*bytes_cmp\s*=\s*(\d+)\s*ratio\s*=\s*([0-9.]+)",
    re.IGNORECASE
)
CMP_BYTES_PATTERNS = [
    re.compile(r"cmp[_\s]*bytes\s*[:=]\s*([0-9]+)", re.IGNORECASE),
    re.compile(r"compressed\s*size\s*[:=]\s*([0-9]+)\s*bytes?", re.IGNORECASE),
    re.compile(r"\bcmp\s*=\s*([0-9]+)\b", re.IGNORECASE),
]

def parse_cuszp_metrics(text: str):
    m = CUSZP_BYTES_LINE.search(text)
    if not m:
        return None
    return {
        "bytes_in": int(m.group(1)),
        "bytes_cmp": int(m.group(2)),
        "ratio": float(m.group(3)),
    }

def parse_cmp_bytes_fallback(text: str):
    for pat in CMP_BYTES_PATTERNS:
        m = pat.search(text)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                pass
    return None

def compute_bpp(bytes_in: int, bytes_cmp: int, dtype_bits: int = 32):
    """
    bits per value = compressed_bits / #values
                   = (bytes_cmp * 8) / (bytes_in * 8 / dtype_bits)
                   = bytes_cmp * dtype_bits / bytes_in
    """
    if bytes_in <= 0 or bytes_cmp is None:
        return None
    return (bytes_cmp * dtype_bits) / bytes_in

# ---- single run ----
def run_once(compressor, infile, out_dir, target_ratio, extra_args, dtype_bits):
    in_path = Path(infile)
    if not in_path.exists():
        return {"status": "input_missing", "dataset": infile, "target_R": target_ratio}

    out_path = Path(out_dir) / f"{in_path.name}.R{target_ratio}.cmp"
    cmd = build_cmd(compressor, in_path, out_path, target_ratio, extra_args)

    t0 = time.time()
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError:
        return {"status": "compressor_not_found", "dataset": infile, "target_R": target_ratio}
    elapsed = time.time() - t0

    stdout = proc.stdout.decode(errors="ignore")
    stderr = proc.stderr.decode(errors="ignore")
    status = "ok" if proc.returncode == 0 else f"ret={proc.returncode}"

    # Prefer cuSZp's own metrics
    metrics = parse_cuszp_metrics(stdout) or parse_cuszp_metrics(stderr)

    # Original bytes from filesystem (sanity)
    orig_bytes_fs = in_path.stat().st_size

    if metrics:
        bytes_in = metrics["bytes_in"]
        cmp_bytes = metrics["bytes_cmp"]
        ratio = metrics["ratio"]
        # Fallback sanity if cmp_bytes is suspicious
        if cmp_bytes is None and out_path.exists():
            cmp_bytes = out_path.stat().st_size
            ratio = (bytes_in / cmp_bytes) if cmp_bytes > 0 else None
    else:
        # Try generic cmp size parse
        cmp_bytes = parse_cmp_bytes_fallback(stdout) or parse_cmp_bytes_fallback(stderr)
        if cmp_bytes is None:
            # last resort: stat on-disk output
            if out_path.exists():
                cmp_bytes = out_path.stat().st_size
            else:
                return {
                    "status": f"{status}|no_cmp_size",
                    "dataset": infile,
                    "target_R": target_ratio,
                    "elapsed_s": f"{elapsed:.3f}",
                }
        bytes_in = orig_bytes_fs
        ratio = (bytes_in / cmp_bytes) if cmp_bytes > 0 else None

    bpp = compute_bpp(bytes_in, cmp_bytes, dtype_bits=dtype_bits) if cmp_bytes else None

    return {
        "status": status,
        "dataset": infile,
        "target_R": target_ratio,
        "elapsed_s": f"{elapsed:.3f}",
        "bytes_in": bytes_in,
        "bytes_in_fs": orig_bytes_fs,
        "bytes_cmp": cmp_bytes,
        "ratio": None if ratio is None else float(ratio),
        "bpp": None if bpp is None else float(bpp),
        "out_path": str(out_path),
        "stdout_tail": stdout[-500:],
        "stderr_tail": stderr[-500:],
    }

# ---- main ----
def main():
    args = parse_args()

    targets = [float(x.strip()) for x in args.targets.split(",") if x.strip()]
    if not targets:
        print("No targets provided.", file=sys.stderr)
        sys.exit(2)

    inputs = list(args.inputs)
    if args.input_list:
        inputs += read_input_list(args.input_list)
    inputs = [str(Path(p)) for p in inputs]
    if not inputs:
        print("No input datasets provided.", file=sys.stderr)
        sys.exit(2)

    ensure_dir(args.out_dir)

    rows = []
    for infile in inputs:
        for R in targets:
            res = run_once(args.compressor, infile, args.out_dir, R, args.extra_args, args.dtype_bits)
            rows.append({
                "dataset": res.get("dataset", infile),
                "target_R": res.get("target_R", R),
                "status": res.get("status"),
                "elapsed_s": res.get("elapsed_s", ""),
                "bytes_in": res.get("bytes_in"),
                "bytes_in_fs": res.get("bytes_in_fs"),
                "bytes_cmp": res.get("bytes_cmp"),
                "ratio": res.get("ratio"),
                "bpp": res.get("bpp"),
                "out_path": res.get("out_path", ""),
            })

            # progress
            r_show = res.get("ratio")
            print(f"[{res.get('status')}] R={R:<4} file={Path(infile).name:<30} "
                  f"ratio={(f'{r_show:.4f}' if isinstance(r_show, (int,float)) else 'NA')} "
                  f"time={res.get('elapsed_s','')}s")

    # write CSV
    csv_path = Path(args.csv)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "dataset", "target_R", "status", "elapsed_s",
            "bytes_in", "bytes_in_fs", "bytes_cmp", "ratio", "bpp", "out_path"
        ])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nSaved: {csv_path}")

    # summarize averages by target_R
    by_R_ratio = {}
    by_R_bpp = {}
    counts = {}
    for r in rows:
        if r["status"] == "ok" and isinstance(r["ratio"], (int, float)):
            R = r["target_R"]
            by_R_ratio.setdefault(R, []).append(r["ratio"])
            if isinstance(r.get("bpp"), (int, float)):
                by_R_bpp.setdefault(R, []).append(r["bpp"])
            counts[R] = counts.get(R, 0) + 1

    if counts:
        print("\n=== Averages per Target_R ===")
        print("Target_R   N    Avg_True_Ratio    Avg_BPP")
        for R in sorted(counts):
            avg_ratio = mean(by_R_ratio.get(R, [])) if by_R_ratio.get(R) else float('nan')
            avg_bpp = mean(by_R_bpp.get(R, [])) if by_R_bpp.get(R) else float('nan')
            print(f"{str(R):<10} {counts[R]:<4} {avg_ratio:<16.4f} {avg_bpp:.6g}")
    else:
        print("\nNo successful results to average.")

if __name__ == "__main__":
    main()


