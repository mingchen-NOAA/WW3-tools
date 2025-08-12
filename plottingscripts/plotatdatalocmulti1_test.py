import datetime
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapScatter


def main():
    # Create test data
    datapath='/work/noaa/marine/jmeixner/2020091300/multi1hurr_JASON3_2020091300.nc'
    datapath='/work/noaa/marine/jmeixner/Hours24to48/20200913/multi1hurricane_JASON3_2020091300.nc'
    datapath='/work2/noaa/marine/jmeixner/TestInterp/ww3-tools/ww3tools/testout_multiatl.nc'

    datanc  = nc.Dataset(datapath)
    validtime = np.array(datanc.variables['time'][:])
    lats  = np.array(datanc.variables['latitude'][:])
    lons  = np.array(datanc.variables['longitude'][:])
    obs_hs = np.array(datanc.variables['hs'][:])
    obs_wnd = np.array(datanc.variables['wsp_cal'][:])
    model_hs = np.array(datanc.variables['swh_interpolated'][:])
    model_wnd = np.array(datanc.variables['ws_interpolated'][:])

    res_date=datetime.date(2020, 9, 13)
    refcdate=((np.datetime64(res_date) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).astype('double')

    fhrs=np.array((validtime-refcdate)/3600)

    #indx=np.where((fhrs < 72.) & (fhrs>24)) 
    #model_hs=model_hs[indx]
    #obs_hs=obs_hs[indx]
    #lats=lats[indx]
    #lons=lons[indx]
    #obs_wnd=obs_wnd[indx]
    #model_wnd=model_wnd[indx]

    atlantic_dict = {
        "extent": (-100, -20, 10, 70),
        "xticks": (-90, -80, -70, -60, -50, -40, -30),
        "yticks": (20, 30, 40, 50, 60),
        "cenlon": -60.,
        "cenlat": 40.
     }


    # Create scatter plot on CONUS domian
    scatter = MapScatter(lats, lons, obs_hs-model_hs)
    scatter.cmap = 'bwr'
    scatter.markersize = 20
    scatter.vmin=-1
    scatter.vmax=1 
    plot1 = CreatePlot()
    plot1.plot_layers = [scatter]
    plot1.projection = 'plcarr'
    plot1.domain = ('custom', atlantic_dict)
    plot1.add_map_features(['coastline'])
    plot1.add_xlabel(xlabel='longitude')
    plot1.add_ylabel(ylabel='latitude')
    plot1.add_title(label='HS [m]', loc='center',
                    fontsize=20)
    plot1.add_colorbar(label='obs (JASON3) - model',
                       fontsize=12, extend='neither')
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('new_atl_hsdiff_JASON3_multi1_day2.png')
    fig.close_figure()    


    scatter = MapScatter(lats, lons, obs_wnd-model_wnd)
    scatter.cmap = 'bwr'
    scatter.markersize = 20
    scatter.vmin=-5
    scatter.vmax=5
    plot1 = CreatePlot()
    plot1.plot_layers = [scatter]
    plot1.projection = 'plcarr'
    plot1.domain = ('custom', atlantic_dict)
    plot1.add_map_features(['coastline'])
    plot1.add_xlabel(xlabel='longitude')
    plot1.add_ylabel(ylabel='latitude')
    plot1.add_title(label='Wind Speed [m/s]', loc='center',
                    fontsize=20)
    plot1.add_colorbar(label='obs (JASON3) - model',
                       fontsize=12, extend='neither')
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('new_atl_wnddiff_JASON3_multi1_day2.png')
    fig.close_figure()


    scatter = MapScatter(lats, lons, model_hs)
    scatter.cmap = 'turbo'
    scatter.markersize = 20
    scatter.vmin=0
    scatter.vmax=15
    plot1 = CreatePlot()
    plot1.plot_layers = [scatter]
    plot1.projection = 'plcarr'
    plot1.domain = ('custom', atlantic_dict)
    plot1.add_map_features(['coastline'])
    plot1.add_xlabel(xlabel='longitude')
    plot1.add_ylabel(ylabel='latitude')
    plot1.add_title(label='HS [m]', loc='center',
                    fontsize=20)
    plot1.add_colorbar(label='model',
                       fontsize=12, extend='neither')
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('new_atl_hs_multi1_day2.png')
    fig.close_figure()


    scatter = MapScatter(lats, lons, model_wnd)
    scatter.cmap = 'turbo'
    scatter.markersize = 20
    scatter.vmin=0
    scatter.vmax=35
    plot1 = CreatePlot()
    plot1.plot_layers = [scatter]
    plot1.projection = 'plcarr'
    plot1.domain = ('custom', atlantic_dict)
    plot1.add_map_features(['coastline'])
    plot1.add_xlabel(xlabel='longitude')
    plot1.add_ylabel(ylabel='latitude')
    plot1.add_title(label='Wind Speed [m/s]', loc='center',
                    fontsize=20)
    plot1.add_colorbar(label='model',
                       fontsize=12, extend='neither')
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('new_atl_wnd_multi1_day2.png')
    fig.close_figure()



if __name__ == '__main__':
    main()
