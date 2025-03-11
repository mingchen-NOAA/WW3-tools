import datetime
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapScatter
from emcpy.plots.plots import Scatter
from emcpy.plots.create_plots import CreatePlot, CreateFigure


def main():
    # Create test data
    datapath='/work/noaa/marine/jmeixner/2020091300/HR1hurr_JASON3_2020091300.nc'
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


    indx=np.where((fhrs < 24.) & (fhrs>1)) 
    model_hs1=model_hs[indx]
    obs_hs1=obs_hs[indx]
    lats1=lats[indx]
    lons1=lons[indx]
    obs_wnd1=obs_wnd[indx]
    model_wnd1=model_wnd[indx]

    indx=np.where((fhrs < 48.) & (fhrs>24))
    model_hs2=model_hs[indx]
    obs_hs2=obs_hs[indx]
    lats2=lats[indx]
    lons2=lons[indx]
    obs_wnd2=obs_wnd[indx]
    model_wnd2=model_wnd[indx]

    indx=np.where((fhrs < 72.) & (fhrs>48))
    model_hs3=model_hs[indx]
    obs_hs3=obs_hs[indx]
    lats3=lats[indx]
    lons3=lons[indx]
    obs_wnd3=obs_wnd[indx]
    model_wnd3=model_wnd[indx]

    indx=np.where((fhrs < 96.) & (fhrs>72))
    model_hs4=model_hs[indx]
    obs_hs4=obs_hs[indx]
    lats4=lats[indx]
    lons4=lons[indx]
    obs_wnd4=obs_wnd[indx]
    model_wnd4=model_wnd[indx]

    indx=np.where((fhrs < 120.) & (fhrs>96))
    model_hs5=model_hs[indx]
    obs_hs5=obs_hs[indx]
    lats5=lats[indx]
    lons5=lons[indx]
    obs_wnd5=obs_wnd[indx]
    model_wnd5=model_wnd[indx]


    indx=np.where((fhrs < 144) & (fhrs>120))
    model_hs6=model_hs[indx]
    obs_hs6=obs_hs[indx]
    lats6=lats[indx]
    lons6=lons[indx]
    obs_wnd6=obs_wnd[indx]
    model_wnd6=model_wnd[indx]

    indx=np.where((fhrs < 168.) & (fhrs>144))
    model_hs7=model_hs[indx]
    obs_hs7=obs_hs[indx]
    lats7=lats[indx]
    lons7=lons[indx]
    obs_wnd7=obs_wnd[indx]
    model_wnd7=model_wnd[indx]

# Create Scatter object
    sctr1 = Scatter(obs_hs1, model_hs1)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 HS Day1')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,15) #np.nanmax(obs_hs))
    plot1.set_ylim(0,15) #np.nanmax(obs_hs))
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_hs_day1.png')
    fig.close_figure()    
    sctr1 = Scatter(obs_wnd1, model_wnd1)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 Wind Day1')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,35) #np.nanmax(obs_hs))
    plot1.set_ylim(0,35) #np.nanmax(obs_hs))
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_wind_day1.png')
    fig.close_figure()


#DAY2 

    sctr1 = Scatter(obs_hs2, model_hs2)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 HS Day2')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,15) #np.nanmax(obs_hs))
    plot1.set_ylim(0,15) #np.nanmax(obs_hs))
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_hs_day2.png')
    fig.close_figure()
    sctr1 = Scatter(obs_wnd2, model_wnd2)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 Wind Day2')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,35) 
    plot1.set_ylim(0,35) 
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_wind_day2.png')
    fig.close_figure()

#DAY3 

    sctr1 = Scatter(obs_hs3, model_hs3)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 HS Day3')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,15) #np.nanmax(obs_hs))
    plot1.set_ylim(0,15) #np.nanmax(obs_hs))
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_hs_day3.png')
    fig.close_figure()
    sctr1 = Scatter(obs_wnd3, model_wnd3)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 Wind Day3')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,35)
    plot1.set_ylim(0,35)
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_wind_day3.png')
    fig.close_figure()


#DAY 5 

    sctr1 = Scatter(obs_hs5, model_hs5)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 HS Day5')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,15) #np.nanmax(obs_hs))
    plot1.set_ylim(0,15) #np.nanmax(obs_hs))
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_hs_day5.png')
    fig.close_figure()
    sctr1 = Scatter(obs_wnd5, model_wnd5)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 Wind Day5')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,35)
    plot1.set_ylim(0,35)
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_wind_day5.png')
    fig.close_figure()


#DAY 7 

    sctr1 = Scatter(obs_hs7, model_hs7)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 HS Day7')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,15) #np.nanmax(obs_hs))
    plot1.set_ylim(0,15) #np.nanmax(obs_hs))
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_hs_day7.png')
    fig.close_figure()
    sctr1 = Scatter(obs_wnd7, model_wnd7)
    sctr1.density_scatter()
    plot1 = CreatePlot()
    plot1.plot_layers = [sctr1]
    plot1.add_title(label='HR1 Wind Day7')
    plot1.add_xlabel(xlabel='observation (JASON3)')
    plot1.add_ylabel(ylabel='model')
    plot1.add_legend()
    plot1.set_xlim(0,35)
    plot1.set_ylim(0,35)
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    fig.save_figure('scatter_HR1JASON3_wind_day7.png')
    fig.close_figure()

if __name__ == '__main__':
    main()
