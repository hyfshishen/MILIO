
import matplotlib.pyplot as plt
import re
import os
import numpy as np
from collections import defaultdict

plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.linewidth'] = 2.0


# Config
LOG_FILE = "benchmark_fixratio_warmup_output.log"
OUTPUT_DIR = "benchmark_charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Rename map
MODE_MAP = {
    "outlier": "MILIO-o",
    "plain": "MILIO-p"
}

def parse_log(filepath):
    # data[dataset][ratio][mode][metric] = list of values
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
                # BENCH_START:CESM:outlier:4: ...
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
                if "profile end-to-end speed:" in line:
                    m = re.search(r"speed:\s*([0-9\.]+)", line)
                    if m: data[current_ds][current_ratio][current_mode]['profile'].append(float(m.group(1)))
                
                elif "compression end-to-end speed:" in line:
                    m = re.search(r"speed:\s*([0-9\.]+)", line)
                    if m: data[current_ds][current_ratio][current_mode]['compression'].append(float(m.group(1)))
                    
                elif "total end-to-end speed:" in line:
                    m = re.search(r"speed:\s*([0-9\.]+)", line)
                    if m: data[current_ds][current_ratio][current_mode]['total'].append(float(m.group(1)))
                
                # New Format Support
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

def plot_breakdown(data, target_mode, output_path):
    # Aggregate data
    # summary[dataset][metric] = mean value
    summary = defaultdict(lambda: defaultdict(float))
    
    datasets = sorted(list(data.keys()))
    metrics = ['profile', 'compression', 'total']
    
    # Process each dataset
    valid_datasets = []
    
    for ds in datasets:
        # Check if we have data for this mode
        has_data = False
        # Average across ratios
        for metric in metrics:
            vals = []
            for r in [4.0, 6.0, 8.0]:
                v = data[ds][r][target_mode][metric]
                if v: vals.extend(v)
            if vals:
                summary[ds][metric] = np.mean(vals)
                has_data = True
            else:
                summary[ds][metric] = 0.0
        
        if has_data:
            valid_datasets.append(ds)

    # Compute Global Average
    summary["Average"] = defaultdict(float)
    for metric in metrics:
        all_vals = []
        for ds in valid_datasets:
            if summary[ds][metric] > 0:
                all_vals.append(summary[ds][metric])
        summary["Average"][metric] = np.mean(all_vals) if all_vals else 0.0
        
    plot_labels = valid_datasets + ["Average"]
    
    # Vectors
    y_profile = [summary[d]['profile'] for d in plot_labels]
    y_comp = [summary[d]['compression'] for d in plot_labels]
    y_total = [summary[d]['total'] for d in plot_labels]
    
    # Plotting
    x = np.arange(len(plot_labels)) * 1.5
    bar_width = 0.35
    
    # Figure Size: Higher (e.g. 16x4.5)
    fig, ax = plt.subplots(figsize=(17, 4.5))
    
    # Styles
    # Profile: Orange, hatch ..
    # Compression: Blue, hatch \\
    # Total: Green, hatch xx
    
    style_prof = {'color': 'white', 'edgecolor': '#ff7f0e', 'hatch': '..', 'linewidth': 1.0}
    style_comp = {'color': 'white', 'edgecolor': '#1f77b4', 'hatch': '\\\\', 'linewidth': 1.0}
    style_tot = {'color': 'white', 'edgecolor': '#2ca02c', 'hatch': 'xx', 'linewidth': 1.0}

    r1 = ax.bar(x - bar_width, y_profile, bar_width, label='Profile', **style_prof)
    r2 = ax.bar(x, y_comp, bar_width, label='Compression', **style_comp)
    r3 = ax.bar(x + bar_width, y_total, bar_width, label='Total (End-to-End)', **style_tot)
    
    # Overlay Black Borders
    ax.bar(x - bar_width, y_profile, bar_width, color='none', edgecolor='black', linewidth=1.0)
    ax.bar(x, y_comp, bar_width, color='none', edgecolor='black', linewidth=1.0)
    ax.bar(x + bar_width, y_total, bar_width, color='none', edgecolor='black', linewidth=1.0)
    
    ax.set_ylabel('Thrpt. (GB/s)', fontsize=34)
    ax.tick_params(axis='y', labelsize=32)
    
    ax.set_xticks(x)
    # Rotated labels
    ax.set_xticklabels(plot_labels, rotation=20, ha='right', fontsize=34)
    
    # Increase Y-axis ticks
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    
    # Bold Average
    xtick_labels = ax.get_xticklabels()
    if xtick_labels:
        xtick_labels[-1].set_fontweight('bold')
        
    # Legend: Right Side
    from matplotlib.patches import Patch
    
    p1 = Patch(facecolor='white', edgecolor='#ff7f0e', hatch='..')
    p2 = Patch(facecolor='white', edgecolor='#1f77b4', hatch='\\\\')
    p3 = Patch(facecolor='white', edgecolor='#2ca02c', hatch='xx')
    
    p_frame = Patch(facecolor='none', edgecolor='black', linewidth=1.0)
    
    handles = [(p1, p_frame), (p2, p_frame), (p3, p_frame)]
    labels = ['Profile', 'Comp.', 'Total']

    ax.legend(handles=handles, labels=labels, fontsize=34, handlelength=1.2, loc='center left', bbox_to_anchor=(0.98, 0.5), frameon=False)
    
    # Grid
    ax.set_axisbelow(True)
    ax.grid(axis='y', linestyle=':', alpha=0.8, color='gray')
    ax.grid(axis='x', linestyle=':', alpha=0.5, color='gray')
    
    ax.set_ylim(0, 1200)
    
    # Label all bars (Small) -> ONLY Average
    def label_bar(rect, pos):
        height = rect.get_height()
        if height > 0:
            effective_y = min(height, 1200)
            
            if pos == 'left':
                ax.annotate(f'{height:.0f}',
                            xy=(rect.get_x(), effective_y),
                            xytext=(-5, -5),
                            textcoords="offset points",
                            ha='right', va='top', fontsize=28, rotation=40, color='black')
            elif pos == 'right':
                ax.annotate(f'{height:.0f}',
                            xy=(rect.get_x() + rect.get_width(), effective_y),
                            xytext=(-10, 15),
                            textcoords="offset points",
                            ha='left', va='top', fontsize=28, rotation=40, color='black')
            else: # top
                ax.annotate(f'{height:.0f}',
                            xy=(rect.get_x() + rect.get_width() / 2, effective_y),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=28, rotation=40, color='black')

    # Label 'Average' group AND any bar > 1200
    avg_idx = len(plot_labels) - 1
    
    for i in range(len(plot_labels)):
        height1 = r1[i].get_height()
        height2 = r2[i].get_height()
        height3 = r3[i].get_height()
        
        is_avg = (i == avg_idx)
        
        # Profile (r1) -> Left
        if is_avg or height1 > 1100:
            label_bar(r1[i], 'left')
            
        # Compression (r2) -> Top
        if is_avg or height2 > 1100:
            label_bar(r2[i], 'top')
            
        # Total (r3) -> Right
        if is_avg or height3 > 1100:
            label_bar(r3[i], 'right')
    
    # Custom padding using 4 numbers (margins)
    # left, bottom, right, top
    plt.subplots_adjust(left=0.11, bottom=0.29, right=0.84, top=0.95)
    plt.savefig(output_path, dpi=300) # Remove bbox_inches='tight' to respect subplots_adjust
    print(f"Generated chart: {output_path}")
    plt.close(fig)

if __name__ == "__main__":
    print("Parsing logs...")
    data = parse_log(LOG_FILE)
    
    print("Generating charts...")
    plot_breakdown(data, "MILIO-p", "benchmark_charts/chart_breakdown_millio_p.pdf")
    plot_breakdown(data, "MILIO-o", "benchmark_charts/chart_breakdown_millio_o.pdf")
