import netCDF4 as nc
import numpy as np
import pandas as pd
import os
import json
import matplotlib.pyplot as plt  # Import matplotlib for saving figures
from pvalstats import ModelObsPlot

# PDF and CDF
import seaborn as sns
from scipy.stats import ks_2samp

# Load configuration settings from JSON file
with open('evalsumconfig_hurricane.json') as config_file:
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
        suffixes = ['_gfs', '_hr1', '_hr2', '_hr3b', '_hr5']

########################## Ming Chen #############################################
        # check if time matches
        all_verified = True
        reference_time = datasets[0].variables['time'][:]
        for i, (ds, key) in enumerate(zip(datasets[1:], list(directories.keys())[1:]), 1):
            time_array = ds.variables['time'][:]
            if not np.array_equal(reference_time, time_array):
                print(f"Dataset {i} ({filename}_{key}) has a different time array!")
                print(f"Length: {len(time_array)} vs {len(reference_time)}")
                print(f"First 5: {time_array[:5]} vs {reference_time[:5]}")
                all_verified = False

        if all_verified:
            print("\nAll dataset time matches.")
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

#####################################################################################################
        # verify merged data against combined data
        def verify_merged_data(merged_df, datasets, variable_type, suffixes):
            print(f"Verifying {variable_type} data:")
            all_verified = True

            for i, (ds, suffix) in enumerate(zip(datasets, suffixes)):
                raw_data = ds.variables[f'model_{variable_type}'][:]
                merged_data = merged_df[f'{variable_type}{suffix}'].values

                if len(raw_data) != len(merged_data):
                    print(f"Note: Length difference for {variable_type}{suffix}: "
                          f"raw={len(raw_data)}, merged={len(merged_data)}")

                # Check if values match (accounting for NaN values and shorter length)
                min_length = min(len(raw_data), len(merged_data))
                raw_data_subset = raw_data[:min_length]
                merged_data_subset = merged_data[:min_length]

                mask = ~np.isnan(raw_data_subset) & ~np.isnan(merged_data_subset)

                if mask.sum() == 0:
                    print(f"No comparable values for {variable_type}{suffix} (all NaN)")
                    all_verified = False
                elif not np.allclose(raw_data_subset[mask], merged_data_subset[mask]):
                    print(f"Value mismatch detected in {variable_type}{suffix}")
                    all_verified = False
            if all_verified:
                print(f"All {variable_type} data verified successfully")

        # Verify the merged dataframes
        verify_merged_data(merged_hs, datasets, 'hs', suffixes)
        verify_merged_data(merged_wnd, datasets, 'wnd', suffixes)
#####################################################################################################

        merged_hs = merged_hs.dropna()
        merged_wnd = merged_wnd.dropna()

        # Close datasets
        for ds in datasets:
            ds.close()

        ############################## MC Start #####################################################

#        csv_path = os.path.join(output_dir, f"merged_hs_{filename}_{satellite_name}_{season}.csv")
#        merged_hs.to_csv(csv_path, index=False)
#        print(f"Saved merged_hs to {csv_path}")

        top_5_threshold_hs = merged_hs['obs_hs'].quantile(0.95)
        high_event_indexes_hs = merged_hs.index[merged_hs['obs_hs'] > top_5_threshold_hs].tolist()
        merged_hs_high = merged_hs.loc[high_event_indexes_hs].copy()

        top_5_threshold_wnd = merged_wnd['obs_wnd'].quantile(0.95)
        high_event_indexes_wnd = merged_wnd.index[merged_wnd['obs_wnd'] > top_5_threshold_wnd].tolist()
        merged_wnd_high = merged_wnd.loc[high_event_indexes_wnd].copy()

        model_columns_hs = ['hs_gfs', 'hs_hr1', 'hs_hr2', 'hs_hr3b', 'hs_hr5']
        model_columns_wnd = ['wnd_gfs', 'wnd_hr1', 'wnd_hr2', 'wnd_hr3b', 'wnd_hr5']

        model_labels = ['GFS', 'HR1', 'HR2', 'HR3b', 'HR5']


        # Create ModelObsPlot for top 5% high HS
        mop_hs = ModelObsPlot(
            model=np.c_[merged_hs_high['hs_gfs'], merged_hs_high['hs_hr1'], merged_hs_high['hs_hr2'], merged_hs_high['hs_hr3b'], merged_hs_high['hs_hr5']],
            obs=merged_hs_high['obs_hs'],
            axisnames=["Models", "Satellite"],
            mlabels=["GFSv16", "HR1", "HR2", "HR3b", "HR5"],
            ftag=os.path.join(output_dir, f"plot_5%_HIGH_HS_{filename}_{satellite_name}_{season}")
        )
        mop_hs.qqplot()
        mop_hs.taylordiagram()

        for col, label in zip(model_columns_hs, model_labels):
            mop_hs = ModelObsPlot(
                model=merged_hs_high[col].values.reshape(-1, 1),
                obs=merged_hs_high['obs_hs'],
                linreg=True,
                axisnames=["Model", "Satellite"],
                color=['blue'],
                mlabels=[label],
                ftag=os.path.join(output_dir, f"plot_5%_HIGH_HS_{filename}_{satellite_name}_{season}_{label}_")
            )
            mop_hs.scatterplot()

        # Create ModelObsPlot for top 5% high WND
        mop_wnd = ModelObsPlot(
            model=np.c_[merged_wnd_high['wnd_gfs'], merged_wnd_high['wnd_hr1'], merged_wnd_high['wnd_hr2'], merged_wnd_high['wnd_hr3b'], merged_wnd_high['wnd_hr5']],
            obs=merged_wnd_high['obs_wnd'],
            axisnames=["Models", "Satellite"],
            mlabels=["GFSv16", "HR1", "HR2", "HR3b", "HR5"],
            ftag=os.path.join(output_dir, f"plot_5%_HIGH_WND_{filename}_{satellite_name}_{season}")
        )
        mop_wnd.qqplot()
        mop_wnd.taylordiagram()

        for col, label in zip(model_columns_wnd, model_labels):
            mop_wnd = ModelObsPlot(
                model=merged_wnd_high[col].values.reshape(-1, 1),
                obs=merged_wnd_high['obs_wnd'],
                linreg=True,
                axisnames=["Model", "Satellite"],
                color=['blue'],
                mlabels=[label],
                ftag=os.path.join(output_dir, f"plot_5%_HIGH_WND_{filename}_{satellite_name}_{season}_{label}_")
            )
            mop_wnd.scatterplot()

        ## PDF and CDF
        def pdf_plot(dataframe, models, ftag, flag):
            model_labels = ['GFSv16', 'HR1', 'HR2', 'HR3b', 'HR5']
            colors = {
                'Satellite': 'black',
                'GFSv16': 'darkblue',
                'HR1': 'darkred',
                'HR2': 'darkgreen',
                'HR3b': 'purple',
                'HR5': 'deeppink'
            }

            fig = plt.figure(1, figsize=(5, 4.5))
            ax = fig.add_subplot(111)
            if flag=='hs':
                sns.kdeplot(dataframe['obs_hs'], label='Satellite', color=colors['Satellite'], linewidth=3)
            else:
                sns.kdeplot(dataframe['obs_wnd'], label='Satellite', color=colors['Satellite'], linewidth=3)

            for col, label in zip(models, model_labels):
                sns.kdeplot(dataframe[col], label=label, color=colors[label])

            if flag=='hs':
                plt.xlabel('Significant Wave Height')
            else:
                plt.xlabel('Wind Speed')

            plt.ylabel('Density')
            plt.title('PDF Comparison: Satellite vs Models')
            plt.legend()
            plt.tight_layout()
            plt.savefig(ftag + 'PDF.png', dpi=200, facecolor='w', edgecolor='w', orientation='portrait',
                        format='png', transparent=False, bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            del fig, ax

        # Plot Hs PDF
        model_hs_columns = ['hs_gfs', 'hs_hr1', 'hs_hr2', 'hs_hr3b', 'hs_hr5']
        ftag = os.path.join(output_dir, f"plot_5%_HIGH_HS_PDF_{filename}_{satellite_name}_{season}")
        pdf_plot(merged_hs_high, model_hs_columns, ftag, 'hs')

        ftag = os.path.join(output_dir, f"plot_HS_PDF_{filename}_{satellite_name}_{season}")
        pdf_plot(merged_hs, model_hs_columns, ftag, 'hs')

        # Plot WND PDF
        model_wnd_columns = ['wnd_gfs', 'wnd_hr1', 'wnd_hr2', 'wnd_hr3b', 'wnd_hr5']
        ftag = os.path.join(output_dir, f"plot_5%_HIGH_WND_PDF_{filename}_{satellite_name}_{season}")
        pdf_plot(merged_wnd_high, model_wnd_columns, ftag, 'wnd')

        ftag = os.path.join(output_dir, f"plot_WND_PDF_{filename}_{satellite_name}_{season}")
        pdf_plot(merged_wnd, model_wnd_columns, ftag, 'wnd')

        ############################## MC End #####################################################

        # Create ModelObsPlot for HS
        mop_hs = ModelObsPlot(
            model=np.c_[merged_hs['hs_gfs'], merged_hs['hs_hr1'], merged_hs['hs_hr2'], merged_hs['hs_hr3b'], merged_hs['hs_hr5']],
            obs=merged_hs['obs_hs'],
            axisnames=["Models", "Satellite"],
            mlabels=["GFSv16", "HR1", "HR2", "HR3b", "HR5"],
            ftag=os.path.join(output_dir, f"plot_HS_{filename}_{satellite_name}_{season}")
        )
        mop_hs.qqplot()
        mop_hs.taylordiagram()

        for col, label in zip(model_columns_hs, model_labels):
            mop_hs = ModelObsPlot(
                model=merged_hs[col].values.reshape(-1, 1),
                obs=merged_hs['obs_hs'],
                linreg=True,
                axisnames=["Model", "Satellite"],
                color=['blue'],
                mlabels=[label],
                ftag=os.path.join(output_dir, f"plot_HS_{filename}_{satellite_name}_{season}_{label}_")
            )
            mop_hs.scatterplot()

        # Create ModelObsPlot for WND
        mop_wnd = ModelObsPlot(
            model=np.c_[merged_wnd['wnd_gfs'], merged_wnd['wnd_hr1'], merged_wnd['wnd_hr2'], merged_wnd['wnd_hr3b'], merged_wnd['wnd_hr5']],
            obs=merged_wnd['obs_wnd'],
            axisnames=["Models", "Satellite"],
            mlabels=["GFSv16", "HR1", "HR2", "HR3b", "HR5"],
            ftag=os.path.join(output_dir, f"plot_WND_{filename}_{satellite_name}_{season}")
        )
        mop_wnd.qqplot()
        mop_wnd.taylordiagram()

        for col, label in zip(model_columns_wnd, model_labels):
            mop_wnd = ModelObsPlot(
                model=merged_wnd[col].values.reshape(-1, 1),
                obs=merged_wnd['obs_wnd'],
                linreg=True,
                axisnames=["Model", "Satellite"],
                color=['blue'],
                mlabels=[label],
                ftag=os.path.join(output_dir, f"plot_WND_{filename}_{satellite_name}_{season}_{label}_")
            )
            mop_wnd.scatterplot()

    else:
        # Not all file paths exist message
        print(f"Some files for {filename} do not exist.")

