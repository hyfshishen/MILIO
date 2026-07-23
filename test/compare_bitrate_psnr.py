#!/usr/bin/env python3
import argparse
import subprocess
import re
import os
import math
import numpy as np
import pandas as pd
import datetime
from typing import List, Tuple, Optional

# ---------- regexes ----------
RE_TABLE_LINE      = re.compile(r'^\s*(\d+)\s+([0-9.eE+\-]+)\s+(\d+)\s+([0-9.]+)\s*$')
RE_PICK_LINE       = re.compile(r'pick\s+EB_idx=(\d+)\s+relEB=([0-9.eE+\-]+)', re.IGNORECASE)
RE_COMPRESS_RATIO  = re.compile(r'(?:\[compress\].*ratio=|ratio\s*[:=]\s*)([0-9.]+)')
RE_BYTES_CMP       = re.compile(r'\bbytes_cmp(?:ressed)?\s*=\s*([0-9]+)')  # best effort

def run_cmd(cmd: List[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.stdout

def parse_fixratio_pick_and_ratio(output: str) -> Tuple[Optional[float], Optional[float], Optional[int]]:
    """
    Returns (relEB_used, actual_ratio, cmp_bytes)
    """
    relEB = None
    m = RE_PICK_LINE.search(output)
    if m:
        try:
            relEB = float(m.group(2))
        except Exception:
            relEB = None
    actual_ratio = None
    m = RE_COMPRESS_RATIO.search(output)
    if m:
        try:
            actual_ratio = float(m.group(1))
        except Exception:
            pass
    cmp_bytes = None
    m = RE_BYTES_CMP.search(output)
    if m:
        try:
            cmp_bytes = int(m.group(1))
        except Exception:
            pass
    # fallback: some builds print "[compress] bytes_in=X  bytes_cmp=Y  ratio=Z"
    if cmp_bytes is None:
        # try to recover from that line form
        m2 = re.search(r'\[compress\].*bytes_cmp=([0-9]+)', output)
        if m2:
            try:
                cmp_bytes = int(m2.group(1))
            except Exception:
                pass
    return relEB, actual_ratio, cmp_bytes

def psnr_db(x: np.ndarray, y: np.ndarray, peak_mode: str = "range") -> float:
    """
    PSNR for float arrays. peak_mode:
      - "range": peak = (max(x) - min(x))
      - "maxabs": peak = max(abs(x))
    """
    assert x.dtype == np.float32 and y.dtype == np.float32
    assert x.size == y.size
    diff = x.astype(np.float64) - y.astype(np.float64)
    mse = float(np.mean(diff * diff))
    if mse == 0.0:
        return float("inf")
    if peak_mode == "range":
        peak = float(np.max(x) - np.min(x))
    elif peak_mode == "maxabs":
        peak = float(np.max(np.abs(x)))
    else:
        raise ValueError("peak_mode must be 'range' or 'maxabs'")
    # prevent log of zero if data is constant
    if peak <= 0.0 or not math.isfinite(peak):
        peak = 1.0
    return 20.0 * math.log10(peak) - 10.0 * math.log10(mse)

def read_f32(path: str) -> np.ndarray:
    a = np.fromfile(path, dtype=np.float32)
    return a

def n_elems_from_shape(shape: Tuple[int, ...]) -> int:
    ne = 1
    for s in shape:
        ne *= int(s)
    return ne

def infer_cmp_bpp(cmp_bytes: int, n_elems: int) -> float:
    return (cmp_bytes * 8.0) / float(n_elems)

def cuszp_fixedratio_one(dataset: str,
                         target_R: float,
                         fixratio_exe: str,
                         cuszp_exe: str,
                         out_dec: str,
                         extra_fixratio: List[str],
                         extra_cuszp: List[str]) -> Tuple[Optional[float], Optional[float], Optional[int], str]:
    """
    Run cuSZp_fixratio to get relEB and actual ratio; then run cuSZp with that relEB to produce decompressed out_dec.
    Returns (relEB_used, actual_ratio, cmp_bytes, stdout_all)
    """
    # 1) fixed-ratio run
    cmd_fix = [fixratio_exe, "-i", dataset, "-R", str(target_R)] + (extra_fixratio or [])
    out1 = run_cmd(cmd_fix)
    relEB, actual_ratio, cmp_bytes = parse_fixratio_pick_and_ratio(out1)

    # 2) reconstruct with cuSZp at that relEB (compress+decompress in one go by writing -o)
    if relEB is not None:
        cmd_cuszp = [cuszp_exe, "-i", dataset, "-t", "f32", "-m", "plain", "-eb", "rel", f"{relEB}", "-o", out_dec] + (extra_cuszp or [])
        out2 = run_cmd(cmd_cuszp)
    else:
        out2 = ""

    return relEB, actual_ratio, cmp_bytes, (out1 + "\n---\n" + out2)

def zfp_one(dataset: str,
            shape: Tuple[int, int, int],
            zfp_exe: str,
            rate_bpv: float,
            out_dec: str,
            extra_zfp: List[str]) -> Tuple[Optional[int], str]:
    """
    Run zfp at fixed rate (bits per value), writing decompressed out_dec.
    Uses -h so the compressed stream carries type/dims/params in the header.
    Returns (cmp_bytes, stdout)
    """
    nx, ny, nz = [int(v) for v in shape]
    zcmp = out_dec + ".zfp.cmp"

    # Remove any stale files from prior runs
    for p in (zcmp, out_dec):
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass

    # 1) Compress with header (-h) so decode knows type/dims/params
    #    -f (float), -3 nx ny nz (3D), -i dataset (raw input), -z zcmp (compressed out), -r rate (bits/value)
    cmd_c = [zfp_exe, "-h", "-f", "-3", str(nx), str(ny), str(nz),
             "-i", dataset, "-z", zcmp, "-r", f"{rate_bpv}"] + (extra_zfp or [])
    out_c = run_cmd(cmd_c)

    # Get compressed size for bitrate
    cmp_bytes = None
    try:
        st = os.stat(zcmp)
        cmp_bytes = st.st_size
    except Exception:
        pass

    # 2) Decompress using the header (-h) to recover array to out_dec
    #    -z zcmp (compressed input), -o out_dec (decompressed output)
    cmd_d = [zfp_exe, "-h", "-z", zcmp, "-o", out_dec] + (extra_zfp or [])
    out_d = run_cmd(cmd_d)

    return cmp_bytes, (out_c + "\n---\n" + out_d)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Bitrate vs PSNR: cuSZp fixed-ratio vs ZFP.")
    # Datasets & shapes
    ap.add_argument("--datasets", type=str, nargs="+", required=True, help="List of .f32 datasets")
    ap.add_argument("--shapes", type=str, nargs="+", required=True,
                    help="List of shapes per dataset, like '512,512,512'. Must match --datasets length.")
    # Executables
    ap.add_argument("--fixratio-exe", type=str, default="/home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio", help="Path to cuSZp_fixratio")
    ap.add_argument("--cuszp-exe", type=str, default="/home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp", help="Path to cuSZp (for relEB decode)")
    ap.add_argument("--zfp-exe", type=str, default="/home/bohan/zfp/build/bin/zfp", help="Path to zfp CLI")
    # Sweeps
    ap.add_argument("--ratios", type=float, nargs="+", default=[4,5,6,7,8,16,24,28,32],
                    help="Target R for cuSZp fixed-ratio sweep.")
    ap.add_argument("--zfp-rates", type=float, nargs="*", default=[8,7,6,5,4,3,2,1],
                    help="Optional ZFP rates (bits/value). If omitted, will use the measured cuSZp bitrates rounded.")
    # Options
    ap.add_argument("--psnr-peak", type=str, choices=["range", "maxabs"], default="range", help="PSNR peak mode.")
    ap.add_argument("--strip-prefix", type=str, default="/home/bohan",
                    help="Strip this prefix from dataset paths in CSV.")
    ap.add_argument("--workdir", type=str, default="./_wrk_bpp_psnr", help="Working directory for outputs.")
    ap.add_argument("--extra-fixratio", type=str, nargs="*", default=[], help="Extra args to cuSZp_fixratio")
    ap.add_argument("--extra-cuszp", type=str, nargs="*", default=[], help="Extra args to cuSZp")
    ap.add_argument("--extra-zfp", type=str, nargs="*", default=[], help="Extra args to zfp")
    ap.add_argument("--csv", type=str, default=None, help="Output CSV path")
    args = ap.parse_args(argv)

    if len(args.datasets) != len(args.shapes):
        raise SystemExit("ERROR: --datasets and --shapes must have the same length.")

    os.makedirs(args.workdir, exist_ok=True)

    # Load originals once (also useful for PSNR)
    originals = []
    n_elems_list = []
    for ds in args.datasets:
        a = read_f32(ds)
        originals.append(a)
        n_elems_list.append(a.size)

    results = []
    # ---------- cuSZp fixed-ratio sweep ----------
    measured_bpps: List[float] = []
    for ds_idx, dataset in enumerate(args.datasets):
        ds_rel = os.path.relpath(dataset, args.strip_prefix)
        x = originals[ds_idx]
        n_elems = n_elems_list[ds_idx]
        # A small helper to derive a dataset-specific tag
        base_tag = os.path.basename(dataset)

        for R in args.ratios:
            dec_path = os.path.join(args.workdir, f"{base_tag}.cuszp.R{R}.dec.f32")
            relEB_used, actual_ratio, cmp_bytes, _log = cuszp_fixedratio_one(
                dataset=dataset,
                target_R=R,
                fixratio_exe=args.fixratio_exe,
                cuszp_exe=args.cuszp_exe,
                out_dec=dec_path,
                extra_fixratio=args.extra_fixratio,
                extra_cuszp=args.extra_cuszp
            )
            if actual_ratio is not None:
                bpp = 32.0 / float(actual_ratio)
            elif cmp_bytes is not None:
                bpp = infer_cmp_bpp(cmp_bytes, n_elems)
                actual_ratio = (n_elems * 4.0) / float(cmp_bytes) if cmp_bytes else None
            else:
                bpp = None

            psnr = None
            if os.path.exists(dec_path):
                y = read_f32(dec_path)
                if y.size == x.size:
                    psnr = psnr_db(x, y, peak_mode=args.psnr_peak)

            results.append({
                "codec": "cuszp",
                "dataset": ds_rel,
                "shape": args.shapes[ds_idx],
                "target_R": R,
                "relEB_used": relEB_used,
                "bpp": bpp,
                "psnr_db": psnr,
                "cmp_bytes": cmp_bytes,
                "ratio": actual_ratio
            })
            if bpp is not None:
                measured_bpps.append(bpp)

    # ---------- ZFP sweep ----------
    # If zfp rates not provided, reuse the set of measured cuSZp bpps (rounded to nearest 0.5)
    if args.zfp_exe and (args.zfp_rates is None or len(args.zfp_rates) == 0):
        uniq = sorted({round(v * 2.0) / 2.0 for v in measured_bpps if v is not None})
        zfp_rates = uniq
    else:
        zfp_rates = args.zfp_rates or []

    # Parse shapes
    shapes = []
    for s in args.shapes:
        parts = [int(v) for v in s.split(",")]
        if len(parts) != 3:
            raise SystemExit(f"ERROR: shape '{s}' must be 'nx,ny,nz'")
        shapes.append(tuple(parts))

    for ds_idx, dataset in enumerate(args.datasets):
        ds_rel = os.path.relpath(dataset, args.strip_prefix)
        x = originals[ds_idx]
        n_elems = n_elems_list[ds_idx]
        base_tag = os.path.basename(dataset)
        shape3 = shapes[ds_idx]

        for rate in zfp_rates:
            dec_path = os.path.join(args.workdir, f"{base_tag}.zfp.r{rate}.dec.f32")
            cmp_bytes, _log = zfp_one(
                dataset=dataset,
                shape=shape3,
                zfp_exe=args.zfp_exe,
                rate_bpv=rate,
                out_dec=dec_path,
                extra_zfp=args.extra_zfp
            )
            bpp = infer_cmp_bpp(cmp_bytes, n_elems) if cmp_bytes is not None else None
            ratio = (n_elems * 4.0) / float(cmp_bytes) if cmp_bytes else None

            psnr = None
            if os.path.exists(dec_path):
                y = read_f32(dec_path)
                if y.size == x.size:
                    psnr = psnr_db(x, y, peak_mode=args.psnr_peak)

            results.append({
                "codec": "zfp",
                "dataset": ds_rel,
                "shape": args.shapes[ds_idx],
                "target_R": None,
                "relEB_used": None,
                "bpp": bpp if bpp is not None else rate,  # bpp should match 'rate' ideally
                "psnr_db": psnr,
                "cmp_bytes": cmp_bytes,
                "ratio": ratio
            })

    # ---------- Save CSV ----------
    df = pd.DataFrame(results, columns=[
        "codec", "dataset", "shape", "target_R", "relEB_used", "bpp", "psnr_db", "cmp_bytes", "ratio"
    ])
    # sort: dataset -> codec -> bpp
    df = df.sort_values(by=["dataset", "codec", "bpp"], kind="stable")

    if args.csv is None:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        args.csv = f"./bitrate_psnr_{ts}.csv"
    df.to_csv(args.csv, index=False)
    print(df.to_csv(index=False).rstrip())
    print(f"Saved results to: {args.csv}")

    return 0

if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))

"""
python compare_bitrate_psnr.py \
  --datasets \
    /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/W-98x1200x1200.f32 \
  --shapes \
    98,1200,1200 \
  --psnr-peak range \
  --csv ./bitrate_psnr_W.csv
"""
