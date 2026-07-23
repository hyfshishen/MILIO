
import os
import subprocess
import glob

# Configuration
# Use the CLI tools that include verification (PSNR)
CLI_1D = "./build/examples/bin/cuszp_fixed_ratio_cli"
CLI_3D = "./build/examples/bin/cuszp_fixed_ratio_cli_3d"
ZFP_EXE = "/u/bzhang28/zfp/build/bin/zfp"

OUTPUT_SCRIPT = "run_rd_bench.sh"
OUTPUT_LOG = "benchmark_rd_comparison.log"

DATASETS = {
    # 3D Datasets
    "CESM": {
        "path": "/scratch/bfrq/bzhang28/SDRBENCH-CESM-ATM-26x1800x3600/CLDICE_1_26_1800_3600.f32",
        "dims": [3600, 1800, 26], # x, y, z
        "is_3d": True
    },
    "NYX": {
        "path": "/scratch/bfrq/bzhang28/SDRBENCH-EXASKY-NYX-512x512x512/dark_matter_density.f32",
        "dims": [512, 512, 512],
        "is_3d": True
    },
    "SYNTHESIS": {
        "path": "/scratch/bfrq/bzhang28/synthetic_truss_with_five_defects_1200x1200x1200_float32.raw",
        "dims": [1200, 1200, 1200],
        "is_3d": True
    },
    # 1D or others
    "QMCPACK": {
        "path": "/scratch/bfrq/bzhang28/dataset/115x69x69x288/einspline_115_69_69_288.f32",
        "dims": None, 
        "is_3d": False
    },
    "RTM": {
        "path": "/scratch/bfrq/bzhang28/pressure_3000",
        "dims": None,
        "is_3d": False
    }
}

RATIOS = [2, 3, 4, 5, 6, 7, 8, 10, 16, 32]

def get_num_elements(filepath):
    try:
        size = os.path.getsize(filepath)
        return size // 4 # float32
    except:
        return 0

def run_gen():
    script_content = "#!/bin/bash\n"
    count = 0
    
    for ds_name, config in DATASETS.items():
        filepath = config["path"]
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found for {ds_name}")
            continue
            
        nele = get_num_elements(filepath)
        
        # Determine Command for MILIO-o
        # Use sampling rate 100
        
        for ratio in RATIOS:
            count += 1
            
            # --- MILIO-o ---
            # Command Construction
            if config["is_3d"]:
                # CLI_3D -i <in> -x <x> -y <y> -z <z> -r <ratio> -m outlier -s 100
                dx, dy, dz = config["dims"]
                cmd_cuszp = f"{CLI_3D} -i {filepath} -x {dx} -y {dy} -z {dz} -r {ratio} -m outlier -s 100"
            else:
                # CLI_1D -i <in> -n <nele> -r <ratio> -m outlier -s 100
                cmd_cuszp = f"{CLI_1D} -i {filepath} -n {nele} -r {ratio} -m outlier -s 100"
            
            script_content += f"echo 'BENCH_START:{ds_name}:MILIO-o:{ratio}'\n"
            script_content += f"{cmd_cuszp} || true\n"
            script_content += "sleep 0.1\n"
            
            # --- cuZFP ---
            # Rate = 32 / Ratio
            rate = 32.0 / ratio
            # dim flags for zfp
            if config["is_3d"]:
                dx, dy, dz = config["dims"]
                # ZFP uses -3 <nx> <ny> <nz>. Order usually X Y Z (fastest first?) 
                # or Z Y X. ZFP CLI usually expects nx ny nz.
                # Let's stick to standard nx ny nz.
                dims_flag_zfp = f"-3 {dx} {dy} {dz}"
            else:
                dims_flag_zfp = f"-1 {nele}"
                
            cmd_zfp = f"{ZFP_EXE} -x cuda -i {filepath} -f {dims_flag_zfp} -r {rate} -s"
            
            script_content += f"echo 'BENCH_START:{ds_name}:cuZFP:{ratio}'\n"
            script_content += f"{cmd_zfp} || true\n"
            script_content += "sleep 0.1\n"

    print(f"Generated {count * 2} commands.")
    with open(OUTPUT_SCRIPT, "w") as f:
        f.write(script_content)

    print("Submitting job...")
    # Increase time/mem just in case
    cmd = [
        "srun", "--account=bfrq-delta-gpu", "--partition=gpuA100x4", 
        "--mem=64G", "--time=02:00:00", "--gpus=1",
        "bash", OUTPUT_SCRIPT
    ]
    
    with open(OUTPUT_LOG, "w") as outfile:
        # We want to capture both stdout and stderr
        subprocess.run(cmd, stdout=outfile, stderr=subprocess.STDOUT)
    
    print(f"Benchmark complete. Log: {OUTPUT_LOG}")

if __name__ == "__main__":
    run_gen()
