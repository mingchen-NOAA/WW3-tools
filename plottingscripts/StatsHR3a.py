import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

import datetime as dt
from dateutil.relativedelta import relativedelta
import os


def main():

  rootdir = os.path.join('/work2/noaa/marine/jmeixner/processsatdata', 'jobinterp')

  season=['winter', 'summer', 'hurricane']
  satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT
  #model=['multi1', 'GFSv16', 'HR1', 'HR2', 'HR3']
  model='HR3a'
  season=['hurricane']
  satelites=['JASON3']
  for k in range(len(season)):
    if season[k] == "winter":
       startdate = dt.datetime(2019,12,3)
       enddate = dt.datetime(2020,2,26)
       datestride = 3 
       endday = 16
    elif season[k] == "summer":
       startdate = dt.datetime(2020,6,1)
       enddate = dt.datetime(2020,8,30)
       datestride = 3
       endday = 16
    elif season[k] == "hurricane":
       startdate = dt.datetime(2020,7,20)
       enddate = dt.datetime(2020,11,20)
       datestride = 1
       endday = 7

    nowdate = startdate
    dates1 = []
    while nowdate <= enddate:
       dates1.append(nowdate.strftime('%Y%m%d%H'))
       #nowdate = (nowdate + dt.timedelta(days=datestride)).strftime('%Y%m%d') 
       nowdate = nowdate + dt.timedelta(days=datestride)

    for j in range(len(satelites)): 
      time = []; lats = []; lons = []; fhrs = []
      obs_hs = []; obs_wnd = []; obscal_hs =[]; obscal_wnd = []
      model_hs = []; model_wnd = []
      rmse_wnd_out = []; rmse_hs_out = [];
      bias_wnd_out = []; bias_hs_out = [];
      day_out = []; count_out = [];
      for i in range(len(dates1)):
         OUTDIR=f"/work2/noaa/marine/jmeixner/processsatdata/outinterp/{model}" 
         OUTPUT_FILE=f"{model}_global.0p25_{season[k]}_{dates1[i]}_{satelites[j]}.nc"
         datapath = OUTDIR + "/" + OUTPUT_FILE
         datanc  = nc.Dataset(datapath)

         #time = np.append(time, np.array(datanc.variables['time'][:]) 
         #lats = np.append(lats, np.array(datanc.variables['latitude'][:]))    
         #lons = np.append(lons, np.array(datanc.variables['longitude'][:])) 
         fhrs = np.append(fhrs, np.array(datanc.variables['fcst_hr'][:])) 
  

         obs_hs = np.append(obs_hs,np.array(datanc.variables['obs_hs'][:]))
         obs_wnd = np.append(obs_wnd, np.array(datanc.variables['obs_wnd'][:]))
         #obscal_wnd = np.append(obscal_wnd, np.array(datanc.variables['obs_wnd_cal'][:]))
         #obscal_hs = np.append(obscal_hs, np.array(datanc.variables['model_hs_cal'][:]))

         model_hs = np.append(model_hs, np.array(datanc.variables['model_hs'][:]))
         model_wnd = np.append(model_wnd, np.array(datanc.variables['model_wnd'][:]))

      day0=0   
      day=1
       
      while day <= endday:
        f0 = day0*24 
        f1 = day*24
        indx = np.where(( fhrs < f1 ) & ( fhrs > f0 ) & (~np.isnan(model_hs)))
        obs_hs_day = obs_hs[indx]
        obs_wnd_day = obs_wnd[indx]
        model_hs_day = model_hs[indx]
        model_wnd_day = model_wnd[indx]
    
        #calc stats: 
        diff_hs = model_hs_day - obs_hs_day 
        diff_wnd = model_wnd_day - obs_wnd_day 
  
        bias_hs = diff_hs.mean()
        bias_wnd = diff_wnd.mean()

        rmse_hs = (diff_hs**2).mean()**0.5 
        rmse_wnd = (diff_wnd**2).mean()**0.5

        rmse_hs_out = np.append(rmse_hs_out,rmse_hs)
        rmse_wnd_out = np.append(rmse_wnd_out,rmse_wnd) 
        bias_hs_out = np.append(bias_hs_out,bias_hs)
        bias_wnd_out = np.append(bias_wnd_out,bias_wnd)
        day_out = np.append(day_out,day)
        count_out = np.append(count_out,len(diff_hs))

        day0 = day
        day = day + 1

      print(f"day=")
      print(np.array2string(day_out, separator=', '))
      print(f"count_{model}_{season[k]}_{satelites[j]}=")
      print(np.array2string(count_out, separator=', '))
      print(f"bias_hs_{model}_{season[k]}_{satelites[j]}=")
      print(np.array2string(bias_hs_out, separator=', '))
      print(f"bias_wnd_{model}_{season[k]}_{satelites[j]}=")
      print(np.array2string(bias_wnd_out, separator=', '))
      print(f"rmse_hs_{model}_{season[k]}_{satelites[j]}=")
      print(np.array2string(rmse_hs_out, separator=', '))
      print(f"rmse_wnd_{model}_{season[k]}_{satelites[j]}=")
      print(np.array2string(rmse_wnd_out, separator=', '))


if __name__ == '__main__':
    main()
