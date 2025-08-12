import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt

# Load the NetCDF data
nc_file_path = './Altimeter_CRYOSAT2_HRsummer.nc'  # Replace with your actual file path
nc_data = nc.Dataset(nc_file_path, 'r')

# Extract data for significant wave height from the 'HTSGW_surface' variable
# Assuming the first index (time step) is what you want to plot
lats = nc_data.variables['latitude'][:]
lons = nc_data.variables['longitude'][:]
hs = nc_data.variables['hs'][:]  # Adjust this if the data dimensions require it

# Check data shapes
print("Longitude shape:", lons.shape)
print("Latitude shape:", lats.shape)
print("Wave height shape:", hs.shape)

# Flatten the data for plotting if necessary
lons_flat = lons.flatten()
lats_flat = lats.flatten()
hs_flat = hs.flatten()

# Create plot
fig, ax = plt.subplots(figsize=(12, 8))
scatter_plot = ax.scatter(lons_flat, lats_flat, c=hs_flat, cmap='viridis', s=20)
cbar = plt.colorbar(scatter_plot, ax=ax, orientation='vertical')
cbar.set_label('Significant Wave Height (m)')
ax.set_title('Global Significant Wave Height - Summer Season')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
#plt.show()
plt.savefig('significant_wave_height_summer.png', dpi=300, bbox_inches='tight')

