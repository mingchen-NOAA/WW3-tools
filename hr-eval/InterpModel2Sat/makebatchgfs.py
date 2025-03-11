import datetime as dt
from dateutil.relativedelta import relativedelta
import os

rootdir = os.path.join('/work2/noaa/marine/jmeixner/processsatdata', 'jobinterp')

season=['summer', 'hurricane']
satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT
#model=['multi1', 'GFSv16', 'HR1', 'HR2', 'HR3a']
model='GFSv16'

for k in range(len(season)):
   if season[k] == "winter":
       startdate = dt.datetime(2019,12,3)
       enddate = dt.datetime(2020,2,26)
       datestride = 3 
   elif season[k] == "summer":
       startdate = dt.datetime(2020,6,1)
       #enddate = dt.datetime(2020,8,30) #nooverlap needed 
       enddate = dt.datetime(2020,7,19)
       datestride = 3
   elif season[k] == "hurricane":
       startdate = dt.datetime(2020,7,20)
       enddate = dt.datetime(2020,11,20)
       datestride = 1 

   nowdate = startdate
   dates1 = []
    



   while nowdate <= enddate:
       dates1.append(nowdate.strftime('%Y%m%d%H'))
       #nowdate = (nowdate + dt.timedelta(days=datestride)).strftime('%Y%m%d') 
       nowdate = nowdate + dt.timedelta(days=datestride)
   print(dates1)
   outfile = os.path.join(rootdir, f"submit_{model}_{season[k]}.sh")
   with open(outfile, 'w') as f:
     for i in range(len(dates1)):
                sbatch = f"""sbatch job_{model}_{dates1[i]}.sh
"""

                f.write(sbatch)


