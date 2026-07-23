
import os
import subprocess
import re
import statistics

# Configuration

import os
import subprocess
import re
import statistics

# Configuration
# Updated to use the new CLI tools that report strict profiling times
CLI_1D = "./build/examples/bin/cuszp_fixed_ratio_cli"
CLI_3D = "./build/examples/bin/cuszp_fixed_ratio_cli_3d"
OUTPUT_REPORT = "benchmark_fixratio_all_report.md"
SAMPLING_RATE = 1000
TRIALS = 1

# Dataset definitions with dimensions
# 1D datasets can omit dims or set y=1, z=1
DATASET_CONFIG = {
    "CESM": {
        "path": "/scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600",
        "pattern": ".f32",
        "dims": {"x": 3600, "y": 1800, "z": 26}
    },
    "NYX": {
        "path": "/scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512",
        "pattern": ".f32",
        "dims": {"x": 512, "y": 512, "z": 512}
    },
    "HACC": {
        "path": "/scratch/bfrq/bzhang28/1billionparticles_onesnapshot",
        "pattern": ".f32", 
        "dims": None # 1D
    },
    "EXAFEL": {
        "path": "/scratch/bfrq/bzhang28/SDRBENCH-EXAFEL-130x1480x1552",
        "pattern": ".f32",
        "dims": {"z": 130, "y": 1480, "x": 1552}
    },
    "QMCPACK": {
        "path": "/scratch/bfrq/bzhang28/dataset",
        "pattern": ".f32",
        "dims": None 
    },
    "RTM": {
        "path": "/scratch/bfrq/bzhang28",
        "pattern": "pressure_",
        "dims": None 
    },
    "SYNTHESIS": {
        "path": "/scratch/bfrq/bzhang28",
        "pattern": "synthetic",
        "dims": {"z": 1200, "y": 1200, "x": 1200}
    },
    "EXAALT": {
        "path": "/scratch/bfrq/bzhang28/SDRBENCH-exaalt-copper",
        "pattern": ".dat",
        "dims": None 
    },
    "SCALE": {
        "path": "/scratch/bfrq/bzhang28/SDRBENCH-SCALE_98x1200x1200",
        "pattern": ".f32",
        "dims": {"z": 98, "y": 1200, "x": 1200}
    }
}

# Helper to find files
def find_files(directory, pattern):
    files = []
    if not os.path.exists(directory):
        return []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(pattern) or pattern in filename:
                files.append(os.path.join(root, filename))
    files.sort()
    return files

# Populate dynamic lists
DATASETS = {}
for ds_name, config in DATASET_CONFIG.items():
    DATASETS[ds_name] = find_files(config["path"], config["pattern"])

MODES = ["outlier", "plain"] # Focus on outlier mode as it's the main feature
RATIOS = [4.0, 6.0, 8.0]

def parse_logs(logfile):
    results = {} 
    
    current_ds = None
    current_filename = None
    current_mode = None
    current_ratio = None
    current_data = None
    
    if not os.path.exists(logfile):
        print(f"Error: Log file {logfile} not found!", flush=True)
        return {}

    with open(logfile, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("BENCH_START"):
                parts = line.split(":")
                # BENCH_START:Dataset:Filename:Mode:Ratio
                ds_name = parts[1]
                filename = parts[2]
                mode = parts[3]
                ratio = float(parts[4])
                
                if ds_name not in results: results[ds_name] = {}
                if filename not in results[ds_name]: results[ds_name][filename] = {}
                if mode not in results[ds_name][filename]: results[ds_name][filename][mode] = {}
                if ratio not in results[ds_name][filename][mode]: 
                    results[ds_name][filename][mode][ratio] = {
                         "perf_total": [], "perf_compress": [], "perf_decompress": [], 
                         "psnr": [], "ratio": [], "compliance": [],
                         "perf_profile": [] 
                    }
                current_data = results[ds_name][filename][mode][ratio]

            elif current_data is not None:
                # Updated Parsing for New CLI Tools
                # "Total (Prof+Comp) Thrpt: %.2f GB/s"
                # "Compression Throughput:  %.2f GB/s"
                # "Profiling Throughput:    %.2f GB/s"
                # "Decompression Throughput: %.2f GB/s"
                # "Achieved Ratio: %.2f"
                
                # We also support legacy " total end-to-end speed: %f GB/s" just in case mixed logs

                # Total
                m = re.search(r"Total \(Prof\+Comp\) Thrpt:\s+([\d\.]+)\s+GB/s", line)
                if m: current_data["perf_total"].append(float(m.group(1)))
                m2 = re.search(r"total end-to-end speed:\s+([\d\.]+)\s+GB/s", line) # legacy
                if not m and m2: current_data["perf_total"].append(float(m2.group(1)))

                # Compression
                m = re.search(r"Compression Throughput:\s+([\d\.]+)\s+GB/s", line)
                if m: current_data["perf_compress"].append(float(m.group(1)))
                m2 = re.search(r"compression end-to-end speed:\s+([\d\.]+)\s+GB/s", line) # legacy
                if not m and m2: current_data["perf_compress"].append(float(m2.group(1)))
                
                # Profiling
                m = re.search(r"Profiling Throughput:\s+([\d\.]+)\s+GB/s", line)
                if m: current_data["perf_profile"].append(float(m.group(1)))
                m2 = re.search(r"profile end-to-end speed:\s+([\d\.]+)\s+GB/s", line) # legacy
                if not m and m2: current_data["perf_profile"].append(float(m2.group(1)))

                # Decompression
                m = re.search(r"Decompression Throughput:\s+([\d\.]+)\s+GB/s", line)
                if m: current_data["perf_decompress"].append(float(m.group(1)))
                m2 = re.search(r"decompression end-to-end speed:\s+([\d\.]+)\s+GB/s", line) # legacy
                if not m and m2: current_data["perf_decompress"].append(float(m2.group(1)))
                
                # Ratio
                # "Achieved Ratio: %.2f" or "ratio=%.3f"
                m = re.search(r"Achieved Ratio:\s+([\d\.]+)", line)
                if m: current_data["ratio"].append(float(m.group(1)))
                m2 = re.search(r"ratio=([\d\.]+)", line) # legacy
                if not m and m2: current_data["ratio"].append(float(m2.group(1)))

    return results

def run_benchmark():
    print("Generating benchmark script...", flush=True)
    script_content = "#!/bin/bash\n"
    
    count = 0
    for ds_name, files in DATASETS.items():
        if not files: continue
        print(f"for {ds_name}, found {len(files)} files.", flush=True)
        
        # Check if 3D
        is_3d = False
        dims = None
        if ds_name in DATASET_CONFIG and DATASET_CONFIG[ds_name]["dims"]:
             dims = DATASET_CONFIG[ds_name]["dims"]
             # Heuristic: if x, y, z all present and > 1
             if dims.get("x",0) > 1 and dims.get("y",0) > 1 and dims.get("z",0) > 1:
                 is_3d = True

        for filepath in files:
            basename = os.path.basename(filepath)
            
            for mode in MODES:
                for ratio in RATIOS:
                    for i in range(TRIALS):
                        count += 1
                        script_content += f"echo 'BENCH_START:{ds_name}:{basename}:{mode}:{ratio}'\n"
                        
                        # Select Binary
                        if is_3d:
                            # 3D CLI: -i <in> -x <x> -y <y> -z <z> -r <ratio> -m <mode> -s <sample>
                            cmd = f"{CLI_3D} -i {filepath} -x {dims['x']} -y {dims['y']} -z {dims['z']} -r {ratio} -m {mode} -s {SAMPLING_RATE}"
                        else:
                            # 1D CLI: -i <in> -n <nele> -r <ratio> -m <mode> -s <sample>
                            # Need to calculate nele or pass file size?
                            # 1D CLI uses -n <num_elements>
                            # We can get size from os.path.getsize(filepath) // 4
                            try:
                                sz = os.path.getsize(filepath) // 4
                                cmd = f"{CLI_1D} -i {filepath} -n {sz} -r {ratio} -m {mode} -s {SAMPLING_RATE}"
                            except:
                                cmd = f"echo 'Error getting size for {filepath}'"
                        
                        script_content += f"{cmd} || true\n"
                        script_content += "sleep 0.1\n"
    
    print(f"Generated {count} commands.", flush=True)
    with open("run_fixratio_all.sh", "w") as f:
        f.write(script_content)
    
    print("Submitting job...", flush=True)
    cmd = [
        "srun", "--account=bfrq-delta-gpu", "--partition=gpuA100x4", 
        "--mem=64G", "--time=02:00:00", "--gpus=1",
        "bash", "run_fixratio_all.sh"
    ]
    
    with open("benchmark_fixratio_warmup_output.log", "w") as outfile:
        # We want to capture both stdout and stderr
        subprocess.run(cmd, stdout=outfile, stderr=subprocess.STDOUT)
    
    print("Job complete. Parsing results...", flush=True)
    results = parse_logs("benchmark_fixratio_warmup_output.log")
    
    with open(OUTPUT_REPORT, "w") as f:
        f.write("# cuSZp_fixratio Benchmark Report\n\n")
        
        for ds_name in results:
            f.write(f"\n## Dataset: {ds_name}\n")
            for mode in MODES:
                f.write(f"\n### Mode: {mode.capitalize()}\n")
                f.write("| File | Ratio | Comp Speed (GB/s) | Achieved Ratio | Prof Speed |\n")
                f.write("|---|---|---|---|---|\n")
                
                for filename in results[ds_name]:
                    if mode not in results[ds_name][filename]: continue
                    
                    for ratio in RATIOS:
                        if ratio not in results[ds_name][filename][mode]: continue
                        
                        data = results[ds_name][filename][mode][ratio]
                        if not data["perf_total"]: continue
                        
                        avg_total = statistics.mean(data["perf_total"])
                        avg_ratio = statistics.mean(data["ratio"]) if data["ratio"] else 0
                        avg_prof = statistics.mean(data["perf_profile"]) if data["perf_profile"] else 0
                        
                        f.write(f"| {filename} | {ratio} | {avg_total:.2f} | {avg_ratio:.2f} | {avg_prof:.2f} |\n")

    print(f"Report generated: {OUTPUT_REPORT}", flush=True)

if __name__ == "__main__":
    run_benchmark()
