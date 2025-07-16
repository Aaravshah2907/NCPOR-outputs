import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import sys
month_day_dict = {
    1: 'jan', 31: 'feb', 61: 'mar', 91: 'apr', 121: 'may', 151: 'jun',
    181: 'jul', 211: 'aug', 241: 'sep', 271: 'oct', 301: 'nov', 331: 'dec'
}

year = int(sys.argv[1]) if len(sys.argv) > 1 else 3
# Load the NetCDF file
ncfile = f'Year_{year}/year_{year}_combined.nc'  # Replace with your actual file
ds = Dataset(ncfile)

# Extract variables
lon = ds.variables['lon'][:]
lat = ds.variables['lat'][:]
un = ds.variables['un'][:]  # shape: (time, lat, lon)
vn = ds.variables['vn'][:]
pn = ds.variables['pn'][:]

# Prompt user for time range
day_init_min = 1
day_final_max = 364

def generate_plots(day_init, day_final):
    # Ensure valid indices
    if day_init < 0 or day_final >= un.shape[0] or day_init > day_final:
        raise ValueError("Invalid day indices. Please check the input values.")

    # Average over the specified time range (inclusive)
    U = np.mean(un[day_init:day_final+1, :, :], axis=0)
    V = np.mean(vn[day_init:day_final+1, :, :], axis=0)
    P = np.mean(pn[day_init:day_final+1, :, :], axis=0)

    # Mask fill values (Ferret uses 9.969e+36 as missing)
    fill_value = 9.969e+36
    U = np.ma.masked_where(U >= 1e+30, U)
    V = np.ma.masked_where(V >= 1e+30, V)
    P = np.ma.masked_where(P >= 1e+30, P)
    
    U = U / 10  # Convert wind speed to dm/s
    V = V / 10  # Convert wind speed to dm/s
    P = P / 980  # Convert pressure to hPa

    # Create meshgrid for plotting
    LON, LAT = np.meshgrid(lon, lat)
    
    # Calculate magnitude and filter extremes
    magnitude = np.sqrt(U**2 + V**2)
    q95 = np.percentile(magnitude.compressed(), 95)

    # Create mask for reasonable vectors
    reasonable_mask = magnitude < q95

    # Apply mask to coordinates and vectors
    LON_filtered = np.where(reasonable_mask, LON, np.nan)
    LAT_filtered = np.where(reasonable_mask, LAT, np.nan)
    U_filtered = np.where(reasonable_mask, U, np.nan)
    V_filtered = np.where(reasonable_mask, V, np.nan)

    # Plot
    plt.figure(figsize=(10, 8))
    cmap = plt.get_cmap('RdBu_r')  # Choose a colormap
    # Some alternative color maps you can use:
    # 'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 
    # 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Grays', 'Grays_r', 
    # 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 
    # 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 
    # 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 
    # 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 
    # 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 
    # 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 
    # 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 
    # 'autumn', 'autumn_r', 'berlin', 'berlin_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 
    # 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 
    # 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 
    # 'gist_gray', 'gist_gray_r', 'gist_grey', 'gist_grey_r', 'gist_heat', 'gist_heat_r', 'gist_ncar', 
    # 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 
    # 'gist_yarg_r', 'gist_yerg', 'gist_yerg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 
    # 'gray', 'gray_r', 'grey', 'grey_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 
    # 'jet', 'jet_r', 'magma', 'magma_r', 'managua', 'managua_r', 'nipy_spectral', 'nipy_spectral_r', 
    # 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 
    # 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 
    # 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 
    # 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r', 'twilight_shifted', 
    # 'twilight_shifted_r', 'vanimo', 'vanimo_r', 'viridis', 'viridis_r', 'winter', 'winter_r'
    pc = plt.pcolormesh(LON, LAT, P, cmap=cmap, shading='nearest', vmin=-20, vmax=20)
    # To use another, just change 'viridis' to your preferred colormap name.
    plt.colorbar(pc, label='pn')

    # Quiver (vector field)
    # To avoid clutter, plot every Nth arrow
    step = 8
    plt.quiver(LON_filtered[::step, ::step], LAT_filtered[::step, ::step], 
            U_filtered[::step, ::step], V_filtered[::step, ::step], 
            scale=50, color='k', width=0.002, headwidth=3)

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Year {}: (Averaged from index {} to {})'.format(year, day_init, day_final))
    plt.tight_layout()
    month = month_day_dict.get(day_init, 'dec')
    plt.savefig(f'year-{year}-{month}-wind_clim.png', dpi=200)
    plt.close()  # Close the plot to free memory

def main_loop():
    for day_init in range(day_init_min, day_final_max + 1,30):
        day_final = day_init + 29
        if day_final > day_final_max or day_init == 331:
            day_final = day_final_max
        if day_init == 361:
            continue
        print(f"Year {year}: Generating plot for days {day_init} to {day_final}...")
        generate_plots(day_init, day_final)
        
if __name__ == "__main__":
    main_loop()
    print(f"Year {year}: All plots generated successfully.")