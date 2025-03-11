import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import netCDF4 as nc

# Paths to the NetCDF files
model_file_path = '/scratch2/NCEPDEV/marine/Saeideh.Banihashemi/GlobalDev/GEFS/Data/EP4c_1/20180221/c00/gridded/gefswave.t00z.global.0p25.20180221.nc'  # Replace with your actual model data file path
interpolated_file_path = './WW3.Altimeter_20180221_2018010101to2018033123.nc'

# Ask for the model time step index
model_time_step_idx = int(input("Enter the model time step index: "))  # User inputs the time step index

# Read model data
with nc.Dataset(model_file_path, 'r') as model_nc:
    lats_model = model_nc.variables['latitude'][:]
    lons_model = model_nc.variables['longitude'][:]
    hs_model = model_nc.variables['HTSGW_surface'][model_time_step_idx, :, :]  # Adjust variable name

# Read interpolated satellite data
with nc.Dataset(interpolated_file_path, 'r') as interp_nc:
    interp_htsgw = interp_nc.variables['HTSGW_surface'][model_time_step_idx, :]
    interp_lats = interp_nc.variables['latitude_sat'][:]
    interp_lons = interp_nc.variables['longitude_sat'][:]

# Select the first 500 points for the interpolated satellite track (you can change it)
interp_htsgw_track = interp_htsgw[:500]
interp_lats_track = interp_lats[:500]
interp_lons_track = interp_lons[:500]

# Determine the extent for the zoomed area
min_lat, max_lat = np.min(interp_lats_track), np.max(interp_lats_track)
min_lon, max_lon = np.min(interp_lons_track), np.max(interp_lons_track)
padding = 1.0  # degrees, adjust as necessary
extent = [min_lon-padding, max_lon+padding, min_lat-padding, max_lat+padding]

# Specify common color limits for both plots
cmin, cmax = 0, 5  # Adjust maximum as necessary

# Plotting
fig = plt.figure(figsize=(15, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.set_extent(extent, crs=ccrs.PlateCarree())

# Contour plot for the model's significant wave height data
contour_plot_model = ax.contourf(lons_model, lats_model, hs_model, levels=np.linspace(cmin, cmax, 256), vmin=cmin, vmax=cmax, transform=ccrs.PlateCarree(), cmap='viridis')

# Scatter plot for the interpolated satellite data
scatter_plot_interp = ax.scatter(interp_lons_track, interp_lats_track, c=interp_htsgw_track, cmap='viridis', vmin=cmin, vmax=cmax, edgecolor='black', s=50, transform=ccrs.PlateCarree())

# Colorbar
cbar = plt.colorbar(contour_plot_model, ax=ax, orientation='vertical', fraction=0.046, pad=0.04, extend='both')
cbar.set_label('Significant Wave Height (m)')

# Title
plt.title(f'Comparison of Model and Interpolated Satellite Significant Wave Height (First 500 Points)', fontsize=14)

# Show the plot
plt.show()

