
import matplotlib.pyplot as plt
import re
import os
import numpy as np
from collections import defaultdict

plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.linewidth'] = 2.0

import matplotlib.patches as mpatches

# Config
LOG_FILE = "benchmark_fixratio_warmup_output.log"
OUTPUT_FILE = "benchmark_charts/chart_overhead_normalized.pdf"
os.makedirs("benchmark_charts", exist_ok=True)

# Rename map
MODE_MAP = {
    "outlier": "MILIO-o",
    "plain": "MILIO-p"
}

def parse_log(filepath):
    # data[dataset][ratio][mode]['profile'] = value
    # data[dataset][ratio][mode]['compression'] = value
    # data[dataset][ratio][mode]['total'] = value
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data

    current_ds = None
    current_mode = None
    current_ratio = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("BENCH_START:"):
                parts = line.split(":")
                if len(parts) >= 5:
                    dataset = parts[1]
                    # if dataset == "CESM": dataset = "CESM-ATM"
                    if dataset == "SYNTHESIS": dataset = "SYNTH"
                    mode_raw = parts[3]
                    ratio = float(parts[4])
                    current_ds = dataset
                    current_mode = MODE_MAP.get(mode_raw, mode_raw)
                    current_ratio = ratio
                else:
                    current_ds = None
                    
            elif current_ds:
                # Support Legacy Format
                if "profile end-to-end speed:" in line:
                    m = re.search(r"speed:\s*([0-9\.]+)", line)
                    if m: data[current_ds][current_ratio][current_mode]['profile'].append(float(m.group(1)))
                
                elif "compression end-to-end speed:" in line:
                    m = re.search(r"speed:\s*([0-9\.]+)", line)
                    if m: data[current_ds][current_ratio][current_mode]['compression'].append(float(m.group(1)))
                    
                elif "total end-to-end speed:" in line:
                    m = re.search(r"speed:\s*([0-9\.]+)", line)
                    if m: data[current_ds][current_ratio][current_mode]['total'].append(float(m.group(1)))

                # Support New Format
                # "  Profiling Throughput:    %.2f GB/s"
                elif "Profiling Throughput:" in line:
                    m = re.search(r"Throughput:\s*([0-9\.]+)\s*GB/s", line)
                    if m: data[current_ds][current_ratio][current_mode]['profile'].append(float(m.group(1)))
                
                elif "Compression Throughput:" in line:
                    m = re.search(r"Throughput:\s*([0-9\.]+)\s*GB/s", line)
                    if m: data[current_ds][current_ratio][current_mode]['compression'].append(float(m.group(1)))
                    
                elif "Total (Prof+Comp) Thrpt:" in line:
                    m = re.search(r"Thrpt:\s*([0-9\.]+)\s*GB/s", line)
                    if m: data[current_ds][current_ratio][current_mode]['total'].append(float(m.group(1)))

    return data

def plot_normalized_overhead(data):
    datasets = sorted(list(data.keys()))
    
    # summary[ds][mode]['val']
    summary = defaultdict(lambda: defaultdict(dict))
    valid_datasets = []
    
    modes = ['MILIO-p', 'MILIO-o']
    
    for ds in datasets:
        has_data = False
        for mode in modes:
            comp_vals = []
            prof_vals = []
            total_vals = []
            
            # User requested ONLY Ratio 4.0
            for r in [4.0]:
                v_c = data[ds][r][mode]['compression']
                v_p = data[ds][r][mode]['profile']
                v_t = data[ds][r][mode]['total']
                
                if v_c: comp_vals.extend(v_c)
                if v_p: prof_vals.extend(v_p)
                if v_t: total_vals.extend(v_t)
            
            if comp_vals and prof_vals and total_vals:
                # Convert Speed to Time (Time = Size / Speed)
                # Since Size is constant per dataset, Time ~ 1/Speed
                t_c_list = [1.0/v for v in comp_vals]
                t_p_list = [1.0/v for v in prof_vals]
                t_t_list = [1.0/v for v in total_vals]
                
                avg_time_comp = np.mean(t_c_list)
                avg_time_prof = np.mean(t_p_list)
                avg_time_total = np.mean(t_t_list)
                
                avg_time_comp = np.mean(t_c_list)
                avg_time_prof = np.mean(t_p_list)
                
                # Stack Overhead = Prof_Time / Comp_Time
                overhead = avg_time_prof / avg_time_comp
                summary[ds][mode]['overhead'] = overhead
                
                # Force Total Bar to match Stack Height (Comp + Prof)
                # This aligns with user expectation that Total = Comp + Prof in code logic
                summary[ds][mode]['total_rel'] = 1.0 + overhead
                
                has_data = True
            else:
                summary[ds][mode]['overhead'] = 0.0
                summary[ds][mode]['total_rel'] = 0.0
        
        if has_data:
            valid_datasets.append(ds)
            
    # Global Average
    summary['Average'] = defaultdict(dict)
    for mode in modes:
        vals_oh = [summary[ds][mode]['overhead'] for ds in valid_datasets if summary[ds][mode]['overhead'] > 0]
        vals_tot = [summary[ds][mode]['total_rel'] for ds in valid_datasets if summary[ds][mode]['total_rel'] > 0]
        
        summary['Average'][mode]['overhead'] = np.mean(vals_oh) if vals_oh else 0.0
        summary['Average'][mode]['total_rel'] = np.mean(vals_tot) if vals_tot else 0.0
        
    plot_labels = valid_datasets + ["Average"]
    
    # Vectors
    y_base = [1.0 for _ in plot_labels]
    
    y_oh_p = [summary[d]['MILIO-p']['overhead'] for d in plot_labels]
    y_tot_p = [summary[d]['MILIO-p']['total_rel'] for d in plot_labels]
    
    y_oh_o = [summary[d]['MILIO-o']['overhead'] for d in plot_labels]
    y_tot_o = [summary[d]['MILIO-o']['total_rel'] for d in plot_labels]
    # Plotting
    x = np.arange(len(plot_labels)) * 1.5
    
    # Styles
    # Plain: Stripe ///
    # Outlier: Cross ***
    
    # Styles
    # Plain: Stripe ///
    # Outlier: Cross ***
    
    # Colors
    c_comp = '#1f77b4' # Blue (Compression)
    c_over = '#f1c40f' # Sunflower Yellow (Overhead)
    
    # Plain Styles (Left Bar)
    # Base = Compression = Blue
    s_p_base = {'facecolor': 'white', 'edgecolor': c_comp, 'hatch': '///', 'linewidth': 1.0}
    # Top = Overhead = Yellow
    s_p_over = {'facecolor': 'white', 'edgecolor': c_over, 'hatch': '///', 'linewidth': 1.0}
    
    # Outlier Styles (Right Bar)
    # Base = Compression = Blue
    s_o_base = {'facecolor': 'white', 'edgecolor': c_comp, 'hatch': '***', 'linewidth': 1.0}
    # Top = Overhead = Yellow
    s_o_over = {'facecolor': 'white', 'edgecolor': c_over, 'hatch': '***', 'linewidth': 1.0}
    
    w = 0.45
    gap = 0.05
    
    pos_p = x - w/2 - gap/2
    pos_o = x + w/2 + gap/2
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # --- Plain Stacked ---
    # Bottom: Baseline (1.0)
    ax.bar(pos_p, y_base, w, label='Compression', **s_p_base)
    # Top: Overhead
    ax.bar(pos_p, y_oh_p, w, bottom=y_base, label='Overhead (Plain)', **s_p_over)
    
    # --- Outlier Stacked ---
    # Bottom: Baseline (1.0)
    ax.bar(pos_o, y_base, w, **s_o_base)
    # Top: Overhead
    ax.bar(pos_o, y_oh_o, w, bottom=y_base, label='Overhead (Outlier)', **s_o_over)
    
    # --- Overlay Black Borders ---
    # Plain Base
    ax.bar(pos_p, y_base, w, color='none', edgecolor='black', linewidth=1.0)
    # Plain Overhead
    ax.bar(pos_p, y_oh_p, w, bottom=y_base, color='none', edgecolor='black', linewidth=1.0)
    
    # Outlier Base
    ax.bar(pos_o, y_base, w, color='none', edgecolor='black', linewidth=1.0)
    # Outlier Overhead
    ax.bar(pos_o, y_oh_o, w, bottom=y_base, color='none', edgecolor='black', linewidth=1.0)
    
    ax.set_ylabel('Relative time', fontsize=32)
    ax.tick_params(axis='y', labelsize=30)
    
    ax.set_xticks(x)
    ax.set_xticklabels(plot_labels, rotation=30, ha='right', fontsize=30)
    
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.set_ylim(0, 1.6)
    
    # Bold Average
    xtick_labels = ax.get_xticklabels()
    if xtick_labels:
        xtick_labels[-1].set_fontweight('bold')
        
    ax.set_axisbelow(True)
    ax.grid(axis='y', linestyle=':', alpha=0.8, color='gray')
    ax.grid(axis='x', linestyle=':', alpha=0.5, color='gray')
    
    # Legend
    from matplotlib.patches import Patch
    
    # Helpers for legend handles with black overlay
    def create_handle(facecolor, edgecolor, hatch):
        p_colored = Patch(facecolor=facecolor, edgecolor=edgecolor, hatch=hatch)
        p_frame = Patch(facecolor='none', edgecolor='black', linewidth=1.0)
        return (p_colored, p_frame)

    # Requested Order:
    # Compression (MILIO-p) -> Blue, ///
    # Compression (MILIO-o) -> Blue, ***
    # Profiling (MILIO-p)   -> Yellow, ///
    # Profiling (MILIO-o)   -> Yellow, ***
    
    h_c_p = create_handle('white', c_comp, '///')
    h_c_o = create_handle('white', c_comp, '***')
    h_p_p = create_handle('white', c_over, '///')
    h_p_o = create_handle('white', c_over, '***')
    
    legend_handles = [h_c_p, h_c_o, h_p_p, h_p_o]
    legend_labels = ['Compression (MILIO-p)', 'Compression (MILIO-o)', 'Profiling (MILIO-p)', 'Profiling (MILIO-o)']
    
    ax.legend(handles=legend_handles, labels=legend_labels, fontsize=23, handlelength=1.2, loc='upper center', bbox_to_anchor=(0.5, 1.44), ncol=2, frameon=False)
    
    # Annotations Disabled
    def label_top(rects, label_vals, color='black'):
        pass
    
    # No calls to label_top
    
    plt.subplots_adjust(left=0.125, bottom=0.29, right=0.99, top=0.82)
    
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Generated chart: {OUTPUT_FILE}")
    plt.close(fig)

if __name__ == "__main__":
    print("Parsing logs...")
    data = parse_log(LOG_FILE)
    print("Generating charts...")
    plot_normalized_overhead(data)
