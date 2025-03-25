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
    file_paths = [
            os.path.join(directories[key], f"{filename}_{key}_{season}_{satellite_name}.nc")
            for key in directories ]

    # Check if all files exist and then process
    if all(os.path.exists(fp) for fp in file_paths):
        datasets = [nc.Dataset(fp, 'r') for fp in file_paths]
        dfs_hs = []
        dfs_wnd = []
        suffixes = ['_multi1', '_gfs', '_hr1', '_hr2', '_hr3a', '_hr3b', '_hr5']

########################## Ming Chen #############################################
        # check if time matches
        reference_time = datasets[0].variables['time'][:]
        for i, (ds, key) in enumerate(zip(datasets[1:], list(directories.keys())[1:]), 1):
            time_array = ds.variables['time'][:]
            if not np.array_equal(reference_time, time_array):
                print(f"Dataset {i} ({filename}_{key}) has a different time array!")
                print(f"Length: {len(time_array)} vs {len(reference_time)}")
                print(f"First 5: {time_array[:5]} vs {reference_time[:5]}")
            else:
                print(f"Dataset {i} ({filename}_{key}) time matches Dataset 0.")
###################################################################################

        for ds, suffix in zip(datasets, suffixes):
            df_hs = pd.DataFrame({
                    'time': ds.variables['time'][:],
                    'hs' + suffix: ds.variables['model_hs'][:]
            })
            df_hs = df_hs.reset_index().rename(columns={'index': 'row_id'})
            dfs_hs.append(df_hs)

            df_wnd = pd.DataFrame({
                    'time': ds.variables['time'][:],
                    'wnd' + suffix: ds.variables['model_wnd'][:]
            })
            df_wnd = df_wnd.reset_index().rename(columns={'index': 'row_id'})
            dfs_wnd.append(df_wnd)

        # Merging HS dataframes
        merged_hs = dfs_hs[0]
        for df in dfs_hs[1:]:
            merged_hs = pd.merge(merged_hs, df, on=['time', 'row_id'], how='inner')

        # Merging WND dataframes
        merged_wnd = dfs_wnd[0]
        for df in dfs_wnd[1:]:
            merged_wnd = pd.merge(merged_wnd, df, on=['time', 'row_id'], how='inner')

        # Adding observation data
        df_obs_hs = pd.DataFrame({
            'time': datasets[0].variables['time'][:],
            'obs_hs': datasets[0].variables['obs_hs_cal'][:]
        }).reset_index().rename(columns={'index': 'row_id'})
        
        df_obs_wnd = pd.DataFrame({
            'time': datasets[0].variables['time'][:],
            'obs_wnd': datasets[0].variables['obs_wnd_cal'][:]
        }).reset_index().rename(columns={'index': 'row_id'})
        
        merged_hs = pd.merge(merged_hs, df_obs_hs, on=['time', 'row_id'], how='inner')
        merged_wnd = pd.merge(merged_wnd, df_obs_wnd, on=['time', 'row_id'], how='inner')

        merged_hs = merged_hs.drop(columns=['row_id'])
        merged_wnd = merged_wnd.drop(columns=['row_id'])

        merged_hs = merged_hs.dropna()
        merged_wnd = merged_wnd.dropna()

        # Close datasets
        for ds in datasets:
            ds.close()

        ############################## MC Start #####################################################

#        csv_path = os.path.join(output_dir, f"merged_hs_{filename}_{satellite_name}_{season}.csv")
#        merged_hs.to_csv(csv_path, index=False)
#        print(f"Saved merged_hs to {csv_path}")

        model_columns_hs = ['hs_multi1', 'hs_gfs', 'hs_hr1', 'hs_hr2', 'hs_hr3a', 'hs_hr3b', 'hs_hr5']
        top_5_percent_info_hs = {}
        for col in model_columns_hs:
            top_5_threshold_hs = merged_hs[col].quantile(0.95)
            high_event_indexes_hs = merged_hs.index[merged_hs[col] > top_5_threshold_hs].tolist()
            top_5_percent_info_hs[col] = {
                'threshold': top_5_threshold_hs,
                'num_high_event': len(high_event_indexes_hs),
                'high_event_indexes': high_event_indexes_hs,
                'hs': merged_hs.loc[high_event_indexes_hs,col].tolist(),
                'obs_hs': merged_hs.loc[high_event_indexes_hs,'obs_hs'].tolist()
            }

        model_columns_wnd = ['wnd_multi1', 'wnd_gfs', 'wnd_hr1', 'wnd_hr2', 'wnd_hr3a', 'wnd_hr3b', 'wnd_hr5']
        top_5_percent_info_wnd = {}
        for col in model_columns_wnd:
            top_5_threshold_wnd = merged_wnd[col].quantile(0.95)
            high_event_indexes_wnd = merged_wnd.index[merged_wnd[col] > top_5_threshold_wnd].tolist()
            top_5_percent_info_wnd[col] = {
                'threshold': top_5_threshold_wnd,
                'num_high_event': len(high_event_indexes_wnd),
                'high_event_indexes': high_event_indexes_wnd,
                'wnd': merged_wnd.loc[high_event_indexes_wnd,col].tolist(),
                'obs_wnd': merged_wnd.loc[high_event_indexes_wnd,'obs_wnd'].tolist()
            }            
        
        # Create ModelObsPlot for top 5% high HS
        mop_hs = ModelObsPlot(
            model=np.c_[top_5_percent_info_hs['hs_multi1']['hs'], 
                        top_5_percent_info_hs['hs_gfs']['hs'],
                        top_5_percent_info_hs['hs_hr1']['hs'],
                        top_5_percent_info_hs['hs_hr2']['hs'],
                        top_5_percent_info_hs['hs_hr3a']['hs'],
                        top_5_percent_info_hs['hs_hr3b']['hs'],
                        top_5_percent_info_hs['hs_hr5']['hs']],
            obs=np.c_[top_5_percent_info_hs['hs_multi1']['obs_hs'], 
                        top_5_percent_info_hs['hs_gfs']['obs_hs'],
                        top_5_percent_info_hs['hs_hr1']['obs_hs'],
                        top_5_percent_info_hs['hs_hr2']['obs_hs'],
                        top_5_percent_info_hs['hs_hr3a']['obs_hs'],
                        top_5_percent_info_hs['hs_hr3b']['obs_hs'],
                        top_5_percent_info_hs['hs_hr5']['obs_hs']],
            axisnames=["Models", "Satellite"],
            mlabels=["MULTI1", "GFSv16", "HR1", "HR2", "HR3a", "HR3b", "HR5"],
            ftag=os.path.join(output_dir, f"plot_5%_HIGH_HS_{filename}_{satellite_name}_{season}")
        )
        mop_hs.qqplot()
        mop_hs.taylordiagram()

        # Create ModelObsPlot for top 5% high WND
        mop_wnd = ModelObsPlot(
            model=np.c_[top_5_percent_info_wnd['wnd_multi1']['wnd'], 
                        top_5_percent_info_wnd['wnd_gfs']['wnd'],
                        top_5_percent_info_wnd['wnd_hr1']['wnd'],
                        top_5_percent_info_wnd['wnd_hr2']['wnd'],
                        top_5_percent_info_wnd['wnd_hr3a']['wnd'],
                        top_5_percent_info_wnd['wnd_hr3b']['wnd'],
                        top_5_percent_info_wnd['wnd_hr5']['wnd']],
            obs=np.c_[top_5_percent_info_wnd['wnd_multi1']['obs_wnd'], 
                        top_5_percent_info_wnd['wnd_gfs']['obs_wnd'],
                        top_5_percent_info_wnd['wnd_hr1']['obs_wnd'],
                        top_5_percent_info_wnd['wnd_hr2']['obs_wnd'],
                        top_5_percent_info_wnd['wnd_hr3a']['obs_wnd'],
                        top_5_percent_info_wnd['wnd_hr3b']['obs_wnd'],
                        top_5_percent_info_wnd['wnd_hr5']['obs_wnd']],
            axisnames=["Models", "Satellite"],
            mlabels=["MULTI1", "GFSv16", "HR1", "HR2", "HR3a", "HR3b", "HR5"],
            ftag=os.path.join(output_dir, f"plot_5%_HIGH_WND_{filename}_{satellite_name}_{season}")
        )
        mop_wnd.qqplot()
        mop_wnd.taylordiagram()         
        
        ############################## MC End #####################################################

        # Create ModelObsPlot for HS
        mop_hs = ModelObsPlot(
            model=np.c_[merged_hs['hs_multi1'], merged_hs['hs_gfs'], merged_hs['hs_hr1'], merged_hs['hs_hr2'], merged_hs['hs_hr3a'], merged_hs['hs_hr3b'], merged_hs['hs_hr5']],
            obs=merged_hs['obs_hs'],
            axisnames=["Models", "Satellite"],
            mlabels=["MULTI1", "GFSv16", "HR1", "HR2", "HR3a", "HR3b", "HR5"],
            ftag=os.path.join(output_dir, f"plot_HS_{filename}_{satellite_name}_{season}")
        )
        mop_hs.qqplot()
        mop_hs.taylordiagram()

        # Create ModelObsPlot for WND
        mop_wnd = ModelObsPlot(
            model=np.c_[merged_wnd['wnd_multi1'], merged_wnd['wnd_gfs'], merged_wnd['wnd_hr1'], merged_wnd['wnd_hr2'], merged_wnd['wnd_hr3a'], merged_wnd['wnd_hr3b'], merged_wnd['wnd_hr5']],
            obs=merged_wnd['obs_wnd'],
            axisnames=["Models", "Satellite"],
            mlabels=["MULTI1", "GFSv16", "HR1", "HR2", "HR3a", "HR3b", "HR5"],
            ftag=os.path.join(output_dir, f"plot_WND_{filename}_{satellite_name}_{season}")
        )
        mop_wnd.qqplot()
        mop_wnd.taylordiagram()
    else:
        # Not all file paths exist message
        print(f"Some files for {filename} do not exist.")

