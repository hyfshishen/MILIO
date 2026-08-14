#!/usr/bin/env python3
"""Download and arrange the evaluation datasets for MILIO.

Downloads all nine datasets into DATA_ROOT (default: ``./datasets``, override
with --data-root or the DATA_ROOT environment variable):

  * The eight SDRBench archives are fetched over HTTP from SDRBench and extracted
    in place.
  * SYNTHESIS is served over HTTP by Open-SciVis and downloaded directly.
  * RTM lives on a public Google Drive folder (pressure_1000/2000/3000) and is
    fetched with ``gdown`` (installed on demand).

If SDRBench is unavailable, a complete public backup of the eight archives is at:
  https://drive.google.com/drive/folders/1iDDSqc2_-U-lYEr3XdwVjJmOeI-e0mdV

The script is idempotent: datasets that are already arranged are skipped, so it
is safe to re-run after an interruption.

Usage:
  python3 download_datasets.py [--data-root DIR] [--keep-archives]
                               [--skip-rtm] [--dry-run]
"""
import argparse
import glob
import os
import subprocess
import sys
import tarfile
import urllib.request

SDR = "https://g-d0cd3f.fd635.8443.data.globus.org/raw-data"

# (url, archive name, marker dir, extracted dir if it differs from the marker).
# Marker = directory the benchmark scripts expect; if the archive extracts to a
# different top-level directory, it is renamed to the marker after extraction.
ARCHIVES = [
    (f"{SDR}/CESM-ATM/SDRBENCH-CESM-ATM-26x1800x3600.tar.gz",   # CESM 3D fields
     "SDRBENCH-CESM-ATM-26x1800x3600.tar.gz", "SDRBENCH-CESM-ATM-26x1800x3600", None),
    (f"{SDR}/CESM-ATM/SDRBENCH-CESM-ATM-1800x3600.tar.gz",      # CESM 2D (Fig. 15)
     "SDRBENCH-CESM-ATM-1800x3600.tar.gz", "1800x3600", None),
    (f"{SDR}/EXASKY/HACC/EXASKY-HACC-data-big-size.tar.gz",     # extracts EXASKY-HACC-data-big-size/
     "EXASKY-HACC-data-big-size.tar.gz", "1billionparticles_onesnapshot", "EXASKY-HACC-data-big-size"),
    (f"{SDR}/EXASKY/NYX/SDRBENCH-EXASKY-NYX-512x512x512.tar.gz",
     "SDRBENCH-EXASKY-NYX-512x512x512.tar.gz", "SDRBENCH-EXASKY-NYX-512x512x512", None),
    (f"{SDR}/QMCPACK/SDRBENCH-QMCPack.tar.gz",                  # extracts SDRBENCH-QMCPack/
     "SDRBENCH-QMCPack.tar.gz", "dataset", "SDRBENCH-QMCPack"),
    (f"{SDR}/SCALE_LETKF/SDRBENCH-SCALE-98x1200x1200.tar.gz",
     "SDRBENCH-SCALE-98x1200x1200.tar.gz", "SDRBENCH-SCALE_98x1200x1200", None),
    (f"{SDR}/EXAALT/SDRBENCH-EXAALT-copper.tar.gz",
     "SDRBENCH-EXAALT-copper.tar.gz", "SDRBENCH-exaalt-copper", None),
    (f"{SDR}/EXAFEL/SDRBENCH-EXAFEL-130x1480x1552.tar.gz",
     "SDRBENCH-EXAFEL-130x1480x1552.tar.gz", "SDRBENCH-EXAFEL-130x1480x1552", None),
]

# SYNTHESIS is served over HTTP (no extraction, plain raw file).
SYNTHESIS_NAME = "synthetic_truss_with_five_defects_1200x1200x1200_float32.raw"
SYNTHESIS_URL = ("http://klacansky.com/open-scivis-datasets/"
                 "synthetic_truss_with_five_defects/" + SYNTHESIS_NAME)

# RTM is a Google Drive folder holding pressure_1000 / _2000 / _3000.
RTM_FOLDER_URL = ("https://drive.google.com/drive/folders/"
                  "1arA8kjqAQXbYINUBndgMA7oDrfXxx4mU")

RTM_MANUAL = """\
  RTM could not be downloaded automatically. Download the three fields manually
  from:
      {url}
  then place them under {root}/rtm/
  (pressure_1000, pressure_2000, pressure_3000).
"""


def http_download(url, dest, dry=False):
    if dry:
        print(f"  [dry-run] would download {url}")
        return
    tmp = dest + ".part"

    def hook(blocks, bs, total):
        done = blocks * bs
        if total > 0:
            pct = min(100.0, done * 100.0 / total)
            sys.stdout.write(f"\r  downloading {os.path.basename(dest)}: "
                             f"{pct:5.1f}% ({done / 1e9:.2f} GB)")
        else:
            sys.stdout.write(f"\r  downloading {os.path.basename(dest)}: "
                             f"{done / 1e9:.2f} GB")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, tmp, reporthook=hook)
    print()
    os.replace(tmp, dest)


def extract(archive, root, dry=False):
    if dry:
        print(f"  [dry-run] would extract {os.path.basename(archive)}")
        return
    print(f"  extracting {os.path.basename(archive)} ...")
    with tarfile.open(archive, "r:gz") as tf:
        tf.extractall(root)


def ensure_gdown():
    """Import gdown, installing it into the user site on demand (RTM only)."""
    try:
        import gdown  # noqa: F401
        return True
    except ImportError:
        print("  gdown not found; installing it (pip install --user gdown) ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   "--user", "--quiet", "gdown"])
            import gdown  # noqa: F401
            return True
        except Exception as e:
            print(f"  could not install gdown automatically: {e}")
            return False


def rtm_present(root):
    return bool(glob.glob(os.path.join(root, "rtm", "**", "pressure_*"),
                          recursive=True))


def download_rtm(root, dry=False):
    if rtm_present(root):
        print("[skip] RTM (already arranged: rtm/)")
        return
    if dry:
        print(f"  [dry-run] would fetch RTM folder via gdown -> {root}/rtm")
        return
    if not ensure_gdown():
        print(RTM_MANUAL.format(url=RTM_FOLDER_URL, root=root))
        return
    import gdown
    out = os.path.join(root, "rtm")
    os.makedirs(out, exist_ok=True)
    print("[get ] RTM (Google Drive folder)")
    try:
        gdown.download_folder(RTM_FOLDER_URL, output=out,
                              quiet=False, use_cookies=False)
    except Exception as e:
        print(f"  gdown failed: {e}")
    if not rtm_present(root):
        print(RTM_MANUAL.format(url=RTM_FOLDER_URL, root=root))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root",
                    default=os.environ.get("DATA_ROOT", "./datasets"),
                    help="target directory (default: $DATA_ROOT or ./datasets)")
    ap.add_argument("--keep-archives", action="store_true",
                    help="keep the downloaded .tar.gz archives after extraction")
    ap.add_argument("--skip-rtm", action="store_true",
                    help="do not attempt the RTM (Google Drive) download")
    ap.add_argument("--dry-run", action="store_true",
                    help="only show what would be done")
    args = ap.parse_args()

    root = os.path.abspath(args.data_root)
    os.makedirs(root, exist_ok=True)
    print(f"Arranging datasets under: {root}\n")

    # 1. SDRBench archives (HTTP) -> extract -> normalize directory name.
    for url, name, marker, extracted in ARCHIVES:
        if os.path.exists(os.path.join(root, marker)):
            print(f"[skip] {name} (already arranged: {marker}/)")
            continue
        archive = os.path.join(root, name)
        if not os.path.exists(archive):
            print(f"[get ] {name}")
            http_download(url, archive, args.dry_run)
        else:
            print(f"[have] {name} (archive already downloaded)")
        extract(archive, root, args.dry_run)
        if not args.dry_run and extracted and extracted != marker:
            src = os.path.join(root, extracted)
            if os.path.isdir(src):
                os.rename(src, os.path.join(root, marker))
                print(f"  renamed {extracted}/ -> {marker}/")
        if not args.keep_archives and not args.dry_run:
            os.remove(archive)

    # 2. SYNTHESIS (HTTP).
    dest = os.path.join(root, SYNTHESIS_NAME)
    if os.path.exists(dest):
        print(f"[skip] {SYNTHESIS_NAME} (already downloaded)")
    else:
        print(f"[get ] {SYNTHESIS_NAME}")
        http_download(SYNTHESIS_URL, dest, args.dry_run)

    # 3. RTM (Google Drive folder).
    if args.skip_rtm:
        print("[skip] RTM (--skip-rtm)")
    else:
        download_rtm(root, args.dry_run)

    print("\nDone.")
    if not args.dry_run and not args.skip_rtm and not rtm_present(root):
        print("NOTE: RTM is not present yet -- see the message above.")


if __name__ == "__main__":
    main()
