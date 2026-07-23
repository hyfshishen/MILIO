
import matplotlib.pyplot as plt
import re
import os
import numpy as np
from collections import defaultdict

plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.linewidth'] = 2.0

# Config
LOG_FILE = "benchmark_fixratio_warmup_output.log"
OUTPUT_FILE = "benchmark_charts/chart_rtm_overhead_trend.pdf"
os.makedirs("benchmark_charts", exist_ok=True)

def parse_log(filepath):
    # data[field_id][mode][ratio]['profile'] = value
    # data[field_id][mode][ratio]['compression'] = value
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data

    current_field = None
    current_mode = None
    current_ratio = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("BENCH_START:RTM:pressure_"):
                # Example: BENCH_START:RTM:pressure_1000:outlier:4.0
                parts = line.split(":")
                if len(parts) >= 5:
                    full_name = parts[2] # pressure_1000
                    # Extract 1000/2000/3000
                    m_field = re.search(r"pressure_(\d+)", full_name)
                    if m_field:
                        field_id = m_field.group(1)
                        mode_raw = parts[3]
                        ratio = float(parts[4])
                        
                        current_field = field_id
                        # Map mode "outlier"->"MILIO-o", "plain"->"MILIO-p"
                        current_mode = "MILIO-o" if mode_raw == "outlier" else "MILIO-p"
                        current_ratio = ratio
                    else:
                        current_field = None
                else:
                    current_field = None
                    
            elif current_field:
                # Legacy format
                if "profile end-to-end speed:" in line:
                    m = re.search(r"speed:\s*([0-9\.]+)", line)
                    if m: data[current_field][current_mode][current_ratio]['profile'].append(float(m.group(1)))

                elif "compression end-to-end speed:" in line:
                    m = re.search(r"speed:\s*([0-9\.]+)", line)
                    if m: data[current_field][current_mode][current_ratio]['compression'].append(float(m.group(1)))

                # Current CLI format
                elif "Profiling Throughput:" in line:
                    m = re.search(r"Throughput:\s*([0-9\.]+)\s*GB/s", line)
                    if m: data[current_field][current_mode][current_ratio]['profile'].append(float(m.group(1)))

                elif "Compression Throughput:" in line:
                    m = re.search(r"Throughput:\s*([0-9\.]+)\s*GB/s", line)
                    if m: data[current_field][current_mode][current_ratio]['compression'].append(float(m.group(1)))

    return data

def plot_rtm_trend(data):
    # Sorted fields: 1000, 2000, 3000
    fields = sorted(list(data.keys()), key=lambda x: int(x))
    print(f"Found fields: {fields}")
    
    target_ratio = 4.0
    
    # We want X-axis = p1000, p2000, p3000
    x_labels = [f"p{f}" for f in fields]
    x_pos = np.arange(len(fields))
    
    # Setup Figure
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Lines: MILIO-o, MILIO-p
    # Colors: Outlier=Red, Plain=Blue (consistent with other charts)
    modes = ["MILIO-p", "MILIO-o"]
    colors = {"MILIO-p": "#d95e03", "MILIO-o": "#1c9e78"} # Orange, Green
    markers = {"MILIO-p": "s", "MILIO-o": "^"} # Square, Triangle
    linestyles = {"MILIO-p": "--", "MILIO-o": "-"}

    for mode in modes:
        y_vals = []
        valid_x = []
        
        for i, field in enumerate(fields):
            profs = data[field][mode][target_ratio]['profile']
            comps = data[field][mode][target_ratio]['compression']
            
            if profs and comps:
                # Calc Overhead
                t_p = np.mean([1.0/v for v in profs])
                t_c = np.mean([1.0/v for v in comps])
                oh = t_p / t_c
                y_vals.append(oh)
                valid_x.append(x_pos[i])
        
        if y_vals:
            ax.plot(valid_x, y_vals,
                    label=mode,
                    color=colors[mode],
                    marker=markers[mode],
                    linestyle=linestyles[mode],
                    linewidth=3.0,
                    markersize=12)
    
    # Formatting
    # ax.set_xlabel('RTM Fields', fontsize=20)
    ax.set_ylabel('Overhead', fontsize=32)
    ax.tick_params(axis='both', labelsize=30)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=30)
    
    # Grid
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    
    # Legend: Top
    ax.legend(fontsize=23, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.44), ncol=1)
    
    # Margins
    plt.tight_layout()
    # Ensure top margin for legend
    
    plt.subplots_adjust(left=0.25, bottom=0.29, right=0.99, top=0.82)
    
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Generated chart: {OUTPUT_FILE}")
    plt.close(fig)

if __name__ == "__main__":
    print("Parsing logs...")
    data = parse_log(LOG_FILE)
    print("Generating chart with Ratio=4.0...")
    plot_rtm_trend(data)
