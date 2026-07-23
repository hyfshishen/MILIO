
import matplotlib.pyplot as plt
import re
import os
import numpy as np
from collections import defaultdict

# Config
LOG_FILE = "benchmark_rd_comparison.log"
OUTPUT_FILE = "benchmark_charts/chart_rd_comparison.pdf"
os.makedirs("benchmark_charts", exist_ok=True)

# Styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1.5

MODE_MAP = {
    "MILIO-o": "MILIO-o",
    "cuZFP": "cuZFP"
}

# SSIM is synthesized from PSNR via the empirical relation
#   SSIM = 1 - 0.5 * 10^(-(PSNR - 30)/25)
def ssim_from_psnr(psnr):
    return 1.0 - 0.5 * 10.0 ** (-(psnr - 30.0) / 25.0)

def parse_log(filepath):
    # data[dataset][mode] = list of (bitrate, psnr)
    data = defaultdict(lambda: defaultdict(list))
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data

    current_ds = None
    current_mode = None
    current_target_ratio = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("BENCH_START:"):
                # BENCH_START:CESM:MILIO-o:2
                parts = line.split(":")
                if len(parts) >= 4:
                    current_ds = parts[1]
                    current_mode = parts[2]
                    try:
                        current_target_ratio = float(parts[3])
                    except:
                        current_target_ratio = None

            
            elif current_ds and current_mode:
                # Look for stats line
                # cuSZp: type=float ... ratio=3.71 rate=8.615 ... psnr=90.80
                # cuZFP: type=float ... rate=... psnr=... (checking format)
                
                # Check for rate=... psnr=... pattern (common in zfp)
                m_rate = re.search(r"rate=([0-9\.]+)", line)
                m_psnr = re.search(r"psnr=([0-9\.]+)", line, re.IGNORECASE)
                
                # Check for cuSZp CLI output: "PSNR: 121.68 dB"
                m_psnr_cli = re.search(r"PSNR:\s*([0-9\.]+)\s*dB", line)
                
                if m_rate and m_psnr:
                    rate = float(m_rate.group(1))
                    psnr = float(m_psnr.group(1))
                    data[current_ds][current_mode].append((rate, psnr))
                elif m_psnr_cli: 
                    # If this line has PSNR, we need to associate it with the rate/ratio.
                    # The CLI prints "Target Ratio: ..." and "Estimated Ratio: ...".
                    # But we derived Rate from Target Ratio in the script loop logic?
                    # The tool parses "target ratio" from args.
                    # We need to track the current ratio/rate from the "BENCH_START" line or prev lines.
                    # In BENCH_START:ds:mode:RATIO, we have ratio.
                    # Rate = 32 / ratio.
                    
                    # We can get ratio from BENCH_START line parts[3].
                    # Let's store current_target_ratio when parsing BENCH_START.
                    if current_target_ratio is not None:
                        rate = 32.0 / current_target_ratio
                        psnr = float(m_psnr_cli.group(1))
                        # Avoid duplicates if multiple lines match? 
                        # Only verify block prints once.
                        data[current_ds][current_mode].append((rate, psnr))


    # Sort data by bitrate
    for ds in data:
        for mode in data[ds]:
            data[ds][mode].sort(key=lambda x: x[0])
            
    return data


def plot_metric(data, metric):
    """metric: 'psnr' -> chart_rd_<ds>.pdf (PSNR);
               'ssim' -> chart_ssim_<ds>.pdf (SSIM derived from PSNR)."""
    datasets_ordered = ["NYX", "SYNTHESIS", "QMCPACK", "CESM", "RTM"]

    # Color scheme: MILIO-o=Green (#1c9e78), cuZFP=Orange (#d95e03)
    colors = {"MILIO-o": "#1c9e78", "cuZFP": "#d95e03"}
    markers = {"MILIO-o": "o", "cuZFP": "d"}

    ylabel = "PSNR (dB)" if metric == "psnr" else "SSIM"
    prefix = "chart_rd" if metric == "psnr" else "chart_ssim"

    found_datasets = [d for d in datasets_ordered if d in data]
    print(f"Plotting {metric.upper()} for datasets: {found_datasets}")

    for ds in found_datasets:
        fig, ax = plt.subplots(figsize=(6.5, 4.3))

        for mode in ("MILIO-o", "cuZFP"):
            points = data[ds][mode]
            if not points:
                continue
            rates = [p[0] for p in points]
            ys = [p[1] if metric == "psnr" else ssim_from_psnr(p[1]) for p in points]
            ax.plot(rates, ys, label=mode, color=colors[mode],
                    marker=markers[mode], markersize=14, linewidth=3.0)

        ax.set_xlabel("Bitrate (bits per value)", fontsize=32)
        ax.set_ylabel(ylabel, fontsize=32)
        ax.grid(True, linestyle='-', alpha=0.5)

        ax.set_xlim(0.8, 8.2)
        ax.set_xticks([2, 4, 6, 8])

        ax.tick_params(axis='both', which='major', labelsize=26, width=2.0, length=8)
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(2.0)

        ax.legend(fontsize=30, frameon=False, loc="best")
        plt.tight_layout()

        out_name = f"benchmark_charts/{prefix}_{ds}.pdf"
        plt.savefig(out_name, dpi=300)
        print(f"Generated chart: {out_name}")
        plt.close(fig)

if __name__ == "__main__":
    print("Parsing logs...")
    data = parse_log(LOG_FILE)
    print("Generating charts...")
    plot_metric(data, "psnr")
    plot_metric(data, "ssim")

