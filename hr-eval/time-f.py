import netCDF4 as nc
import numpy as np
import os
import json
import netCDF4 as nc
import numpy as np
import glob
import os
import datetime



# Load configuration from JSON file
try:
    with open('/scratch2/NCEPDEV/marine/Ghazal.Mohammadpour/transfer/validation/WW3-tools/ww3tools/ORION/WW3-tools/ww3tools/config5.json') as f:
        config = json.load(f)
except json.JSONDecodeError as e:
    print(f"Failed to decode JSON: {e}")
    exit(1)  # Stop execution if JSON is invalid

# Iterate over each model configuration
for model_config in config['models']:
    model_dir = model_config['model_dir']
    base_output_dir = model_config['base_output_dir']

    # Get a list of all .nc files in the model directory
    nc_files_model = glob.glob(os.path.join(model_dir, '*.nc'))

    # Iterate over each time range
    for time_range in model_config['time_ranges']:
        start_hours = time_range['start']
        end_hours = time_range['end']

        # Initialize lists to store data for this time range
        all_model_hs = []
        all_obs_hs = []
        all_time = []
        all_model_wnd = []
        all_obs_wnd = []

        # Process each file
        for idx, file_path_model in enumerate(nc_files_model):
            print(f"Processing file {idx + 1} of {len(nc_files_model)} for time range {start_hours}-{end_hours} hours: {file_path_model}")
            dataset_model = nc.Dataset(file_path_model, 'r')

            try:
                # Extract necessary variables
                model_hs = dataset_model.variables['model_hs'][:]
                obs_hs = dataset_model.variables['obs_hs'][:]
                time = dataset_model.variables['time'][:]
                initial_condition_time = dataset_model.getncattr('initial_condition_time')
                model_wnd = dataset_model.variables['model_wnd'][:]
                obs_wnd = dataset_model.variables['obs_wnd'][:]
                fhrs = dataset_model.variables['fcst_hr'][:]


                dataset_model.close()

                # Calculate the desired time range in seconds
                desired_start_time = initial_condition_time + (start_hours * 3600)
                desired_end_time = initial_condition_time + (end_hours * 3600)

                # Find indices for the desired time range
                indices = np.where((time > desired_start_time) & (time <= desired_end_time))[0]
                #indices = np.where( (fhrs > start_hours) & ( fhrs < end_hours))

                # Extract data for the desired time range
                all_model_hs.append(model_hs[indices])
                all_obs_hs.append(obs_hs[indices])
                all_time.append(time[indices])
                all_model_wnd.append(model_wnd[indices])
                all_obs_wnd.append(obs_wnd[indices])
            except AttributeError as e:
                print(f"Warning: An error occurred - {e}")

        if all_time:
            all_model_hs = np.concatenate(all_model_hs)
            all_obs_hs = np.concatenate(all_obs_hs)
            all_time = np.concatenate(all_time)
            all_model_wnd = np.concatenate(all_model_wnd)
            all_obs_wnd = np.concatenate(all_obs_wnd)

            # Sort data by time
            sorted_indices = np.argsort(all_time)
            sorted_time = all_time[sorted_indices]
            sorted_model_hs = all_model_hs[sorted_indices]
            sorted_obs_hs = all_obs_hs[sorted_indices]
            sorted_model_wnd = all_model_wnd[sorted_indices]
            sorted_obs_wnd = all_obs_wnd[sorted_indices]

            # Construct output file path
            output_file = os.path.join(base_output_dir, f"filtered_{start_hours}h_to_{end_hours}h.nc")

            # Save filtered data to a new NetCDF file
            with nc.Dataset(output_file, 'w') as nc_out:
                nc_out.createDimension('time', len(sorted_time))
                nc_out.createVariable('time', 'f8', ('time',))
                nc_out.createVariable('model_hs', 'f8', ('time',))
                nc_out.createVariable('obs_hs', 'f8', ('time',))
                nc_out.createVariable('model_wnd', 'f8', ('time',))
                nc_out.createVariable('obs_wnd', 'f8', ('time',))
                nc_out.variables['time'][:] = sorted_time
                nc_out.variables['model_hs'][:] = sorted_model_hs
                nc_out.variables['obs_hs'][:] = sorted_obs_hs
                nc_out.variables['model_wnd'][:] = sorted_model_wnd
                nc_out.variables['obs_wnd'][:] = sorted_obs_wnd
        else:
            print(f"No data available for range {start_hours} to {end_hours} hours.")

