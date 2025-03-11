import datetime as dt
from dateutil.relativedelta import relativedelta
import os

rootdir = os.path.join('/work2/noaa/marine/jmeixner/processsatdata', 'jobsubs')

startdate = dt.datetime(2019,12,1)
enddate = dt.datetime(2023,12,31)

nowdate = startdate
dates1 = []
dates2 = []

while nowdate <= enddate:
    dates1.append(nowdate.strftime('%Y%m%d'))
    dates2.append((nowdate + dt.timedelta(days=15)).strftime('%Y%m%d'))
    dates1.append((nowdate + dt.timedelta(days=15)).strftime('%Y%m%d'))
    nowdate = nowdate + relativedelta(months=+1)
    dates2.append(nowdate.strftime('%Y%m%d'))
    
    
print(dates1)
print(dates2)
satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT
for i in range(len(dates1)):
    for j in range(len(satelites)): 
        outfile = os.path.join(rootdir, f"job_{satelites[j]}_{dates1[i]}.sh")
        with open(outfile, 'w') as f:
            f.write('#!/bin/bash\n')
            sbatch = f"""#SBATCH --nodes=1
#SBATCH -q batch
#SBATCH -t 08:00:00
#SBATCH -A marine-cpu
#SBATCH -J procsat_{satelites[j]}_{dates1[i]} 
#SBATCH -o run_{satelites[j]}_{dates1[i]}.o%j
#SBATCH --partition=orion
#SBATCH --exclusive


module use /work2/noaa/marine/jmeixner/general/modulefiles
module load ww3tools

ThisDir=/work2/noaa/marine/jmeixner/processsatdata
PathToWW3TOOLS=/work2/noaa/marine/jmeixner/processsatdata/ww3-tools/ww3tools

SAT={satelites[j]}

IDATE={dates1[i]}00
EDATE={dates2[i]}00

"""
            f.write(sbatch)
            f.write('YAMLFILE=${ThisDir}/configs/${SAT}.yaml \n')
            f.write('python ${PathToWW3TOOLS}/ProcSat_Altimeter.py --satelite ${SAT} --initdate ${IDATE} --enddate ${EDATE} --timestep 1.0 --yaml ${YAMLFILE} \n')
