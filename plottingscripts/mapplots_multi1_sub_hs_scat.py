import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapGridded
from emcpy.plots.map_plots import MapScatter


def main():
  fhrs=[1,2,3,12,24,36,48,72,96,120,144,168]
  for fhr in fhrs:
    print('fhr=',fhr)

    basepath='/work/noaa/marine/jmeixner/Data/multi1/2020091300/gridded'
    prepath='multi_1.at_10m.t00z.f'

    filepath=basepath+'/'+prepath+'%03d.grib2.nc' % (fhr)
    datanc  = nc.Dataset(filepath)

    validtime = np.array(datanc.variables['time'][:]).astype('double')
    lats  = np.array(datanc.variables['latitude'][:])
    lons  = np.array(datanc.variables['longitude'][:])
    hs = np.array(datanc.variables['HTSGW_surface'][:])
    fill_val_hs = datanc.variables['HTSGW_surface'].__dict__['_FillValue']
    wnd = np.array(datanc.variables['WIND_surface'][:])
    fill_val_wnd = datanc.variables['WIND_surface'].__dict__['_FillValue']

    indx=np.where(hs==fill_val_hs) 
    hs[indx]=np.nan 
    indx=np.where(wnd==fill_val_wnd) 
    wnd[indx]=np.nan

    X, Y = np.meshgrid(lats, lons)


    datapath='/work2/noaa/marine/jmeixner/TestInterp/ww3-tools/ww3tools/testout_multiatl.nc'

    datanc2  = nc.Dataset(datapath)
    lats  = np.array(datanc2.variables['latitude'][:])
    lons  = np.array(datanc2.variables['longitude'][:])
    obs_hs = np.array(datanc2.variables['hs'][:])
    obs_wnd = np.array(datanc2.variables['wsp_cal'][:])
    model_hs = np.array(datanc2.variables['swh_interpolated'][:])
    model_wnd = np.array(datanc2.variables['ws_interpolated'][:])



    # Create gridded map object
    gridded = MapGridded(X, Y, np.transpose( hs[0] ))
    gridded.cmap = 'turbo'
    gridded.vmin = 0
    gridded.vmax = 15 


    scatter = MapScatter(lats, lons, obs_hs-model_hs)
    scatter.cmap = 'bwr'
    scatter.markersize = 1
    scatter.vmin=-.1
    scatter.vmax=.1


    atlantic_dict = {
        "extent": (-100, -20, 0, 80),
        "xticks": (-90, -80, -70, -60, -50, -40, -30),
        "yticks": (20, 30, 40, 50, 60),
        "cenlon": -60.,
        "cenlat": 40.
     }




    # Create plot object and add features
    plot1 = CreatePlot()
    plot1.plot_layers = [gridded, scatter]
    plot1.projection = 'plcarr'
    plot1.domain = ('custom', atlantic_dict)
    plot1.add_map_features(['coastline'])
    plot1.add_xlabel(xlabel='longitude')
    plot1.add_ylabel(ylabel='latitude')
    titleofplot='multi1 IC 2020091300 fhr %03d' % fhr 
    plot1.add_title(label=titleofplot, loc='center')
    plot1.add_grid()
    plot1.add_colorbar(label='Significant Wave Height [m]',
                       fontsize=12, extend='neither')

    # Create figure
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    
    figname='newh_multi1.f%03d.png' % (fhr)
    fig.save_figure(figname ) 
    fig.close_figure()







if __name__ == '__main__':
    main()
