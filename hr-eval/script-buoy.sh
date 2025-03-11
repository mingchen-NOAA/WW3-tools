#!/bin/sh --login
#SBATCH -q debug
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:30:00
#SBATCH --partition=hera
#SBATCH --account=marine-cpu
#SBATCH --job-name=process_data
#SBATCH --output=zlogfile-buoy-multi19.out


# Load necessary modules
module use /scratch1/NCEPDEV/climate/Jessica.Meixner/general/modulefiles-rocky16
module load ww3tools


# Define variables
input_gz_file="multi_1.t11z.spec_tar.gz"
output_directory="./"
buoy_path="/scratch2/NCEPDEV/marine/Matthew.Masarik/dat/buoys/NDBC/ncformat/wparam"

# Process data for each date
python3 modelBuoy_collocation.py unzip "$input_gz_file" "$output_directory" "$buoy_path"


