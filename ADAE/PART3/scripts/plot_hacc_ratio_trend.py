#!/usr/bin/env python3
# Reproduces the paper's Fig. 13 (fig:Compression_Ratio_range): target vs.
# achieved compression ratio across all six HACC fields (vx, vy, vz, xx, yy, zz)
# for MILIO-p and MILIO-o at target ratios R = 4, 6, 8.
#
# Reads the fixed-ratio benchmark log produced by run_part3.sh
# (benchmark_fixratio_warmup_output.log, same log that feeds TABLE III) and
# writes benchmark_charts/chart_hacc_ratio_trend.pdf.
import matplotlib.pyplot as plt
import re
import os
import numpy as np
from collections import defaultdict

plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.linewidth'] = 2.0

LOG_FILE = "benchmark_fixratio_warmup_output.log"
OUTPUT_FILE = "benchmark_charts/chart_hacc_ratio_trend.pdf"
os.makedirs("benchmark_charts", exist_ok=True)


def parse_log(filepath):
    # data[field][target_ratio][mode] = achieved_ratio
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data

    current_field = None
    current_target = None
    current_mode = None
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # BENCH_START:HACC:vy.f32:outlier:4.0
            m = re.match(r'^BENCH_START:HACC:([^:]+):(outlier|plain):([0-9.]+)$', line)
            if m:
                current_field = m.group(1).replace(".f32", "")
                current_mode = "MILIO-o" if m.group(2) == "outlier" else "MILIO-p"
                current_target = float(m.group(3))
                continue
            if line.startswith("BENCH_START:"):   # a different dataset
                current_field = None
                continue
            if current_field is not None:
                # CLI prints "  Achieved Ratio: 4.13"
                ma = re.match(r'Achieved Ratio:\s*([0-9.]+)', line)
                if ma:
                    data[current_field][current_target][current_mode] = float(ma.group(1))
                    current_field = None   # one achieved ratio per block
    return data


def plot_hacc_ratio(data):
    all_fields = list(data.keys())
    desired_order = ["vx", "vy", "vz", "xx", "yy", "zz"]
    fields = [f for f in desired_order if f in all_fields]
    for f in all_fields:
        if f not in fields:
            fields.append(f)
    print(f"Found fields: {fields}")
    if not fields:
        print("No HACC data found; skipping chart_hacc_ratio_trend.pdf")
        return

    x_pos = np.arange(len(fields))
    targets = [4.0, 6.0, 8.0]
    modes = ["MILIO-p", "MILIO-o"]

    fig, ax = plt.subplots(figsize=(16, 4))
    mode_colors = {"MILIO-p": "#d95e03", "MILIO-o": "#1c9e78"}
    ratio_markers = {4.0: 'o', 6.0: 's', 8.0: '^'}
    mode_linestyles = {"MILIO-p": '--', "MILIO-o": '-'}

    for t in targets:
        marker = ratio_markers[t]
        ax.axhline(y=t, color='red', linestyle=':', alpha=0.6, linewidth=2.0)
        for mode in modes:
            y_vals, valid_x = [], []
            for i, f in enumerate(fields):
                val = data[f][t].get(mode, None)
                if val:
                    y_vals.append(val)
                    valid_x.append(x_pos[i])
            if y_vals:
                ax.plot(valid_x, y_vals,
                        color=mode_colors[mode], marker=marker,
                        linestyle=mode_linestyles[mode], linewidth=2.5,
                        markersize=23, label=f"T={int(t)} ({mode})")

    ax.set_ylabel('Comp. Ratio', fontsize=32)
    ax.set_yticks([4, 5, 6, 7, 8])
    ax.tick_params(axis='both', labelsize=32)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(fields, fontsize=32, rotation=0)
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(fontsize=30, frameon=False, loc='upper left', bbox_to_anchor=(1.0, 1.1))

    plt.tight_layout()
    plt.subplots_adjust(left=0.06, bottom=0.15, right=0.7, top=0.98)
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Generated chart: {OUTPUT_FILE}")
    plt.close(fig)


if __name__ == "__main__":
    print("Parsing logs...")
    data = parse_log(LOG_FILE)
    print("Generating chart...")
    plot_hacc_ratio(data)
