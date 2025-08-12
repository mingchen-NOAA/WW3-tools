import datetime
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapScatter


def main():
    # Create test data
    datapath='/work/noaa/marine/jmeixner/2020091300/HR3ascout_JASON3_2020091300.nc'
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
    print(fhrs)

    print('fhrmin',np.min(fhrs)) 
    print('fhrmax',np.max(fhrs)) 
    howmanyhours=(np.max(validtime)-np.min(validtime))/3600 
    print('howmanyhours',howmanyhours)

    print(validtime.shape)
    print(fhrs.shape)
    print(obs_hs.shape)

    indx=np.where((fhrs < 72.) & (fhrs>24)) 
    model_hs=model_hs[indx]
    obs_hs=obs_hs[indx]
    lats=lats[indx]
    lons=lons[indx]
    obs_wnd=obs_wnd[indx]
    model_wnd=model_wnd[indx]

    # Create scatter plot on CONUS domian
    scatter = MapScatter(lats, lons, obs_wnd-model_wnd)
    # change colormap and markersize
    scatter.cmap = 'bwr'
    scatter.markersize = 5
    #scatter.vmin=-3
    #scatter.vmax=3

    atlantic_dict = {
        "extent": (-100, -20, 10, 70),
        "xticks": (-90, -80, -70, -60, -50, -40, -30),
        "yticks": (20, 30, 40, 50, 60),
        "cenlon": -60.,
        "cenlat": 40.
     }


    # Create plot object and add features
    plot1 = CreatePlot()
    plot1.plot_layers = [scatter]
    plot1.projection = 'plcarr'

    plot1.domain = ('custom', atlantic_dict)
    plot1.add_map_features(['coastline'])
    plot1.add_xlabel(xlabel='longitude')
    plot1.add_ylabel(ylabel='latitude')
    plot1.add_title(label='HS', loc='center',
                    fontsize=20)
    plot1.add_colorbar(label='obs (JASON3) - model (HR3a scout run) ',
                       fontsize=12, extend='neither')

    # annotate some stats
    #stats_dict = {
    #    'nobs': len(np.linspace(200, 300, 30)),
    #    'vmin': 200,
    #    'vmax': 300,
    #}
    #plot1.add_stats_dict(stats_dict=stats_dict, yloc=-0.175)

    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()

    #plotpath = outpath+'/scatter'+'%03d.png' % (ihr)
    fig.save_figure('atl_wnddiff_hr3aJASON3_day2.png')
    fig.close_figure()    



if __name__ == '__main__':
    main()
