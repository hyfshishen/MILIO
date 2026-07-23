
import matplotlib.pyplot as plt
import re
import os
import numpy as np
from collections import defaultdict
from matplotlib.ticker import MaxNLocator


# Config
LOG_FILE = "benchmark_eb_accuracy_output.log"
OUTPUT_FILE = "benchmark_charts/chart_eb_density.pdf"

# Rename map
MODE_MAP = {
    "outlier": "MILLIO-o",
    "plain": "MILLIO-p"
}


# Styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.linewidth'] = 2.0
plt.rcParams.update({'font.size': 60}) # Base size, will adjust specific elements
plt.rcParams['lines.linewidth'] = 2.0
plt.rcParams['lines.markersize'] = 8

def parse_log(filepath):
    # data[dataset][mode] = list of (predicted, true) tuples
    data = defaultdict(lambda: defaultdict(list))
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data

    current_ds = None
    current_mode = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("BENCH_START:"):
                # BENCH_START:Dataset:File:Mode
                parts = line.split(":")
                if len(parts) >= 4:
                    dataset = parts[1]
                    filename = parts[2]
                    mode_raw = parts[3]
                    
                    if dataset == "RTM" and "pressure_3000" not in filename:
                        current_ds = None
                    else:
                        current_ds = dataset
                        current_mode = MODE_MAP.get(mode_raw, mode_raw)
                else:
                    current_ds = None
            
            elif current_ds and line.startswith("DATA:"):
                # DATA:i:rel_eb:est:true
                parts = line.split(":")
                if len(parts) >= 5:
                    est = float(parts[3])
                    true_val = float(parts[4])
                    
                    if true_val != 0:
                        data[current_ds][current_mode].append((est, true_val))

    return data

def plot_density(data): # Keeping name to avoid changing main call
    datasets = sorted(list(data.keys()))
    
    desired_order = ["NYX", "HACC", "CESM-ATM", "EXAFEL", "RTM", "QMCPACK", "SYNTHESIS", "EXAALT", "SCALE"]
    # Filter datasets present
    plot_datasets = []
    for d in desired_order: 
        if d in datasets: plot_datasets.append(d)
    # Add any others at end
    for d in datasets:
        if d not in plot_datasets: plot_datasets.append(d)
    
    colors = {"MILLIO-o": "#1c9e78", "MILLIO-p": "#d95e03"} # Green, Orange
    markers = {"MILLIO-o": "o", "MILLIO-p": "^"}
    
    # Custom Zoom Ranges (Min, Max) for each dataset
    # Calculated based on approx Front 10% (P0-P10)
    CUSTOM_ZOOM = {
        "CESM": (3, 20.9),
        "EXAALT": (1.5, 4.4),
        "EXAFEL": (2.0, 80.4),
        "HACC": (1.9, 20.2),
        "NYX": (10, 50), # Adjusted for high variance, just a guess based on logs
        "QMCPACK": (2.0, 20.4),
        "RTM": (2.7, 20.4),
        "SCALE": (1.6, 10.6),
        "SYNTHESIS": (30.4, 50.3)
    }

    for i, ds in enumerate(plot_datasets):
        # Create separate figure for each dataset
        fig, ax = plt.subplots(figsize=(12, 10))
        
        all_est = []
        all_true = []
        
        # Plot each mode
        for mode in ["MILLIO-p", "MILLIO-o"]: # Order: Plain then Outlier
            points = data[ds][mode]
            if not points: continue
            
            est = [p[0] for p in points]
            true_vals = [p[1] for p in points]
            
            all_est.extend(est)
            all_true.extend(true_vals)
            
            ax.scatter(est, true_vals, label=mode, color=colors[mode], marker=markers[mode], s=300, alpha=0.7, edgecolors='none') # Increased s=300 for visibility
        
        # Add Y=X Reference Line
        if all_est and all_true:
            min_val = min(min(all_est), min(all_true))
            max_val = max(max(all_est), max(all_true))
            # Pad slightly
            padding = (max_val - min_val) * 0.1
            limit_min = max(0, min_val - padding)
            limit_max = max_val + padding
            
            ax.plot([limit_min, limit_max], [limit_min, limit_max], 'k--', linewidth=3.0, alpha=0.6)
            
        # No Title as requested
        # ax.set_title(ds, fontsize=56, fontweight='bold', pad=15)
        
        ax.set_xlabel("Profiled Ratio", fontsize=70)
        ax.set_ylabel("True Ratio", fontsize=70)
        # Freely adjust Y-label using (x, y) relative to axes. 
        # x < 0 moves left, y=0.5 centers vertically.
        ax.yaxis.set_label_coords(-0.17, 0.5) 
        ax.tick_params(axis='both', labelsize=60)
        
        
        # Limit to ~4 integer ticks (nbins=3 intervals = 4 ticks)
        # integer=True forces integer locations
        ax.xaxis.set_major_locator(MaxNLocator(nbins=3, integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=3, integer=True))
        
        ax.grid(True, linestyle=':', alpha=0.6, linewidth=2.0)
        
        # Add legend to ALL plots since they are separate
        # bbox_to_anchor=(x, y): Fine-tune position. (0, 1) is top-left of axes.
        # markerscale: Adjust size of markers in legend.
        ax.legend(loc='upper left', bbox_to_anchor=(-0.1, 1.07), fontsize=60, markerscale=2.5, frameon=False, framealpha=0.9, edgecolor='black')

        # Add Zoomed Inset
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
        
        # Position: Bottom Right
        axins = ax.inset_axes([0.55, 0.08, 0.4, 0.4]) 
        
        # Plot data on inset
        for mode in ["MILLIO-p", "MILLIO-o"]:
            points = data[ds][mode]
            if not points: continue
            est = [p[0] for p in points]
            true_vals = [p[1] for p in points]
            axins.scatter(est, true_vals, color=colors[mode], marker=markers[mode], s=300, alpha=0.9, edgecolors='none') # Smaller markers for zoom
        
        # Add Reference Line to inset
        axins.plot([limit_min, limit_max], [limit_min, limit_max], 'k--', linewidth=2.0, alpha=0.6)
        
        # Determine Zoom Limits
        if ds in CUSTOM_ZOOM:
            zmin, zmax = CUSTOM_ZOOM[ds]
            axins.set_xlim(zmin, zmax)
            axins.set_ylim(zmin, zmax)
        elif all_est and all_true:
            # Fallback to dynamic P0-P10
            min_x, p10_x = np.percentile(all_est, [0, 10])
            min_y, p10_y = np.percentile(all_true, [0, 10])
            
            span_x = max(p10_x - min_x, 0.05)
            span_y = max(p10_y - min_y, 0.05)
            
            axins.set_xlim(min_x - span_x*0.1, p10_x + span_x*0.1)
            axins.set_ylim(min_y - span_y*0.1, p10_y + span_y*0.1)
            
        axins.tick_params(axis='both', labelsize=48)
        axins.grid(True, linestyle=':', alpha=0.5)
        
        # Connect inset lines
        # mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5") # Connect corners
        patch, c1, c2 = mark_inset(ax, axins, loc1=2, loc2=1, fc="none", ec="black", linewidth=2.0, linestyle="-")
        c1.set_visible(False)
        c2.set_visible(False)

        
        plt.subplots_adjust(left=0.210, bottom=0.18, right=0.99, top=0.99)
        # Save individual file
        safe_name = ds.replace(" ", "_").replace("-", "_")
        out_file = f"benchmark_charts/chart_eb_density_{safe_name}.pdf"
        plt.savefig(out_file, dpi=300)
        print(f"Generated chart: {out_file}")
        plt.close(fig)

if __name__ == "__main__":
    print("Parsing logs...")
    data = parse_log(LOG_FILE)
    print("Generating charts...")
    plot_density(data)
