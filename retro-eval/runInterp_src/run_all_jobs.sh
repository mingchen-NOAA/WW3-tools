#!/bin/bash
set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

# Directory containing all your run_*.sh scripts
SCRIPT_DIR="/work2/noaa/marine/ming.chen/GFS_Retro_Data/data/jobinterp/GFSv16"

# Maximum wait time per run_*.sh batch (40 minutes = 2400 seconds)
MAX_WAIT_SECONDS=2400

# Log file with timestamp
LOG_DIR="${SCRIPT_DIR}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/run_all_sequentially_${TIMESTAMP}.log"

# =============================================================================
# Setup logging: everything goes to both terminal and log file
# =============================================================================

echo "Starting master script at $(date)" | tee "${LOG_FILE}"
echo "Log file: ${LOG_FILE}" | tee -a "${LOG_FILE}"
echo "Script directory: ${SCRIPT_DIR}" | tee -a "${LOG_FILE}"
echo "===========================================" | tee -a "${LOG_FILE}"

# Redirect all subsequent output to both terminal and log file
exec > >(tee -a "${LOG_FILE}") 2>&1

# =============================================================================
# Find all run_*.sh scripts
# =============================================================================

mapfile -t RUN_SCRIPTS < <(ls "${SCRIPT_DIR}"/run_*.sh 2>/dev/null | sort -V)

if [[ ${#RUN_SCRIPTS[@]} -eq 0 ]]; then
    echo "ERROR: No run_*.sh scripts found in ${SCRIPT_DIR}" >&2
    exit 1
fi

echo "FOUND ${#RUN_SCRIPTS[@]} run_*.sh scripts (in processing order):"
echo "------------------------------------------------------------"
printf '%5s  %s\n' "#" "Filename"
printf '%5s  %s\n' "-----" "--------------------------------------------------"
for i in "${!RUN_SCRIPTS[@]}"; do
    script_name=$(basename "${RUN_SCRIPTS[$i]}")
    printf '%5d  %s\n' $((i+1)) "$script_name"
done
echo "------------------------------------------------------------"
echo "Total: ${#RUN_SCRIPTS[@]} scripts"
echo
echo "Starting sequential execution..."
echo

# =============================================================================
# Main loop: process each run_*.sh one by one
# =============================================================================

for script in "${RUN_SCRIPTS[@]}"; do
    script_name=$(basename "$script")

    echo "=================================================="
    echo "Starting $script_name at $(date)"
    echo "=================================================="

    # Run the script and capture submitted SLURM job IDs
    job_ids=()
    while read -r line; do
        if [[ "$line" =~ Submitted\ batch\ job\ ([0-9]+) ]]; then
            job_ids+=("${BASH_REMATCH[1]}")
        fi
    done < <(cd "${SCRIPT_DIR}" && bash "$script")

    if [[ ${#job_ids[@]} -eq 0 ]]; then
        echo "Warning: No SLURM jobs detected from $script_name (possibly failed or no submissions)."
        echo "Pausing 30 seconds before continuing..."
        sleep 30
        continue
    fi

    echo "Submitted ${#job_ids[@]} jobs: ${job_ids[*]}"
    echo "Waiting for completion (max $((MAX_WAIT_SECONDS/60)) minutes)..."

    start_time=$(date +%s)
    while true; do
        # Count remaining PENDING or RUNNING jobs from this batch
        remaining=$(squeue -h -j "$(IFS=,; echo "${job_ids[*]}")" --states=PENDING,RUNNING 2>/dev/null | wc -l || echo 0)

        if [[ $remaining -eq 0 ]]; then
            echo "All jobs from $script_name completed at $(date)"
            break
        fi

        # Timeout check
        elapsed=$(( $(date +%s) - start_time ))
        if [[ $elapsed -ge $MAX_WAIT_SECONDS ]]; then
            echo "TIMEOUT REACHED ($((MAX_WAIT_SECONDS/60)) minutes). Moving to next script."
            echo "Still running/pending: $remaining jobs"
            squeue -h -j "$(IFS=,; echo "${job_ids[*]}")" -o "%i %j %T %R" 2>/dev/null || echo "No jobs visible"
            break
        fi

        sleep 30
    done

    echo "Proceeding to next script..."
    echo
done

# =============================================================================
# Completion
# =============================================================================

echo "=================================================="
echo "ALL ${#RUN_SCRIPTS[@]} run_*.sh scripts have been processed!"
echo "Master script finished at $(date)"
echo "Log saved to: ${LOG_FILE}"
echo "=================================================="
