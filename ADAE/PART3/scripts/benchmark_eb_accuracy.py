
import os
import subprocess
import re

# Configuration
BINARY_PATH = "./build/examples/bin/cuSZp_all_eb_check"
OUTPUT_LOG = "benchmark_eb_accuracy_output.log"
SAMPLING_RATE = 500 # Changed from 1000

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
        "dims": None 
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
        "prefer": "pressure_3000",           # pin the exact field (several snapshots exist)
        "dims": None
    },
    "SYNTHESIS": {
        "path": "/scratch/bfrq/bzhang28",
        "pattern": "synthetic",
        "prefer": "synthetic_truss_with_five_defects_1200x1200x1200_float32.raw",
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

DATASETS = {}

# Non-data files that must never be treated as an input field, even if their
# name happens to match a dataset pattern (e.g. a figure named
# "psnr_bitrate_pressure_3000.pdf" would otherwise match RTM's "pressure_").
_NON_DATA_EXT = (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".gif",
                 ".log", ".md", ".txt", ".sh", ".py", ".tex",
                 ".json", ".csv", ".zip", ".gz", ".tar", ".bak")

def find_files(directory, pattern):
    files = []
    if not os.path.exists(directory):
        return []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(_NON_DATA_EXT):
                continue                       # skip figures/logs/archives, etc.
            if filename.endswith(pattern) or pattern in filename:
                files.append(os.path.join(root, filename))
    files.sort()
    return files

for ds_name, config in DATASET_CONFIG.items():
    DATASETS[ds_name] = find_files(config["path"], config["pattern"])

MODES = ["outlier", "plain"]

def run_benchmark():
    print("Generating benchmark script...", flush=True)
    script_content = "#!/bin/bash\n"
    
    count = 0
    for ds_name, files in DATASETS.items():
        if not files: 
            print(f"No files found for {ds_name}", flush=True)
            continue
        
        # Pick ONE file for the accuracy check. If the dataset pins an exact
        # basename (its search directory may hold several matches), use it;
        # otherwise fall back to the first match.
        prefer = DATASET_CONFIG.get(ds_name, {}).get("prefer")
        filepath = files[0]
        if prefer:
            exact = [f for f in files if os.path.basename(f) == prefer]
            if exact:
                filepath = exact[0]
            else:
                print(f"WARNING: preferred file '{prefer}' not found for "
                      f"{ds_name}; using {os.path.basename(filepath)}", flush=True)
        basename = os.path.basename(filepath)
        
        for mode in MODES:
            count += 1
            script_content += f"echo 'BENCH_START:{ds_name}:{basename}:{mode}'\n"
            
            cmd = f"{BINARY_PATH} -i {filepath} -m {mode} -S {SAMPLING_RATE}"
            
            if ds_name in DATASET_CONFIG and DATASET_CONFIG[ds_name]["dims"]:
                d = DATASET_CONFIG[ds_name]["dims"]
                cmd += f" -x {d['x']} -y {d['y']} -z {d['z']}"
                
                # Check for RTM/EXAALT custom setting
                # Or just use S=1000 default unless specified.
                # User asked for RTM ratio 1500 before, should I use it here?
                # User said "please re-run RTM with 1500".
                # For this new figure, likely consistent params are best.
                # I'll stick to default 1000 for now or respect user's last intent globally?
                # Let's keep 1000 default, it's safer for comparability.
            
            script_content += f"{cmd} || true\n"
            script_content += "sleep 0.1\n"
    
    print(f"Generated {count} commands.", flush=True)
    if count == 0:
        print("Nothing to run.", flush=True)
        return

    with open("run_eb_accuracy.sh", "w") as f:
        f.write(script_content)
    
    print("Submitting job...", flush=True)
    cmd = [
        "srun", "--account=bfrq-delta-gpu", "--partition=gpuA100x4", 
        "--mem=64G", "--time=02:00:00", "--gpus=1",
        "bash", "run_eb_accuracy.sh"
    ]
    
    with open(OUTPUT_LOG, "w") as outfile:
        subprocess.run(cmd, stdout=outfile, stderr=subprocess.STDOUT)
    
    print(f"Job complete. Output saved to {OUTPUT_LOG}", flush=True)

if __name__ == "__main__":
    run_benchmark()
