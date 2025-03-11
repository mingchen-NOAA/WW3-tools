import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import argparse

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapScatter
from emcpy.plots.plots import Scatter
from emcpy.plots.create_plots import CreatePlot, CreateFigure

import datetime as dt
from dateutil.relativedelta import relativedelta
import os

'''
ScatterPlot.py creates scatter density plots (model vs obs) by day for a model input for HR experiments and obs  
'''

def main():

  ap = argparse.ArgumentParser()
  ap.add_argument('-m', '--model', help="String Identifier of Model 'multi1', 'GFSv16', 'HR1', 'HR2', 'HR3a', 'HR3b'", required=True)
  MyArgs = ap.parse_args()

  model = MyArgs.model

  satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT

  if model == "GFSv16": 
    season=['summer', 'hurricane']
  else: 
    season=['winter', 'summer', 'hurricane']

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

    #if multi-1 end at day 7
    if model == "multi1":
      endday = 7


    nowdate = startdate
    dates1 = []
    while nowdate <= enddate:
       dates1.append(nowdate.strftime('%Y%m%d%H'))
       nowdate = nowdate + dt.timedelta(days=datestride)

    for j in range(len(satelites)): 
      time = []; lats = []; lons = []
      fhrs = []
      obs_hs = []; obs_wnd = []
      model_hs = []; model_wnd = []
      for i in range(len(dates1)):
         #list of grids for each model.  First should be "global" or the base, followed by high resolution inserts in the order 
         #of lower(global) to higher(regional) resolution. 
         if model == "multi1":
            grids=['global.0p50', 'alaska.0p16', 'atlocn.0p16', 'epacif.0p16', 'wcoast.0p16', 'alaska.0p06', 'atlocn.0p06', 'wcoast.0p06']
         elif model == "GFSv16":
            grids=['global.0p25', 'global.0p16']
         else:
            grids=['global.0p25']

         for g in range(len(grids)): 

            OUTDIR=f"/work2/noaa/marine/jmeixner/processsatdata/outinterp/{model}" 
            #OUTDIR=f"/scratch1/NCEPDEV/climate/Jessica.Meixner/processsatdata/outinterp/{model}"
            if model == "multi1": 
               OUTPUT_FILE=f"{model}_{grids[g]}_{dates1[i]}_{satelites[j]}.nc"
            elif model == "GFSv16":
               OUTPUT_FILE=f"{model}_{grids[g]}_{dates1[i]}_{satelites[j]}.nc"
            else: 
               OUTPUT_FILE=f"{model}_{grids[g]}_{season[k]}_{dates1[i]}_{satelites[j]}.nc"

            datapath = OUTDIR + "/" + OUTPUT_FILE
            datanc  = nc.Dataset(datapath)
            if g == 0:
               #this is the global/base grid:  
               time_tmpbase = np.array(datanc.variables['time'][:])
               fhrs_tmpbase = np.array(datanc.variables['fcst_hr'][:])
               lats_tmpbase = np.array(datanc.variables['latitude'][:])
               lons_tmpbase = np.array(datanc.variables['longitude'][:])
               obs_hs_tmpbase = np.array(datanc.variables['obs_hs'][:])
               obs_wnd_tmpbase = np.array(datanc.variables['obs_wnd_cal'][:])
               model_hs_tmpbase = np.array(datanc.variables['model_hs'][:])
               model_wnd_tmpbase = np.array(datanc.variables['model_wnd'][:]) 
            else: 
               #this is s a higher resolution sub-grid 
               time_tmphigh = np.array(datanc.variables['time'][:])
               fhrs_tmphigh = np.array(datanc.variables['fcst_hr'][:])
               lats_tmphigh = np.array(datanc.variables['latitude'][:])
               lons_tmphigh = np.array(datanc.variables['longitude'][:])
               obs_hs_tmphigh = np.array(datanc.variables['obs_hs'][:])
               obs_wnd_tmphigh = np.array(datanc.variables['obs_wnd_cal'][:])
               model_hs_tmphigh = np.array(datanc.variables['model_hs'][:])
               model_wnd_tmphigh = np.array(datanc.variables['model_wnd'][:])
               #Check that obs values are the same for sanity check and if so, 
               #replace model values with high res inserts where HS is not nan 
               if ((obs_hs_tmphigh == obs_hs_tmpbase).all()): 
                 np.where(~np.isnan(model_hs_tmphigh), model_hs_tmpbase, model_hs_tmphigh)
                 np.where(~np.isnan(model_hs_tmphigh), model_wnd_tmpbase, model_wnd_tmphigh)

            time = np.append(time, time_tmpbase) 
            lats = np.append(lats, lats_tmpbase)
            lons = np.append(lons, lons_tmpbase)
            fhrs = np.append(fhrs, fhrs_tmpbase)
            obs_hs = np.append(obs_hs, obs_hs_tmpbase)
            obs_wnd = np.append(obs_wnd, obs_wnd_tmpbase)

            model_hs = np.append(model_hs, model_hs_tmpbase)
            model_wnd = np.append(model_wnd, model_wnd_tmpbase) 


      day0=0   
      day=1 

      while day <= endday:
        f0 = day0*24 
        f1 = day*24
        indx=np.where(( fhrs < f1 ) & ( fhrs > f0 ) & (~np.isnan(model_hs))) 
        obs_hs_day = obs_hs[indx]
        obs_wnd_day = obs_wnd[indx]
        model_hs_day = model_hs[indx]
        model_wnd_day = model_wnd[indx]

        # Create Scatter object
        sctr1 = Scatter(obs_hs_day, model_hs_day)
        sctr1.density_scatter()
        sctr1.do_linear_regression = True
        sctr1.add_linear_regression()
        plot1 = CreatePlot()
        plot1.plot_layers = [sctr1]
        plot1.add_title(label=f"HS Day {day} {model} {satelites[j]} {season[k]}")
        plot1.add_xlabel(xlabel=f"observation ({satelites[j]})")
        plot1.add_ylabel(ylabel=f"model ({model})")
        plot1.add_legend()
        plot1.set_xlim(0,15) 
        plot1.set_ylim(0,15) 
        fig = CreateFigure()
        fig.plot_list = [plot1]
        fig.create_figure()
        fig.save_figure(f"scatter_HS_{model}_{satelites[j]}_{season[k]}_day{day}.png")
        fig.close_figure()    

        sctr1 = Scatter(obs_wnd_day, model_wnd_day)
        sctr1.density_scatter()
        sctr1.do_linear_regression = True
        sctr1.add_linear_regression()
        plot1 = CreatePlot()
        plot1.plot_layers = [sctr1]
        plot1.add_title(label=f"WND Day {day} {model} {satelites[j]} {season[k]}")
        plot1.add_xlabel(xlabel=f"observation ({satelites[j]})")
        plot1.add_ylabel(ylabel=f"model ({model})")
        plot1.add_legend()
        plot1.set_xlim(0,35) 
        plot1.set_ylim(0,35) 
        fig = CreateFigure()
        fig.plot_list = [plot1]
        fig.create_figure()
        fig.save_figure(f"scatter_WND_{model}_{satelites[j]}_{season[k]}_day{day}.png")
        fig.close_figure()

        day0 = day
        day = day + 1


if __name__ == '__main__':
    main()
