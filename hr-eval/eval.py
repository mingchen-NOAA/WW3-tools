import netCDF4 as nc
import numpy as np
import pandas as pd
import os
import json
import matplotlib.pyplot as plt  # Import matplotlib for saving figures
from pvalstats import ModelObsPlot

# Load configuration settings from JSON file
with open('evalsumconfig.json') as config_file:
    config = json.load(config_file)

directories = config["directories"]
filenames = config["filenames"]
satellite_name = config["satellite_name"]
season = config["season"]
output_dir = config["output_dir"]

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

for filename in filenames:
    # Construct the full file paths for each model
    file_paths = [os.path.join(directories[key], filename) for key in directories]

    # Check if all files exist and then process
    if all(os.path.exists(fp) for fp in file_paths):
        datasets = [nc.Dataset(fp, 'r') for fp in file_paths]
        dfs_hs = []
        dfs_wnd = []
        suffixes = ['_hr3a', '_hr1', '_hr2', '_gfs', '_multi1', '_hr3b']
        for ds, suffix in zip(datasets, suffixes):
            dfs_hs.append(pd.DataFrame({'time': ds.variables['time'][:], 'hs' + suffix: ds.variables['model_hs'][:]}))
            dfs_wnd.append(pd.DataFrame({'time': ds.variables['time'][:], 'wnd' + suffix: ds.variables['model_wnd'][:]}))

        # Merging HS dataframes
        merged_hs = dfs_hs[0]
        for df in dfs_hs[1:]:
            merged_hs = pd.merge_asof(merged_hs, df, on='time')

        # Merging WND dataframes
        merged_wnd = dfs_wnd[0]
        for df in dfs_wnd[1:]:
            merged_wnd = pd.merge_asof(merged_wnd, df, on='time')

        # Adding observation data
        df_obs_hs = pd.DataFrame({'time': datasets[0].variables['time'][:], 'obs_hs': datasets[0].variables['obs_hs'][:]})
        df_obs_wnd = pd.DataFrame({'time': datasets[0].variables['time'][:], 'obs_wnd': datasets[0].variables['obs_wnd'][:]})
        merged_hs = pd.merge_asof(merged_hs, df_obs_hs, on='time')
        merged_wnd = pd.merge_asof(merged_wnd, df_obs_wnd, on='time')

        merged_hs = merged_hs.dropna()
        merged_wnd = merged_wnd.dropna()

        # Close datasets
        for ds in datasets:
            ds.close()

        # Create ModelObsPlot for HS
        mop_hs = ModelObsPlot(
            model=np.c_[merged_hs['hs_multi1'], merged_hs['hs_gfs'], merged_hs['hs_hr1'], merged_hs['hs_hr2'], merged_hs['hs_hr3a'], merged_hs['hs_hr3b']],
            obs=merged_hs['obs_hs'],
            axisnames=["Models", "Satellite"],
            mlabels=["MULTI1", "GFSv16", "HR1", "HR2", "HR3a", "HR3b"],
            ftag=os.path.join(output_dir, f"plot_HS_{filename}_{satellite_name}_{season}")
        )
        mop_hs.qqplot()
        mop_hs.taylordiagram()

        # Create ModelObsPlot for WND
        mop_wnd = ModelObsPlot(
            model=np.c_[merged_wnd['wnd_multi1'], merged_wnd['wnd_gfs'], merged_wnd['wnd_hr1'], merged_wnd['wnd_hr2'], merged_wnd['wnd_hr3a'], merged_wnd['wnd_hr3b']],
            obs=merged_wnd['obs_wnd'],
            axisnames=["Models", "Satellite"],
            mlabels=["MULTI1", "GFSv16", "HR1", "HR2", "HR3a", "HR3b"],
            ftag=os.path.join(output_dir, f"plot_WND_{filename}_{satellite_name}_{season}")
        )
        mop_wnd.qqplot()
        mop_wnd.taylordiagram()
    else:
        # Not all file paths exist message
        print(f"Some files for {filename} do not exist.")

