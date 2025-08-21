import datetime as dt
from dateutil.relativedelta import relativedelta
import os

rootdir = os.path.join('/scratch4/NCEPDEV/marine/Ming.Chen/wave_eval/processsatdata_ursa', 'jobinterp')

season=['winter']
satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT
model='Retrotests'

startdate = dt.datetime(2024,11,15,12)
enddate = dt.datetime(2025,1,15,12)
datestride = 3

nowdate = startdate
dates1 = []
while nowdate <= enddate:
    dates1.append(nowdate.strftime('%Y%m%d%H'))
    nowdate = nowdate + dt.timedelta(days=datestride)

for i in range(len(dates1)):
         outfile = os.path.join(rootdir, f"job_{model}_p25_{dates1[i]}.sh")
         with open(outfile, 'w') as f:
             f.write('#!/bin/bash\n')
             sbatch = f"""#SBATCH --nodes=1
#SBATCH -q batch
#SBATCH -t 08:00:00
#SBATCH -A marine-cpu
#SBATCH -J procsat_{model}_p16_{dates1[i]}
#SBATCH -o run_{model}_p16_{dates1[i]}.o%j
#SBATCH --exclusive


module use module use /scratch3/NCEPDEV/climate/Jessica.Meixner/general/modulefiles
module load ww3tools

ThisDir=/scratch4/NCEPDEV/marine/Ming.Chen/wave_eval/HR_eval/hr-eval/InterpModel2Sat
PathToWW3TOOLS=/scratch4/NCEPDEV/marine/Ming.Chen/wave_eval/HR-eval/ww3tools

set -x

SEASON={season[k]}
MODEL={model}
CDATE={dates1[i]}
OUTDIR=/scratch4/NCEPDEV/marine/Ming.Chen/wave_eval/processsatdata_ursa/outinterp/{model}

"""

                f.write(sbatch)
                f.write('DATE=${CDATE:0:8} \n')
                f.write('TZ=${CDATE:8:2} \n')
                f.write('MODEL_DATA_DIR="/scratch4/NCEPDEV/marine/Ming.Chen/wave_eval/hpss_gfs/output/${CDATE}/gfs.${DATE}/${TZ}/products/wave/gridded" \n')
                for j in range(len(satelites)):
                        satvalue = f"""

SAT={satelites[j]}

"""

                        f.write(satvalue)

                        f.write('SATELLITE_FILE=/scratch4/NCEPDEV/marine/Ming.Chen/wave_eval/processsatdata_ursa/out/merged/Altimeter_${SAT}_${SEASON}.nc \n')
                        grids=['global.0p25']
                        for g in range(len(grids)):
                           if grids[g] == 'global.0p25':
                               f.write("MODEL_DATA_PATTERN='gfswave.t12z.global.0p25.f*.grib2'\n")
                               f.write('OUTPUT_FILE="${MODEL}_global.0p25_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'global.0p16':
                               f.write("MODEL_DATA_PATTERN='gfswave.t00z.global.0p16.f*.grib2'\n")
                               f.write('OUTPUT_FILE="${MODEL}_global.0p16_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'arctic.9km':
                               f.write("MODEL_DATA_PATTERN='gfswave.t00z.arctic.9km.f*.grib2'\n")
                               f.write('OUTPUT_FILE="${MODEL}_arctic.9km_${CDATE}_${SAT}.nc" \n')
                           f.write('python ${PathToWW3TOOLS}/ProcSat_interpolation.py -t grib2 -d $MODEL_DATA_DIR -p $MODEL_DATA_PATTERN -s $SATELLITE_FILE -o $OUTDIR -f $OUTPUT_FILE -m ${MODEL} \n')
