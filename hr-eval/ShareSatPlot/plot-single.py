import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import netCDF4 as nc
import datetime

# Paths to the NetCDF files
model_file_path = './old_gefswave.t00z.global.0p25.20180221.f003.nc'  # Replace with your model data file path
interpolated_file_path = './AltimeterAlongTrack_ww3tools_JASON3_2018010100to2018033118.nc'  # Adjusted file path

# Open the model data
model_nc = nc.Dataset(model_file_path, 'r')
lats_model = model_nc.variables['latitude'][:]
lons_model = model_nc.variables['longitude'][:]
hs_model = model_nc.variables['HTSGW_surface'][0, :, :]  
model_nc.close()

# Open the interpolated satellite data
interp_nc = nc.Dataset(interpolated_file_path, 'r')
interp_hs = interp_nc.variables['hs'][:500]  # Use 'hs' as the significant wave height variable
interp_lats = interp_nc.variables['latitude'][:500]
interp_lons = interp_nc.variables['longitude'][:500]
interp_nc.close()

# Calculate the extent around the satellite points
padding = 2.0  
min_lat, max_lat = np.min(interp_lats), np.max(interp_lats)
min_lon, max_lon = np.min(interp_lons), np.max(interp_lons)
extent = [min_lon-padding, max_lon+padding, min_lat-padding, max_lat+padding]

# Setting up the plot with Cartopy for geographic projections
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')

# Plotting model significant wave height with the calculated extent
contour_plot_model = ax.contourf(lons_model, lats_model, hs_model, transform=ccrs.PlateCarree(), cmap='viridis', extend='both')
ax.set_extent(extent, crs=ccrs.PlateCarree())

# Plotting interpolated satellite data
scatter_plot_interp = ax.scatter(interp_lons, interp_lats, c=interp_hs, cmap='viridis', edgecolor='black', s=50, transform=ccrs.PlateCarree())

# Adding a colorbar
cbar = plt.colorbar(contour_plot_model, ax=ax, orientation='vertical', extend='both')
cbar.set_label('Significant Wave Height (m)')

# Title and labels
plt.title('Global Significant Wave Height Comparison')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Save the figure
plt.savefig('significant_wave_height_comparison.png', bbox_inches='tight')

# Optionally display the plot
plt.show()

