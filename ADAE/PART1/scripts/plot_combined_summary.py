
import matplotlib.pyplot as plt
import re
import os
import numpy as np
from collections import defaultdict

plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.linewidth'] = 2.0


# Config
LOG_FIXRATIO = "benchmark_fixratio_warmup_output.log"
LOG_CUZFP = "benchmark_cuzfp_output.log"
OUTPUT_FILE_COMP = "benchmark_charts/chart_summary_compression.pdf"
OUTPUT_FILE_DEC = "benchmark_charts/chart_summary_decompression.pdf"

# Rename map
MODE_MAP = {
    "outlier": "MILIO-o",
    "plain": "MILIO-p"
}

def parse_fixratio_log(filepath):
    # data[dataset][ratio][mode]['comp'] = list
    # data[dataset][ratio][mode]['dec'] = list
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'comp': [], 'dec': []})))
    
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
                # Compression
                # "total end-to-end speed:" -> Not what we want? Usually we plot Compression Throughput.
                # Previous script used "total end-to-end speed" for FixRatio?
                # Let's check previous code.
                # "m = re.search(r"speed:\s*([0-9\.]+)", line)" matched "total end-to-end speed: ..."
                # Wait, usually for comparison we use "Compression Throughput" vs "Decompression Throughput".
                # "Total" includes profiling.
                # cuZFP log usually reports compression vs decompression separately.
                # The benchmark_fixratio_all.py prints:
                # " compression end-to-end speed: %f GB/s"
                # " total end-to-end speed: %f GB/s"
                # " decompression end-to-end speed: %f GB/s"
                
                # I should probably plot COMPRESSION speed, not TOTAL (which includes profiling overhead).
                # But previously I was plotting TOTAL for FixRatio?
                # User asked for "benchmarking performance". Usually Comp vs Decomp.
                # Validating previous script: `m = re.search(r"speed:\s*([0-9\.]+)", line)` matches any line with "speed:".
                # The log has "profile end-to-end speed:", "compression end-to-end speed:", "total end-to-end speed:".
                # The PREVIOUS script used `elif "total end-to-end speed:" in line`.
                # So it was plotting TOTAL (Comp + Profile).
                # Does the user want Comp+Profile or just Comp?
                # For "MILIO" (FixRatio), overhead is significant so Total is honest.
                # For Decompression, it's just Decomp.
                
                # Let's stick to Parsing "total" for compression-side bar (to be conservative/honest about overhead)
                # And "decompression" for decompression-side bar.
                
                if "total end-to-end speed:" in line:
                     m = re.search(r"speed:\s*([0-9\.]+)", line)
                     if m: data[current_ds][current_ratio][current_mode]['comp'].append(float(m.group(1)))
                
                elif "decompression end-to-end speed:" in line:
                     m = re.search(r"speed:\s*([0-9\.]+)", line)
                     if m: data[current_ds][current_ratio][current_mode]['dec'].append(float(m.group(1)))
                
                # New Format Support
                elif "Total (Prof+Comp) Thrpt:" in line:
                     m = re.search(r"Thrpt:\s*([0-9\.]+)\s*GB/s", line)
                     if m: data[current_ds][current_ratio][current_mode]['comp'].append(float(m.group(1)))
                
                elif "Decompression Throughput:" in line:
                     m = re.search(r"Throughput:\s*([0-9\.]+)\s*GB/s", line)
                     if m: data[current_ds][current_ratio][current_mode]['dec'].append(float(m.group(1)))

    return data

def parse_cuzfp_log(filepath):
    # data[dataset][ratio]['comp'] = list
    # data[dataset][ratio]['dec'] = list
    data = defaultdict(lambda: defaultdict(lambda: {'comp': [], 'dec': []}))
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data

    current_ds = None
    current_ratio = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("BENCH_START:"):
                parts = line.split(":")
                if len(parts) >= 4:
                    dataset = parts[1]
                    # if dataset == "CESM": dataset = "CESM-ATM"
                    if dataset == "SYNTHESIS": dataset = "SYNTH"
                    ratio = float(parts[3])
                    current_ds = dataset
                    current_ratio = ratio
                else:
                    current_ds = None
            elif current_ds:
                 # Encode
                 if "# encode" in line and "rate:" in line:
                     m = re.search(r"rate:\s*([0-9\.]+)", line)
                     if m: data[current_ds][current_ratio]['comp'].append(float(m.group(1)))
                 # Decode
                 # "# decode3 rate: 163.34 (GB / sec) 512"
                 elif "# decode" in line and "rate:" in line:
                     m = re.search(r"rate:\s*([0-9\.]+)", line)
                     if m: data[current_ds][current_ratio]['dec'].append(float(m.group(1)))
    return data

def plot_combined_v2(fix_data, zfp_data):
    # Datasets
    all_datasets = sorted(list(set(fix_data.keys()) | set(zfp_data.keys())))
    
    # Structure: summary[dataset][mode]['comp'] = avg
    # Structure: summary[dataset][mode]['dec'] = avg
    summary = defaultdict(lambda: defaultdict(lambda: {'comp': 0.0, 'dec': 0.0}))
    
    modes = ["MILIO-o", "MILIO-p", "cuZFP"]
    ratios = [4.0, 6.0, 8.0]
    
    # Per Dataset
    for ds in all_datasets:
        for mode in modes:
            vals_comp = []
            vals_dec = []
            for r in ratios:
                if mode == "cuZFP":
                    v_c = zfp_data[ds][r]['comp']
                    v_d = zfp_data[ds][r]['dec']
                else:
                    v_c = fix_data[ds][r][mode]['comp']
                    v_d = fix_data[ds][r][mode]['dec']
                
                if v_c: vals_comp.extend(v_c)
                if v_d: vals_dec.extend(v_d)
            
            summary[ds][mode]['comp'] = np.mean(vals_comp) if vals_comp else 0.0
            summary[ds][mode]['dec'] = np.mean(vals_dec) if vals_dec else 0.0

    # Global Average
    for mode in modes:
        # Comp Avgs
        avgs_c = [summary[ds][mode]['comp'] for ds in all_datasets if summary[ds][mode]['comp'] > 0]
        summary["Average"][mode]['comp'] = np.mean(avgs_c) if avgs_c else 0.0
        
        # Dec Avgs
        avgs_d = [summary[ds][mode]['dec'] for ds in all_datasets if summary[ds][mode]['dec'] > 0]
        summary["Average"][mode]['dec'] = np.mean(avgs_d) if avgs_d else 0.0
            
    plot_labels = all_datasets + ["Average"]
    colors = ["#ffbfbf", "#bfffff", "#ffffbf"] # Pink, Purple, Yellow

    # Function to plot a single metric (Comp or Dec)
    # Function to plot a single metric (Comp or Dec)
    def plot_metric(metric_key, output_file, ylabel_text="Thrpt. (GB/s)"):
        # Prepare vectors
        y_mo = [summary[d]["MILIO-o"][metric_key] for d in plot_labels]
        y_mp = [summary[d]["MILIO-p"][metric_key] for d in plot_labels]
        y_zfp = [summary[d]["cuZFP"][metric_key] for d in plot_labels]
        
        x = np.arange(len(plot_labels)) * 1.5 # Tighter spacing
        bar_width = 0.35
        
        # Figure Size: Higher (e.g. 16x4.5)
        fig, ax = plt.subplots(figsize=(17, 4.5))
        
        # Styles
        # MILLIO-p: Orange, hatch \\
        # MILLIO-o: Green, hatch //
        # cuZFP: Red, hatch xx
        # Facecolor white, EdgeInsets colored
        
        # Colors
        COLOR_PLAIN = '#d95e03'   # Orange
        COLOR_OUTLIER = '#1c9e78' # Green
        COLOR_ZFP = '#1f77b4'     # Blue (Vivid)

        style_mo = {'color': 'white', 'edgecolor': COLOR_OUTLIER, 'hatch': '//', 'linewidth': 1.0}
        style_mp = {'color': 'white', 'edgecolor': COLOR_PLAIN, 'hatch': '\\\\', 'linewidth': 1.0}
        style_zfp = {'color': 'white', 'edgecolor': COLOR_ZFP, 'hatch': 'xx', 'linewidth': 1.0}

        # Plot bars
        r1 = ax.bar(x - bar_width, y_mo, bar_width, label='MILIO-o', **style_mo)
        r2 = ax.bar(x, y_mp, bar_width, label='MILIO-p', **style_mp)
        r3 = ax.bar(x + bar_width, y_zfp, bar_width, label='cuZFP', **style_zfp)
        
        # Overlay Black Borders
        ax.bar(x - bar_width, y_mo, bar_width, color='none', edgecolor='black', linewidth=1.0)
        ax.bar(x, y_mp, bar_width, color='none', edgecolor='black', linewidth=1.0)
        ax.bar(x + bar_width, y_zfp, bar_width, color='none', edgecolor='black', linewidth=1.0)
        
        ax.set_ylabel(ylabel_text, fontsize=34)
        ax.tick_params(axis='y', labelsize=32)
        
        ax.set_xticks(x)
        # Rotated labels as requested
        ax.set_xticklabels(plot_labels, rotation=20, ha='right', fontsize=34)
        
        # Increase Y-axis ticks
        from matplotlib.ticker import MaxNLocator
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
        
        # Bold Average
        xtick_labels = ax.get_xticklabels()
        if xtick_labels:
            xtick_labels[-1].set_fontweight('bold')
            # It retains italic from set_xticklabels usually
            
        # Grid: Dotted, enable both X and Y
        ax.set_axisbelow(True) # Ensure grid is behind bars
        ax.grid(axis='y', linestyle=':', alpha=0.8, color='gray')
        ax.grid(axis='x', linestyle=':', alpha=0.5, color='gray')
        
        # Legend: Right Side
        from matplotlib.patches import Patch
        # Create base patches (Colored Hatch)
        p1 = Patch(facecolor='white', edgecolor=COLOR_OUTLIER, hatch='//')
        p2 = Patch(facecolor='white', edgecolor=COLOR_PLAIN, hatch='\\\\')
        p3 = Patch(facecolor='white', edgecolor=COLOR_ZFP, hatch='xx')
        
        # Create overlay patch (Black Border)
        p_frame = Patch(facecolor='none', edgecolor='black', linewidth=1.0)
        
        # Combine handles
        handles = [(p1, p_frame), (p2, p_frame), (p3, p_frame)]
        labels = ['MILIO-o', 'MILIO-p', 'cuZFP']
        
        # Place legend outside to the right
        ax.legend(handles=handles, labels=labels, fontsize=34, handlelength=1.2, loc='center left', bbox_to_anchor=(0.98, 0.5), frameon=False)
        
        # Adjust layout to fit legend
        plt.tight_layout() # pad handled automatically usually
        
        # Label ONLY standard 'Average' bars or key features
        # User requested: "Don't label all numbers, just pick a few characteristic ones"
        # We will label (1) The Average column (last column)
        
        def label_bar(rect, pos):
            height = rect.get_height()
            if height > 0:
                if pos == 'left':
                    # To the left of the bar's top-left corner
                    ax.annotate(f'{height:.0f}',
                                xy=(rect.get_x(), height),
                                xytext=(-5, 0),
                                textcoords="offset points",
                                ha='right', va='center', fontsize=28, rotation=40, color='black')
                elif pos == 'right':
                    # To the right of the bar's top-right corner
                    ax.annotate(f'{height:.0f}',
                                xy=(rect.get_x() + rect.get_width(), height),
                                xytext=(-10, 15),
                                textcoords="offset points",
                                ha='left', va='center', fontsize=28, rotation=40, color='black')
                else: # top
                    # On top of the bar
                    ax.annotate(f'{height:.0f}',
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=28, rotation=40, color='black')

        # Only label the last group (Average) which is at index len(plot_labels)-1
        avg_idx = len(plot_labels) - 1
        
        label_bar(r1[avg_idx], 'left')
        label_bar(r2[avg_idx], 'top')
        label_bar(r3[avg_idx], 'right')

        # Custom padding using 4 numbers (margins)
        # left, bottom, right, top
        # plt.subplots_adjust(left=0.11, bottom=0.30, right=0.81, top=0.93)
        plt.subplots_adjust(left=0.11, bottom=0.29, right=0.81, top=0.97)
        plt.savefig(output_file, dpi=300) # Remove bbox_inches='tight' to respect subplots_adjust
        print(f"Generated chart: {output_file}")
        plt.close(fig)

    # Generate both charts
    plot_metric('comp', OUTPUT_FILE_COMP)
    plot_metric('dec', OUTPUT_FILE_DEC)

if __name__ == "__main__":
    print("Parsing logs...")
    d_fix = parse_fixratio_log(LOG_FIXRATIO)
    print(f"FixRatio - Models: {list(d_fix.keys())}")
        
    d_zfp = parse_cuzfp_log(LOG_CUZFP)
    print(f"cuZFP - Models: {list(d_zfp.keys())}")
        
    print("Generating charts...")
    plot_combined_v2(d_fix, d_zfp)
