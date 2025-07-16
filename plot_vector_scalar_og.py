import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import sys

year = sys.argv[1] if len(sys.argv) > 1 else '6'  # Default to Year6 if no argument is provided
print(f"Processing data for Year: {year}")
# Load the NetCDF file
ncfile = f'Year_{year}/year_{year}_combined.nc'  # Replace with your actual file
ds = Dataset(ncfile)
if len(year) == 1:
        year = '200' + year  # Ensure year is two digits (e.g., '2006' for Year 6)
else:
        year = '20' + year # Ensure year is two digits (e.g., '2023' for Year 23)

# Extract variables
lon = ds.variables['lon'][:]
lat = ds.variables['lat'][:]
un = ds.variables['un'][:]  # shape: (time, lat, lon)
vn = ds.variables['vn'][:]
pn = ds.variables['pn'][:]

for time_idx in range(364):
    if time_idx <= 30:
        month = 'Jan'
        day = f"{time_idx+1:02d}"  # Format day as 01, 02, ..., 31
    elif time_idx <= 59:
        month = 'Feb'
        day = f"{time_idx-30+1:02d}"  # Format day as 01, 02, ..., 28/29
    elif time_idx <= 90:
        month = 'Mar'
        day = f"{time_idx-59+1:02d}"  # Format day as 01, 02, ..., 31
    elif time_idx <= 120:
        month = 'Apr'
        day = f"{time_idx-90+1:02d}"  # Format day as 01, 02, ..., 30
    elif time_idx <= 151:
        month = 'May'
        day = f"{time_idx-120+1:02d}"  # Format day as 01, 02, ..., 31               
    elif time_idx <= 181:
        month = 'Jun'
        day = f"{time_idx-151+1:02d}"  # Format day as 01, 02, ..., 30
    elif time_idx <= 212:
        month = 'Jul'
        day = f"{time_idx-181+1:02d}"  # Format day as 01, 02, ..., 31
    elif time_idx <= 242:
        month = 'Aug'
        day = f"{time_idx-212+1:02d}"  # Format day as 01, 02, ..., 31
    elif time_idx <= 273:
        month = 'Sep'
        day = f"{time_idx-242+1:02d}"  # Format day as 01, 02, ..., 30
    elif time_idx <= 303:
        month = 'Oct'
        day = f"{time_idx-273+1:02d}"  # Format day as 01, 02, ..., 31
    elif time_idx <= 334:
        month = 'Nov'
        day = f"{time_idx-303+1:02d}"  # Format day as 01, 02, ..., 30
    else:
        month = 'Dec'
        day = f"{time_idx-334+1:02d}"  # Format day as 01, 02, ..., 31
            
    date = f"{time_idx+1:03d}"  # Format day as 001, 002, ..., 365
    # Choose the time index to plot (e.g., first time slice)
    U = un[time_idx, :, :]
    V = vn[time_idx, :, :]
    P = pn[time_idx, :, :]

    # Mask fill values (Ferret uses 9.969e+36 as missing)
    fill_value = 9.969e+36
    # Mask fill values (Ferret uses 9.969e+36 as missing)
    U = np.ma.masked_where(U >= 1e+30, U)
    V = np.ma.masked_where(V >= 1e+30, V)
    P = np.ma.masked_where(P >= 1e+30, P)

    # Mask values outside 1 and 99 percentiles
    def mask_percentile(arr):
        valid = arr.compressed()
        p1, p99 = np.percentile(valid, 1), np.percentile(valid, 99)
        return np.ma.masked_outside(arr, p1, p99)

    P = P / 980  # Convert pressure to hPa
    U = U / 10  # Convert wind speed to dm/s
    V = V / 10  # Convert wind speed to dm/s
    # Create meshgrid for plotting
    U = mask_percentile(U)
    V = mask_percentile(V)
    P = mask_percentile(P)
    LON, LAT = np.meshgrid(lon, lat)
    
    # Adding a reference text for constant vector magnitude
    scale_val = 100
    constant_magnitude = scale_val / 5  # Adjust divisor as needed for your reference

    # Plot
    plt.figure(figsize=(10, 8))
    cmap = plt.get_cmap('RdBu_r')  # Choose a colormap
    pc = plt.pcolormesh(LON, LAT, P, cmap=cmap, shading='auto', vmin=-30, vmax=30)
    plt.colorbar(pc, label='pn')

    # Quiver (vector field)
    # To avoid clutter, plot every Nth arrow
    step = 8
    plt.quiver(LON[::step, ::step], LAT[::step, ::step], U[::step, ::step], V[::step, ::step], 
            scale=scale_val, color='k', width=0.002, headwidth=3)
    # Add the reference text at the bottom of the image
    plt.text(0.5, 0.02, f'Constant vector magnitude reference: {constant_magnitude:.1f} cm/s', 
         ha='center', va='center', transform=plt.gcf().transFigure, fontsize=10, color='black')
    
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('{} - {} - {}'.format(day,month,year))
    plt.tight_layout()
    plt.savefig(f'daily_sat_plots/Year_{year}_day_{date}.png', dpi=200)
    plt.close()
    print(f"Year {year} : day {date}.")
