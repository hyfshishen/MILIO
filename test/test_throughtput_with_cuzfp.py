#!/usr/bin/env python3
# Compare throughput (GB/s): cuSZp fixed-ratio vs ZFP (CUDA)
# - cuSZp compression throughput: "total end-to-end speed" from cuSZp_fixratio
# - cuSZp decompression throughput: use relEB from fixratio, run cuSZp with -eb rel <relEB> -o <dec>
# - cuSZp fixratio now also records:
#     * profile_gbps  (profile end-to-end speed)
#     * comp_ratio    (actual measured ratio)
#     * bytes_in, bytes_cmp
# - Optional: save .cmp via fixratio (-x) and keep/delete via flags
import argparse, os, re, subprocess, datetime
from typing import List, Tuple, Optional
import pandas as pd

# =========================
# Regex parsers
# =========================
# ZFP summary (-s) lines
RE_ZFP_ENC_RATE = re.compile(r"#\s*encode\d*\s*rate:\s*([0-9.]+)\s*\(\s*GB\s*/\s*sec\s*\)", re.IGNORECASE)
RE_ZFP_DEC_RATE = re.compile(r"#\s*decode\d*\s*rate:\s*([0-9.]+)\s*\(\s*GB\s*/\s*sec\s*\)", re.IGNORECASE)

# cuSZp_fixratio lines
RE_CUSZP_PROFILE_SPEED = re.compile(r"\bprofile\s+end-to-end\s+speed:\s*([0-9.]+)\s*GB/s", re.IGNORECASE)
RE_CUSZP_TOTAL_SPEED   = re.compile(r"\btotal\s+end-to-end\s+speed:\s*([0-9.]+)\s*GB/s", re.IGNORECASE)
RE_CUSZP_COMP_SPEED    = re.compile(r"\bcompression\s+end-to-end\s+speed:\s*([0-9.]+)\s*GB/s", re.IGNORECASE)

# relEB pick
RE_CUSZP_PICK_LINE     = re.compile(r'pick\s+EB_idx=\d+\s+relEB=([0-9.eE+\-]+)', re.IGNORECASE)
RE_CUSZP_RELEB_ANY     = re.compile(r'\brelEB\s*=\s*([0-9.eE+\-]+)\b', re.IGNORECASE)

# compression stats (best effort)
RE_COMP_LINE           = re.compile(r"\[compress\].*?bytes_in\s*=\s*([0-9]+)\s+bytes_cmp\s*=\s*([0-9]+)\s+ratio\s*=\s*([0-9.]+)", re.IGNORECASE)
RE_COMPRESS_RATIO_ONLY = re.compile(r"(?:\[compress\].*?ratio\s*=\s*|ratio\s*[:=]\s*)([0-9.]+)")

# cuSZp decode line
RE_CUSZP_DECOMP_SPEED  = re.compile(r"\bdecompression\s+end-to-end\s+speed:\s*([0-9.]+)\s*GB/s", re.IGNORECASE)

# =========================
# Helpers
# =========================
def run_cmd(cmd: List[str], log_path: Optional[str] = None) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.stdout or ""
    if log_path:
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(out)
        except Exception:
            pass
    if p.returncode != 0:
        raise RuntimeError(f"Command failed (rc={p.returncode}): {' '.join(cmd)}\n---\n{out}")
    return out

def parse_many_floats(tokens) -> List[float]:
    """Accept '8 6 4' or '8,6,4' or mixed."""
    vals: List[float] = []
    for tok in tokens or []:
        for part in str(tok).replace(",", " ").split():
            vals.append(float(part))
    return vals

def parse_zfp_rates(output: str) -> Tuple[Optional[float], Optional[float]]:
    enc = dec = None
    m = RE_ZFP_ENC_RATE.search(output)
    if m:
        try: enc = float(m.group(1))
        except: pass
    m = RE_ZFP_DEC_RATE.search(output)
    if m:
        try: dec = float(m.group(1))
        except: pass
    return enc, dec

def parse_cuszp_fixratio(output: str) -> Tuple[
    Optional[float],  # relEB
    Optional[float],  # profile_gbps
    Optional[float],  # comp_total_gbps
    Optional[float],  # comp_only_gbps
    Optional[float],  # comp_ratio
    Optional[int],    # bytes_in
    Optional[int],    # bytes_cmp
]:
    relEB = None
    m = RE_CUSZP_PICK_LINE.search(output) or RE_CUSZP_RELEB_ANY.search(output)
    if m:
        try: relEB = float(m.group(1))
        except: pass

    profile = None
    m = RE_CUSZP_PROFILE_SPEED.search(output)
    if m:
        try: profile = float(m.group(1))
        except: pass

    comp_total = comp_only = None
    m = RE_CUSZP_TOTAL_SPEED.search(output)
    if m:
        try: comp_total = float(m.group(1))
        except: pass
    m = RE_CUSZP_COMP_SPEED.search(output)
    if m:
        try: comp_only = float(m.group(1))
        except: pass

    ratio = None
    bytes_in = bytes_cmp = None
    m = RE_COMP_LINE.search(output)
    if m:
        try:
            bytes_in  = int(m.group(1))
            bytes_cmp = int(m.group(2))
            ratio     = float(m.group(3))
        except:
            pass
    if ratio is None:
        m = RE_COMPRESS_RATIO_ONLY.search(output)
        if m:
            try: ratio = float(m.group(1))
            except: pass

    return relEB, profile, comp_total, comp_only, ratio, bytes_in, bytes_cmp

def parse_shape(shape_str: str) -> Tuple[int, ...]:
    parts = [int(v) for v in shape_str.split(",")]
    if not (1 <= len(parts) <= 3):
        raise SystemExit(f"Bad shape '{shape_str}'; use 'N' or 'nx,ny' or 'nx,ny,nz'.")
    return tuple(parts)

def zfp_dim_flag(shape: Tuple[int, ...]) -> List[str]:
    if len(shape) == 1:  # 1D
        return ["-1", str(shape[0])]
    if len(shape) == 2:  # 2D
        nx, ny = shape
        return ["-2", str(nx), str(ny)]
    # 3D
    nx, ny, nz = shape
    return ["-3", str(nx), str(ny), str(nz)]

# =========================
# Runners
# =========================
def run_zfp(dataset: str,
            shape: Tuple[int, ...],
            zfp_exe: str,
            rate_bpv: float,
            zfp_extra: List[str],
            workdir: str,
            use_cuda: bool = True) -> Tuple[Optional[float], Optional[float], str]:
    cmd = [zfp_exe]
    if use_cuda:
        cmd += ["-x", "cuda"]
    cmd += ["-i", dataset, "-f"] + zfp_dim_flag(shape) + ["-r", str(rate_bpv), "-s"]
    if zfp_extra:
        cmd += zfp_extra
    tag = os.path.basename(dataset)
    log_path = os.path.join(workdir, f"{tag}.zfp.r{rate_bpv}.log")
    out = run_cmd(cmd, log_path)
    enc, dec = parse_zfp_rates(out)
    return enc, dec, out

def run_cuszp_fixratio(dataset: str,
                       target_R: float,
                       fixratio_exe: str,
                       extra_fixratio: List[str],
                       workdir: str,
                       cmp_path: Optional[str],
                       keep_cmp: bool) -> Tuple[
                           Optional[float], Optional[float], Optional[float], Optional[float],
                           Optional[float], Optional[int], Optional[int], str]:
    """
    Run cuSZp_fixratio; if cmp_path is given, pass '-x cmp_path' to save compressed stream.
    If keep_cmp is False, delete cmp_path after run (best-effort).
    Returns (relEB, profile_gbps, comp_total_gbps, comp_only_gbps, comp_ratio, bytes_in, bytes_cmp, raw_out)
    """
    cmd = [fixratio_exe, "-i", dataset, "-R", str(target_R)]
    if extra_fixratio:
        cmd += extra_fixratio
    if cmp_path:
        try:
            if os.path.exists(cmp_path): os.remove(cmp_path)
        except Exception:
            pass
        cmd += ["-x", cmp_path]

    tag = os.path.basename(dataset)
    log_path = os.path.join(workdir, f"{tag}.cuszp_fixratio.R{target_R}.log")
    out = run_cmd(cmd, log_path)

    relEB, profile, comp_total, comp_only, ratio, bytes_in, bytes_cmp = parse_cuszp_fixratio(out)

    if cmp_path and (not keep_cmp):
        try:
            if os.path.exists(cmp_path): os.remove(cmp_path)
        except Exception:
            pass

    return relEB, profile, comp_total, comp_only, ratio, bytes_in, bytes_cmp, out

def run_cuszp_decode(dataset: str,
                     cuszp_exe: str,
                     relEB: float,
                     dtype: str,
                     mode: str,
                     dec_path: str,
                     extra_cuszp: List[str],
                     workdir: str) -> Tuple[Optional[float], str]:
    """
    Measure decompression throughput by running cuSZp with the picked relEB.
    We don't need a .cmp; cuSZp will compress+decompress and print decode GB/s.
    """
    relEB_str = f"{relEB:.9g}"
    try:
        if os.path.exists(dec_path): os.remove(dec_path)
    except Exception:
        pass

    cmd = [cuszp_exe, "-i", dataset, "-t", dtype, "-m", mode,
           "-eb", "rel", relEB_str, "-o", dec_path]
    if extra_cuszp:
        cmd += extra_cuszp
    log_path = os.path.join(workdir, f"{os.path.basename(dataset)}.cuszp.decode.relEB{relEB_str}.log")
    out = run_cmd(cmd, log_path)

    decomp = None
    m = RE_CUSZP_DECOMP_SPEED.search(out)
    if m:
        try: decomp = float(m.group(1))
        except: pass
    return decomp, out

# =========================
# Main
# =========================
def main(argv=None):
    ap = argparse.ArgumentParser(description="Throughput (GB/s): cuSZp fixed-ratio vs ZFP (CUDA). Records profile speed & actual ratio for cuSZp.")
    # Datasets
    ap.add_argument("--datasets", type=str, nargs="+", required=True,
                    help="List of .f32 datasets")
    ap.add_argument("--shapes", type=str, nargs="+", required=True,
                    help="One shape for all or one-per-dataset: 'N' or 'nx,ny' or 'nx,ny,nz' (for ZFP).")
    # Executables
    ap.add_argument("--fixratio-exe", type=str, default="/home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio")
    ap.add_argument("--cuszp-exe", type=str, default="/home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp")
    ap.add_argument("--zfp-exe", type=str, default="/home/bohan/zfp/build/bin/zfp")
    # Sweeps (comma/space ok)
    ap.add_argument("--ratios", type=str, nargs="+", default=["4","6","8","16","24","32"],
                    help="Target R for cuSZp fixed-ratio sweep. Accepts '4 6 8' or '4,6,8'.")
    ap.add_argument("--zfp-rates", type=str, nargs="+", default=["8","6","4","3","2","1"],
                    help="ZFP rate (bits/value). Accepts '8 6 4' or '8,6,4'.")
    # cuSZp decode options
    ap.add_argument("--cuszp-dtype", type=str, choices=["f32","f64"], default="f32",
                    help="Data type for cuSZp -t.")
    ap.add_argument("--cuszp-mode", type=str, choices=["plain","outlier"], default="plain",
                    help="Encoding mode for cuSZp -m.")
    # Extra args & misc
    ap.add_argument("--extra-fixratio", nargs=argparse.REMAINDER, default=[],
                help="Extra args for cuSZp_fixratio (e.g., -S 1000)")

    ap.add_argument("--extra-cuszp", type=str, nargs="*", default=[],
                    help="Extra args for cuSZp (decode step)")
    ap.add_argument("--extra-zfp", type=str, nargs="*", default=[],
                    help="Extra args for zfp")
    ap.add_argument("--no-zfp-cuda", action="store_true", help="Do not pass '-x cuda' to zfp.")
    ap.add_argument("--strip-prefix", type=str, default="/home/bohan",
                    help="Strip this prefix from dataset path in CSV.")
    ap.add_argument("--workdir", type=str, default="./_wrk_throughput", help="Working directory for logs & dec files.")
    ap.add_argument("--csv", type=str, default=None, help="Output CSV path.")
    # Optional saving of fixratio .cmp
    ap.add_argument("--fixratio-save-cmp", action="store_true",
                    help="If set, call cuSZp_fixratio with '-x <workdir>/<base>.R<ratio>.cmp' to save compressed stream.")
    ap.add_argument("--keep-cmp", action="store_true",
                    help="If set with --fixratio-save-cmp, keep the saved .cmp files (default: delete).")
    args = ap.parse_args(argv)

    # Normalize lists
    args.zfp_rates = parse_many_floats(args.zfp_rates)
    args.ratios    = parse_many_floats(args.ratios)

    os.makedirs(args.workdir, exist_ok=True)

    # Parse/broadcast shapes
    shapes_raw = [parse_shape(s) for s in args.shapes]
    if len(shapes_raw) == 1:
        shapes = shapes_raw * len(args.datasets)
    elif len(shapes_raw) == len(args.datasets):
        shapes = shapes_raw
    else:
        raise SystemExit(f"--shapes count ({len(shapes_raw)}) must be 1 or equal to --datasets count ({len(args.datasets)}).")

    rows = []

    # ---- cuSZp fixed-ratio ----
    for ds in args.datasets:
        ds_rel = os.path.relpath(ds, args.strip_prefix)
        base_tag = os.path.basename(ds)
        for R in args.ratios:
            cmp_path = None
            if args.fixratio_save_cmp:
                Rtag = int(R) if float(R).is_integer() else R
                cmp_path = os.path.join(args.workdir, f"{base_tag}.cuszp_fixratio.R{Rtag}.cmp")

            relEB, profile_gbps, comp_total, comp_only, comp_ratio, bytes_in, bytes_cmp, _ = run_cuszp_fixratio(
                dataset=ds,
                target_R=R,
                fixratio_exe=args.fixratio_exe,
                extra_fixratio=args.extra_fixratio,
                workdir=args.workdir,
                cmp_path=cmp_path,
                keep_cmp=args.keep_cmp,
            )

            # measure decode throughput via cuSZp using relEB
            decomp = None
            if relEB is not None:
                Rtag = int(R) if float(R).is_integer() else R
                dec_path = os.path.join(args.workdir, f"{base_tag}.cuszp.R{Rtag}.dec.f32")
                decomp, _ = run_cuszp_decode(
                    dataset=ds,
                    cuszp_exe=args.cuszp_exe,
                    relEB=relEB,
                    dtype=args.cuszp_dtype,
                    mode=args.cuszp_mode,
                    dec_path=dec_path,
                    extra_cuszp=args.extra_cuszp,
                    workdir=args.workdir,
                )
            else:
                print(f"[warn] relEB not found for {base_tag} @ R={R}. Skipping cuSZp decode.")

            rows.append({
                "codec": "cuszp_fixratio",
                "dataset": ds_rel,
                "shape": None,
                "target_R": R,
                "zfp_rate_req": None,
                "relEB_used": f"{relEB:.9g}" if relEB is not None else None,
                "profile_gbps": profile_gbps,
                "comp_gbps": comp_total,        # total end-to-end speed (compression)
                "comp_only_gbps": comp_only,    # optional
                "decomp_gbps": decomp,          # parsed from cuSZp run
                "comp_ratio": comp_ratio,       # actual ratio from [compress] line
                "bytes_in": bytes_in,
                "bytes_cmp": bytes_cmp,
            })

    # ---- ZFP ----
    for ds, shp in zip(args.datasets, shapes):
        ds_rel = os.path.relpath(ds, args.strip_prefix)
        for rate in args.zfp_rates:
            enc, dec, _ = run_zfp(
                dataset=ds,
                shape=shp,
                zfp_exe=args.zfp_exe,
                rate_bpv=rate,
                zfp_extra=args.extra_zfp,
                workdir=args.workdir,
                use_cuda=(not args.no_zfp_cuda),
            )
            rows.append({
                "codec": "zfp",
                "dataset": ds_rel,
                "shape": ",".join(str(v) for v in shp),
                "target_R": None,
                "zfp_rate_req": rate,
                "relEB_used": None,
                "profile_gbps": None,
                "comp_gbps": enc,        # encode throughput
                "comp_only_gbps": None,
                "decomp_gbps": dec,      # decode throughput
                "comp_ratio": None,
                "bytes_in": None,
                "bytes_cmp": None,
            })

    df = pd.DataFrame(rows, columns=[
        "codec","dataset","shape","target_R","zfp_rate_req","relEB_used",
        "profile_gbps","comp_gbps","comp_only_gbps","decomp_gbps",
        "comp_ratio","bytes_in","bytes_cmp"
    ])
    df = df.sort_values(by=["dataset","codec","target_R","zfp_rate_req"], kind="stable")

    if args.csv is None:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        args.csv = f"./throughput_{ts}.csv"

    df.to_csv(args.csv, index=False)
    print(df.to_csv(index=False).rstrip())
    print(f"Saved results to: {args.csv}")

if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))


"""
python test_throughtput_with_cuzfp.py \
  --datasets /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_x.f32 \
            /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_y.f32 \
            /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/velocity_z.f32 \
            /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/dark_matter_density.f32 \
            /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/baryon_density.f32 \
            /home/bohan/SDRBENCH-EXASKY-NYX-512x512x512/temperature.f32 \
  --shapes 512,512,512 \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_NYX.csv 

python test_throughtput_with_cuzfp.py \
  --datasets /home/bohan/pressure_1000 \
            /home/bohan/pressure_2000 \
            /home/bohan/pressure_3000 \
                --shapes 1008,1008,352 \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_RTM.csv

  python test_throughtput_with_cuzfp.py \
  --datasets     /home/bohan/SDRBENCH-SCALE-98x1200x1200/SDRBENCH-SCALE_98x1200x1200/PRES-98x1200x1200.f32 \
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
                --shapes 98,1200,1200 \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_SCALE.csv

python test_throughtput_with_cuzfp.py \
  --datasets         /home/bohan/1billionparticles_onesnapshot/vx.f32 \
    /home/bohan/1billionparticles_onesnapshot/vy.f32 \
    /home/bohan/1billionparticles_onesnapshot/vz.f32 \
    /home/bohan/1billionparticles_onesnapshot/xx.f32 \
    /home/bohan/1billionparticles_onesnapshot/yy.f32 \
    /home/bohan/1billionparticles_onesnapshot/zz.f32 \
                --shapes 1073726487  \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_HACC.csv

  python test_throughtput_with_cuzfp.py \
  --datasets   /home/bohan/SDRBENCH-QMCPack/dataset/115x69x69x288/einspline_115_69_69_288.f32 \
                --shapes 115,69,19872  \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_QMCPACK.csv

  python test_throughtput_with_cuzfp.py \
  --datasets   /home/bohan/SDRBENCH-QMCPack/dataset/115x69x69x288/einspline_115_69_69_288.f32 \
                --shapes 10695,69,288  \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_QMCPACK.csv

    python test_throughtput_with_cuzfp.py \
  --datasets        /home/bohan/SDRBENCH-CESM-ATM-26x1800x3600/CLDICE_1_26_1800_3600.f32 \
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
                --shapes 26,1800,3600  \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_CESM-ATM.csv

  python test_throughtput_with_cuzfp.py \
  --datasets     /home/bohan/SDRBENCH-EXAFEL-130x1480x1552/SDRBENCH-EXAFEL-data-130x1480x1552.f32\
                --shapes 130,1480,1552 \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_EXAFEL.csv

    python test_throughtput_with_cuzfp.py \
  --datasets     /home/bohan/synthetic_truss_with_five_defects_1200x1200x1200_float32.raw\
                --shapes 1200,1200,1200 \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_synTruss.csv


    
  python test_throughtput_with_cuzfp.py \
  --datasets      /home/bohan/SDRBENCH-exaalt-copper/dataset1-5423x3137.x.f32.dat \
    /home/bohan/SDRBENCH-exaalt-copper/dataset1-5423x3137.z.f32.dat \
    /home/bohan/SDRBENCH-exaalt-copper/dataset1-5423x3137.y.f32.dat \
                --shapes 5423,3137 \
  --fixratio-exe /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp_fixratio \
  --cuszp-exe    /home/bohan/fixed-ratio-with-cuSZp/build/examples/bin/cuSZp \
  --zfp-exe      /home/bohan/zfp/build/bin/zfp \
  --cuszp-dtype f32 --cuszp-mode plain \
  --ratios 4,6,8 \
  --zfp-rates 8,5,4 \
  --fixratio-save-cmp \
  --csv ./throughput_results_exaalt.csv
  



"""
