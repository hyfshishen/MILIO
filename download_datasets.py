#!/usr/bin/env python3
"""Download and arrange the evaluation datasets for MILIO.

Downloads 8 of the 9 datasets (all except RTM) into DATA_ROOT (default:
``./datasets``, override with --data-root or the DATA_ROOT environment
variable), extracts the SDRBench archives, and removes the archives afterwards
(keep them with --keep-archives).

RTM cannot be downloaded through direct link access using wget/urllib; download
its three fields (pressure_1000, pressure_2000, pressure_3000) manually from
the Google Drive links in the AD/AE appendix (or the README), create a folder
``rtm`` under DATA_ROOT, and move the three fields inside it.

The script is idempotent: datasets that are already arranged are skipped.

Usage:
  python3 download_datasets.py [--data-root DIR] [--keep-archives] [--dry-run]
"""
import argparse
import os
import sys
import tarfile
import urllib.request

SDR = ("https://g-8d6b0.fd635.8443.data.globus.org/"
       "ds131.2/Data-Reduction-Repo/raw-data")

# (archive name, URL, marker path that indicates the dataset is already arranged)
ARCHIVES = [
    ("SDRBENCH-CESM-ATM-26x1800x3600.tar.gz",
     f"{SDR}/CESM-ATM/SDRBENCH-CESM-ATM-26x1800x3600.tar.gz",
     "SDRBENCH-CESM-ATM-26x1800x3600"),
    ("SDRBENCH-CESM-ATM-1800x3600.tar.gz",          # 2D CLDHGH (Fig. 15)
     f"{SDR}/CESM-ATM/SDRBENCH-CESM-ATM-1800x3600.tar.gz",
     "1800x3600"),
    ("EXASKY-HACC-data-big-size.tar.gz",            # 1-billion-particle snapshot
     f"{SDR}/EXASKY/HACC/EXASKY-HACC-data-big-size.tar.gz",
     "1billionparticles_onesnapshot"),
    ("SDRBENCH-EXASKY-NYX-512x512x512.tar.gz",
     f"{SDR}/EXASKY/NYX/SDRBENCH-EXASKY-NYX-512x512x512.tar.gz",
     "SDRBENCH-EXASKY-NYX-512x512x512"),
    ("SDRBENCH-QMCPack.tar.gz",
     f"{SDR}/QMCPack/SDRBENCH-QMCPack.tar.gz",
     "dataset"),
    ("SDRBENCH-SCALE-98x1200x1200.tar.gz",
     f"{SDR}/SCALE_LETKF/SDRBENCH-SCALE-98x1200x1200.tar.gz",
     "SDRBENCH-SCALE_98x1200x1200"),
    ("SDRBENCH-exaalt-copper.tar.gz",
     f"{SDR}/EXAALT/SDRBENCH-exaalt-copper.tar.gz",
     "SDRBENCH-exaalt-copper"),
    ("SDRBENCH-EXAFEL-130x1480x1552.tar.gz",
     f"{SDR}/EXAFEL/SDRBENCH-EXAFEL-130x1480x1552.tar.gz",
     "SDRBENCH-EXAFEL-130x1480x1552"),
]

# Plain files downloaded as-is (no extraction).
RAW_FILES = [
    ("synthetic_truss_with_five_defects_1200x1200x1200_float32.raw",
     "http://klacansky.com/open-scivis-datasets/"
     "synthetic_truss_with_five_defects/"
     "synthetic_truss_with_five_defects_1200x1200x1200_float32.raw"),
]

RTM_NOTE = """\
NOTE: RTM (pressure_1000/2000/3000) cannot be downloaded through direct link
access. Please download the three fields manually from the Google Drive links
in the AD/AE appendix (or README), then:
  mkdir -p {root}/rtm
  mv pressure_1000 pressure_2000 pressure_3000 {root}/rtm/
"""


def download(url, dest, dry=False):
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root",
                    default=os.environ.get("DATA_ROOT", "./datasets"),
                    help="target directory (default: $DATA_ROOT or ./datasets)")
    ap.add_argument("--keep-archives", action="store_true",
                    help="keep the downloaded .tar.gz archives after extraction")
    ap.add_argument("--dry-run", action="store_true",
                    help="only show what would be done")
    args = ap.parse_args()

    root = os.path.abspath(args.data_root)
    os.makedirs(root, exist_ok=True)
    print(f"Arranging datasets under: {root}\n")

    for name, url, marker in ARCHIVES:
        archive = os.path.join(root, name)
        if os.path.exists(os.path.join(root, marker)):
            print(f"[skip] {name} (already arranged: {marker}/)")
            continue
        if not os.path.exists(archive):
            print(f"[get ] {name}")
            download(url, archive, args.dry_run)
        else:
            print(f"[have] {name} (archive already downloaded)")
        extract(archive, root, args.dry_run)
        if not args.keep_archives and not args.dry_run:
            os.remove(archive)

    for name, url in RAW_FILES:
        dest = os.path.join(root, name)
        if os.path.exists(dest):
            print(f"[skip] {name} (already downloaded)")
            continue
        print(f"[get ] {name}")
        download(url, dest, args.dry_run)

    print()
    print(RTM_NOTE.format(root=root))
    print("Done. 8/9 datasets arranged (RTM requires the manual step above).")


if __name__ == "__main__":
    main()
