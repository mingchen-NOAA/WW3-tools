import sys
import calendar
import time
import numpy as np
import pandas as pd
import netCDF4 as nc
from datetime import datetime
import timeit
import wread

def along_track(AODN, adatemin, adatemax, wconfig):
    stime = []; rstime = []; slat = []; slon = []; swdepth = []; swdistcoast = []
    shs = []; shscal = []; swsp = []; swspcal = []

    filtered_AODN = AODN[(AODN['TIME'] >= adatemin) & (AODN['TIME'] <= adatemax)]

    for index, row in filtered_AODN.iterrows():
        stime.append(row['TIME'])
        rstime.append(row['TIME'])  # Assuming SAT_TIME is similar to TIME
        slat.append(row['LATITUDE'])
        slon.append(row['LONGITUDE'])
        swdepth.append(row['WDEPTH'])
        swdistcoast.append(row['DISTCOAST'])
        shs.append(row['HS'])
        shscal.append(row['HS_CAL'])
        swsp.append(row['WSPD'])
        swspcal.append(row['WSPD_CAL'])

    AODN_ALONGTRACK = pd.DataFrame({
        'TIME': stime, 'SAT_TIME': rstime, 'LATITUDE': slat, 'LONGITUDE': slon,
        'WDEPTH': swdepth, 'DISTCOAST': swdistcoast, 'HS': shs, 'HS_CAL': shscal,
        'WSPD': swsp, 'WSPD_CAL': swspcal
    })
    return AODN_ALONGTRACK

def save_to_netcdf(df, filename):
    with nc.Dataset(filename, 'w', format='NETCDF4') as dataset:
        time_dim = dataset.createDimension('time', None)
        times = dataset.createVariable('time', np.float64, ('time',))
        latitudes = dataset.createVariable('latitude', np.float32, ('time',))
        longitudes = dataset.createVariable('longitude', np.float32, ('time',))
        depths = dataset.createVariable('wdepth', np.float32, ('time',))
        distcoasts = dataset.createVariable('distcoast', np.float32, ('time',))
        hs = dataset.createVariable('hs', np.float32, ('time',))
        hs_cal = dataset.createVariable('hs_cal', np.float32, ('time',))
        wspd = dataset.createVariable('wspd', np.float32, ('time',))
        wspd_cal = dataset.createVariable('wspd_cal', np.float32, ('time',))

        times[:] = df['TIME'].to_numpy()
        latitudes[:] = df['LATITUDE'].to_numpy()
        longitudes[:] = df['LONGITUDE'].to_numpy()
        depths[:] = df['WDEPTH'].to_numpy()
        distcoasts[:] = df['DISTCOAST'].to_numpy()
        hs[:] = df['HS'].to_numpy()
        hs_cal[:] = df['HS_CAL'].to_numpy()
        wspd[:] = df['WSPD'].to_numpy()
        wspd_cal[:] = df['WSPD_CAL'].to_numpy()

        dataset.description = 'Processed Altimeter Data'
        dataset.source = 'Processed using Python script'

if __name__ == "__main__":
    start = timeit.default_timer()
    wconfig = wread.readconfig('ww3tools.yaml')

    altsel = sys.argv[1] if len(sys.argv) > 1 else 'default_satellite_mission'
    datemin = sys.argv[2] if len(sys.argv) > 2 else '1985010100'
    datemax = sys.argv[3] if len(sys.argv) > 3 else datetime.utcnow().strftime("%Y%m%d%H")

    adatemin = np.double(calendar.timegm(time.strptime(datemin, '%Y%m%d%H')))
    adatemax = np.double(calendar.timegm(time.strptime(datemax, '%Y%m%d%H')))

    AODN = wread.aodn_altimeter(altsel, wconfig, datemin, datemax)

    if wconfig['tspace'] == 2:
        AODN_ALONGTRACK = along_track(AODN, adatemin, adatemax, wconfig)
        save_to_netcdf(AODN_ALONGTRACK, 'output_raw-hurricane_Jason2-large.nc')  # Replace with desired filename

    stop = timeit.default_timer()
    print('Script successfully completed in ' + repr(int(round(stop - start, 0))) + ' seconds.')

