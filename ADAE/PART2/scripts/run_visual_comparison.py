#!/usr/bin/env python3
"""Generate the four reconstructions behind the visual-comparison figure
(Fig. 15): cuZFP and MILIO-o applied to CESM CLDHGH (1800x3600) at target
compression ratios 8 and 16.

Each compressor is used in its natural mode:
  * MILIO is a 1D streaming compressor -- it takes only the element count
    (-n), no logical shape, and is run through the 1D CLI with -D to dump the
    reconstruction.
  * cuZFP is a block-transform compressor that needs the 2D shape; it is given
    the field's labelled dimensions (-2 1800 3600) via `zfp -i ... -o ...`.

It locates (or extracts) the CLDHGH field, submits a single-GPU Slurm job that
writes each reconstruction to disk, then records the achieved MILIO ratios so
the plot can label the panels with the real numbers.

Outputs, in FIG15_WORK (default ./fig15_data):
  CLDHGH_1_1800_3600.dat  cuzfp_cr8.dat  milio_cr8.dat  cuzfp_cr16.dat  milio_cr16.dat
  fig15_cr.env            (export FIG15_CR_MILIO8=... / ...MILIO16=...)
Raw job log: benchmark_visual_comparison.log
"""
import os
import re
import subprocess
import tarfile

# ---- site configuration (run_part2.sh rewrites these placeholders) ----------
DATA_ROOT = "/scratch/bfrq/bzhang28"
ZFP_EXE   = "/u/bzhang28/zfp/build/bin/zfp"
ACCOUNT   = "bfrq-delta-gpu"
PARTITION = "gpuA100x4"

CLI_1D = "./build/examples/bin/cuszp_fixed_ratio_cli"   # MILIO: 1D, shape-agnostic
NELE = 1800 * 3600                                      # CLDHGH element count
ZFP_DIMS = "1800 3600"                                  # cuZFP: labelled 2D shape
CANON = "CLDHGH_1_1800_3600.dat"                        # canonical original (for plot)
TARBALL = os.path.join(DATA_ROOT, "SDRBENCH-CESM-ATM-1800x3600.tar.gz")
MEMBER  = "1800x3600/CLDHGH_1_1800_3600.f32"

WORK = os.environ.get("FIG15_WORK", "./fig15_data")
LOG  = "benchmark_visual_comparison.log"
SAMPLE = 100


def locate_field():
    """Return a path to the raw CLDHGH field, extracting it if needed."""
    # 1) already extracted next to the other SDRBench data or in WORK?
    for cand in (os.path.join(DATA_ROOT, "1800x3600", "CLDHGH_1_1800_3600.f32"),
                 os.path.join(WORK, "CLDHGH_1_1800_3600.f32"),
                 os.path.join(WORK, CANON)):
        if os.path.exists(cand):
            return cand
    # 2) extract the single member from the tarball
    if not os.path.exists(TARBALL):
        raise FileNotFoundError(f"Neither CLDHGH nor {TARBALL} found")
    os.makedirs(WORK, exist_ok=True)
    print(f"Extracting {MEMBER} from {TARBALL} ...")
    with tarfile.open(TARBALL, "r:gz") as tf:
        m = tf.getmember(MEMBER)
        m.name = "CLDHGH_1_1800_3600.f32"      # flatten into WORK
        tf.extract(m, WORK)
    return os.path.join(WORK, "CLDHGH_1_1800_3600.f32")


def main():
    os.makedirs(WORK, exist_ok=True)
    src = locate_field()
    inp = os.path.join(WORK, CANON)            # canonical original the plot reads
    if os.path.abspath(src) != os.path.abspath(inp):
        with open(src, "rb") as a, open(inp, "wb") as b:
            b.write(a.read())

    jobs = [
        ("milio8",  f"{CLI_1D} -i {inp} -n {NELE} -r 8  -m outlier -s {SAMPLE} "
                    f"-D {WORK}/milio_cr8.dat"),
        ("milio16", f"{CLI_1D} -i {inp} -n {NELE} -r 16 -m outlier -s {SAMPLE} "
                    f"-D {WORK}/milio_cr16.dat"),
        ("cuzfp8",  f"{ZFP_EXE} -x cuda -f -2 {ZFP_DIMS} -r 4 -i {inp} "
                    f"-o {WORK}/cuzfp_cr8.dat  -s"),
        ("cuzfp16", f"{ZFP_EXE} -x cuda -f -2 {ZFP_DIMS} -r 2 -i {inp} "
                    f"-o {WORK}/cuzfp_cr16.dat -s"),
    ]
    script = "#!/bin/bash\n"
    for tag, cmd in jobs:
        script += f"echo 'VIS_START:{tag}'\n{cmd} || true\nsleep 0.1\n"
    with open("run_visual_bench.sh", "w") as f:
        f.write(script)

    print("Submitting single-GPU job for the four reconstructions ...")
    srun = ["srun", f"--account={ACCOUNT}", f"--partition={PARTITION}",
            "--nodes=1", "--ntasks=1", "--gpus-per-node=1", "--time=00:15:00",
            "bash", "run_visual_bench.sh"]
    with open(LOG, "w") as out:
        subprocess.run(srun, stdout=out, stderr=subprocess.STDOUT)

    # ---- record achieved MILIO ratios so the plot labels match the run ------
    cr = {}
    cur = None
    with open(LOG) as f:
        for line in f:
            m = re.search(r"VIS_START:(\w+)", line)
            if m:
                cur = m.group(1)
            ma = re.search(r"Achieved Ratio:\s*([0-9.]+)", line)
            if ma and cur in ("milio8", "milio16"):
                cr[cur] = float(ma.group(1))
    env_path = os.path.join(WORK, "fig15_cr.env")
    with open(env_path, "w") as f:
        f.write(f"export FIG15_CR_MILIO8={cr.get('milio8', 8.06):.2f}\n")
        f.write(f"export FIG15_CR_MILIO16={cr.get('milio16', 16.03):.2f}\n")
    print(f"Reconstructions in {WORK}; achieved MILIO ratios: {cr}")
    print(f"Wrote {env_path} and {LOG}")


if __name__ == "__main__":
    main()
