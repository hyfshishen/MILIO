#!/usr/bin/env python3
"""Reproduce TABLE III: achieved compression ratios (bold) and the selected
error bounds under target ratios R = 4, 6, 8, for MILIO-p (plain) and
MILIO-o (outlier).

Parses benchmark_fixratio_warmup_output.log (produced by benchmark_fixratio_all.py)
and emits both a Markdown table (table3.md) and a LaTeX table (table3.tex).
"""
import re
import os
from collections import defaultdict

LOG_FILE = "benchmark_fixratio_warmup_output.log"
OUT_MD = "table3.md"
OUT_TEX = "table3.tex"

RATIOS = [4.0, 6.0, 8.0]

# One representative field per dataset (substring match against the field name in
# the log), plus the short label shown in the table. Row order matches the paper.
FIELDS = [
    ("HACC",      "vy.f32",                                      "vy"),
    ("CESM",      "GCLDLWP_1_26_1800_3600.f32",                  "GCLDLWP"),
    ("EXAFEL",    "SDRBENCH-EXAFEL-data-130x1480x1552.f32",      "EXAFEL_data"),
    ("NYX",       "velocity_x.f32",                              "velocity_x"),
    ("QMCPACK",   "einspline_115_69_69_288.f32",                 "einspline"),
    ("SCALE",     "PRES-98x1200x1200.f32",                       "PRES"),
    ("EXAALT",    "dataset1-5423x3137.x.f32.dat",                "dataset1_x"),
    ("RTM",       "pressure_3000",                               "pressure_3000"),
    ("SYNTHESIS", "synthetic_truss_with_five_defects",           "synthetic_truss"),
]
DISPLAY = {"HACC": "HACC", "CESM": "CESM", "EXAFEL": "EXAFEL", "NYX": "NYX",
           "QMCPACK": "QMCPack", "SCALE": "SCALE", "EXAALT": "EXAALT",
           "RTM": "RTM", "SYNTHESIS": "SYNTHESIS"}


def parse_log(path):
    # data[(ds, mode, ratio)] = {'field': str, 'ratio': float, 'eb': str}
    data = {}
    cur = None  # (ds, field, mode, ratio)
    with open(path) as f:
        for line in f:
            s = line.strip()
            m = re.match(r'^BENCH_START:([^:]+):(.+):(outlier|plain):([0-9.]+)$', s)
            if m:
                ds, field, mode, ratio = m.group(1), m.group(2), m.group(3), float(m.group(4))
                cur = (ds, field, mode, ratio)
                continue
            if cur is None:
                continue
            ds, field, mode, ratio = cur
            # The paper's "Error-bound" column is the relative error bound (RelEB),
            # printed as: "Selected AbsEB: <abs> (RelEB: <rel>)".
            me = re.match(r'Selected AbsEB:\s*[0-9.eE+-]+\s*\(RelEB:\s*([0-9.eE+-]+)\)', s)
            if me:
                data.setdefault((ds, field, mode, ratio), {})['eb'] = me.group(1)
            ma = re.match(r'Achieved Ratio:\s*([0-9.]+)', s)
            if ma:
                data.setdefault((ds, field, mode, ratio), {})['ratio'] = float(ma.group(1))
    return data


def find(data, ds, field_sub, mode, ratio):
    for (d, f, m, r), v in data.items():
        if d == ds and m == mode and abs(r - ratio) < 1e-6 and field_sub in f:
            return v
    return None


def fmt_eb(eb):
    if eb is None:
        return "--"
    try:
        return f"{float(eb):.2e}"
    except ValueError:
        return eb


def main():
    data = parse_log(LOG_FILE)

    # ---- Markdown ----
    md = []
    md.append("# TABLE III — Achieved compression ratios (bold) and error bounds "
              "under target ratios (R = 4, 6, 8)\n")
    header = "| Dataset | Field |"
    sub = "|---|---|"
    for R in (4, 6, 8):
        header += f" R={R} MILIO-p Ratio | Err | R={R} MILIO-o Ratio | Err |"
        sub += "---|---|---|---|"
    md.append(header)
    md.append(sub)
    for ds, field_sub, label in FIELDS:
        row = f"| {DISPLAY[ds]} | {label} |"
        for R in RATIOS:
            for mode in ("plain", "outlier"):
                rec = find(data, ds, field_sub, mode, R)
                ratio = f"**{rec['ratio']:.3f}**" if rec and 'ratio' in rec else "--"
                eb = fmt_eb(rec.get('eb') if rec else None)
                row += f" {ratio} | {eb} |"
        md.append(row)
    with open(OUT_MD, "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\nWrote {OUT_MD}")

    # ---- LaTeX ----
    tex = []
    tex.append(r"\begin{table*}[t]")
    tex.append(r"\centering")
    tex.append(r"\caption{Achieved compression ratios (bold) and corresponding "
               r"error bounds under target ratios ($R=4,6,8$).}")
    tex.append(r"\begin{tabular}{ll" + "cc" * 6 + r"}")
    tex.append(r"\toprule")
    tex.append(r" & & \multicolumn{4}{c}{Target $R=4$} & "
               r"\multicolumn{4}{c}{Target $R=6$} & \multicolumn{4}{c}{Target $R=8$} \\")
    tex.append(r"Dataset & Field & \multicolumn{2}{c}{\textsc{Milio}-p} & "
               r"\multicolumn{2}{c}{\textsc{Milio}-o} & "
               r"\multicolumn{2}{c}{\textsc{Milio}-p} & \multicolumn{2}{c}{\textsc{Milio}-o} & "
               r"\multicolumn{2}{c}{\textsc{Milio}-p} & \multicolumn{2}{c}{\textsc{Milio}-o} \\")
    tex.append(" & & " + " & ".join(["Ratio & Error-bound"] * 6) + r" \\")
    tex.append(r"\midrule")
    for ds, field_sub, label in FIELDS:
        cells = [DISPLAY[ds], label.replace("_", r"\_")]
        for R in RATIOS:
            for mode in ("plain", "outlier"):
                rec = find(data, ds, field_sub, mode, R)
                cells.append(f"\\textbf{{{rec['ratio']:.3f}}}" if rec and 'ratio' in rec else "--")
                cells.append(fmt_eb(rec.get('eb') if rec else None))
        tex.append(" & ".join(cells) + r" \\")
    tex.append(r"\bottomrule")
    tex.append(r"\end{tabular}")
    tex.append(r"\end{table*}")
    with open(OUT_TEX, "w") as f:
        f.write("\n".join(tex) + "\n")
    print(f"Wrote {OUT_TEX}")


if __name__ == "__main__":
    main()
