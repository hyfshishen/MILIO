
import os
import subprocess
import glob

# Configuration
ZFP_EXE = "/u/bzhang28/zfp/build/bin/zfp"
OUTPUT_REPORT = "benchmark_cuzfp_report.md"
CSV_REPORT = "benchmark_cuzfp_all.csv"

# Datasets (Same as fixratio benchmark)
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

# Target Rates for R=4, 6, 8 (bits/value)
# Float32 = 32 bits.
# Ratio 4:  Rate = 32/4 = 8
# Ratio 6:  Rate = 32/6 = 5.333
# Ratio 8:  Rate = 32/8 = 4
TARGET_RATES = [8.0, 5.3333, 4.0] 
# Mapping for report
RATIO_MAP = {8.0: 4, 5.3333: 6, 4.0: 8}

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

def run_benchmark():
    script_content = "#!/bin/bash\n"
    
    datasets_expanded = {}
    for ds_name, config in DATASET_CONFIG.items():
        datasets_expanded[ds_name] = find_files(config["path"], config["pattern"])

    count = 0
    for ds_name, files in datasets_expanded.items():
        if not files: continue
        
        # Configure dimensions flags
        dim_flags = "-1 <SIZE>" # default 1D placehoder if needed, but zfp handles 1D via file size if unspecified? No, needs -1 <Nx>.
        
        dims = DATASET_CONFIG[ds_name]["dims"]
        
        for filepath in files:
            basename = os.path.basename(filepath)
            
            # Determine flags based on dims
            curr_dim_flags = ""
            if dims:
                # 3D: -3 <nx> <ny> <nz> (Order: X Y Z? Help says: -3 <nx> <ny> <nz> : dimensions for 3D array a[nz][ny][nx] -> Slowest to fastest?)
                # Wait. C-order: a[nz][ny][nx].
                # User's dims: {"x": 3600, "y": 1800, "z": 26}. 
                # If these are X,Y,Z logical, then in C buffer they are typically Z, Y, X (Z slow, X fast).
                # So -3 3600 1800 26.
                curr_dim_flags = f"-3 {dims['x']} {dims['y']} {dims['z']}"
            else:
                # 1D fallback
                # Need file size
                try:
                    fsize = os.path.getsize(filepath)
                    nele = fsize // 4
                    curr_dim_flags = f"-1 {nele}"
                except:
                    continue

            for rate in TARGET_RATES:
                count += 1
                ratio_label = RATIO_MAP.get(rate, 0)
                if ratio_label == 6: rate_str = "5.3333"
                else: rate_str = str(int(rate))
                
                script_content += f"echo 'BENCH_START:{ds_name}:{basename}:{ratio_label}'\n"
                # zfp -x cuda -i <in> -f -3 ... -r <rate> -s
                script_content += f"{ZFP_EXE} -x cuda -i {filepath} -f {curr_dim_flags} -r {rate_str} -s || true\n"
                script_content += "sleep 0.1\n"

    print(f"Generated {count} commands.")
    with open("run_cuzfp_all.sh", "w") as f:
        f.write(script_content)
    
    print("Submitting job...")
    cmd = [
        "srun", "--account=bfrq-delta-gpu", "--partition=gpuA100x4", 
        "--mem=64G", "--time=02:00:00", "--gpus=1",
        "bash", "run_cuzfp_all.sh"
    ]
    
    with open("benchmark_cuzfp_output.log", "w") as outfile:
        subprocess.run(cmd, stdout=outfile, stderr=subprocess.STDOUT)
    
    print("Job complete. Parsing...")
    # Add parsing logic if needed later, or just cat log
    
if __name__ == "__main__":
    run_benchmark()
