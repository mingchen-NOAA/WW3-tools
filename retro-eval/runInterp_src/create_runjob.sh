#!/bin/bash
#cd /work2/noaa/marine/ming.chen/GFS_Retro_Data/data/jobinterp/GFSv16
cd /work2/noaa/marine/ming.chen/GFS_Retro_Data/data/jobinterp/retrov17_01

BATCH=20
i=0
runid=1

rm -f run_*.sh

#for jc in job_GFSv16_global.0p25_*.sh; do
for jc in job_retrov17_01_global.0p25_*.sh; do
  if [ $i -eq 0 ]; then
    runfile="run_${runid}.sh"
    echo "#!/bin/bash" > "$runfile"
    echo "set -euo pipefail" >> "$runfile"
    echo "set -x" >> "$runfile"
  fi

  echo "sbatch $jc" >> "$runfile"

  i=$((i+1))
  if [ $i -eq $BATCH ]; then
    chmod +x "$runfile"
    runid=$((runid+1))
    i=0
  fi
done

# finalize last file if partial
if [ $i -ne 0 ]; then
  chmod +x "$runfile"
fi
