import sys
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os
import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature

dict_data = {}

def generate_season_wise_plots_updated(year):
    print(f"Processing data for Year: {year}")
    ncfile = f'Year_{year}/year_{year}_combined.nc'
    print(f"Reading NetCDF file: {ncfile}")
    ds = Dataset(ncfile)
    if len(year) == 1:
        year_full = '200' + year
    else:
        year_full = '20' + year
    dict_data[year_full] = {}

    lon = ds.variables['lon'][:]
    lat = ds.variables['lat'][:]
    un = ds.variables['un'][:]
    vn = ds.variables['vn'][:]

    # Find indices for the region: 5N–30N, 75E–100E
    lat_mask = (lat >= 5) & (lat <= 30)
    lon_mask = (lon >= 75) & (lon <= 100)
    lat_indices = np.where(lat_mask)[0]
    lon_indices = np.where(lon_mask)[0]

    # Subset the lat/lon arrays
    lat_sub = lat[lat_indices]
    lon_sub = lon[lon_indices]

    # Define seasons with day indices
    seasons = {
        'Winter': list(range(334, 365)) + list(range(0, 31)) + list(range(31, 60)),
        'Summer': list(range(60, 91)) + list(range(91, 121)) + list(range(121, 152)),
        'Spring': list(range(152, 182)) + list(range(182, 213)) + list(range(213, 243)),
        'Autumn': list(range(243, 274)) + list(range(274, 304)) + list(range(304, 334))
    }

    for season, days in seasons.items():
        output_dir = f'Image_output/{season}'
        os.makedirs(output_dir, exist_ok=True)
        dict_data[year_full][season] = {}

        # Stack all U and V for this season, then average
        U_stack = []
        V_stack = []
        for time_idx in days:
            U = un[time_idx, :, :]
            V = vn[time_idx, :, :]
            # Subset to region
            U = U[np.ix_(lat_indices, lon_indices)]
            V = V[np.ix_(lat_indices, lon_indices)]
            U = np.ma.masked_where(U >= 1e+30, U)
            V = np.ma.masked_where(V >= 1e+30, V)
            U = U / 100  # convert to dm/s
            V = V / 100
            U_stack.append(U)
            V_stack.append(V)

        U_season = np.ma.mean(np.ma.stack(U_stack), axis=0)
        V_season = np.ma.mean(np.ma.stack(V_stack), axis=0)

        # Mask invalid values before magnitude calculation to avoid warnings
        U_season = np.ma.masked_invalid(U_season)
        V_season = np.ma.masked_invalid(V_season)

        magnitude = np.ma.sqrt(U_season**2 + V_season**2) * np.sign(U_season) * np.sign(V_season)
        # No multiplication! Plot as is.

        # Print min and max magnitude (ignoring masked values)
        min_mag = float(magnitude.min())
        max_mag = float(magnitude.max())
        dict_data[year_full][season]['min_magnitude'] = min_mag
        dict_data[year_full][season]['max_magnitude'] = max_mag
        print(f"Season: {season}, Min Magnitude: {min_mag:.4f}, Max Magnitude: {max_mag:.4f}")

        # Prepare custom colormap with over/under colors for out-of-bounds
        cmap = plt.get_cmap('RdBu_r').copy()
        light_grey = '#D3D3D3'
        cmap.set_over(light_grey)
        cmap.set_under(light_grey)

        LON, LAT = np.meshgrid(lon_sub, lat_sub)
        scale_val = 30

        plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        pc = ax.pcolormesh(LON, LAT, magnitude, cmap=cmap, shading='gouraud',
                           vmin=-0.3, vmax=0.3, transform=ccrs.PlateCarree())
        plt.colorbar(pc, label='Wind Vector Magnitude (cm/s)', extend='both', ax=ax)
        step = 8
        ax.quiver(LON[::step, ::step], LAT[::step, ::step], U_season[::step, ::step], V_season[::step, ::step], 
                  scale=scale_val, color='k', width=0.002, headwidth=3, transform=ccrs.PlateCarree())
        # Add bold landlines and coastlines with white landmass
        ax.add_feature(cfeature.LAND, facecolor='white', edgecolor='black', linewidth=1.5)
        ax.coastlines(linewidth=1.5)
        # Set extent to Bay of Bengal region
        ax.set_extent([75, 100, 5, 30], crs=ccrs.PlateCarree())

        # Add gridlines with labels
        gl = ax.gridlines(draw_labels=True, linewidth=1.2, color='gray', alpha=0.7, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 12, 'weight': 'bold'}
        gl.ylabel_style = {'size': 12, 'weight': 'bold'}

        # Add note about the color mapping and scaling
        '''plt.text(0.5, 0.02, 
            'Magnitude plotted between 0–0.3 cm/s;\n'
            'Values outside (0,0.3) are shown as light grey.\n',
            ha='center', va='center', transform=plt.gcf().transFigure, fontsize=10, color='black', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        '''
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title(f'Satellite : {season} {year_full} (Bay of Bengal)', fontsize=14)
        plt.tight_layout()

        filename = f'{output_dir}/{season}-{year_full}.png'
        plt.savefig(filename, dpi=200)
        plt.close()
        print(f"Saved plot: {filename}")
    
    ds.close()
    print(f"Closed dataset for Year: {year_full}")

if __name__ == '__main__':
    for year in range(11, 23):
        generate_season_wise_plots_updated(str(year))
        print(f"Completed processing for Year: 20{year:02d}")
    """if len(sys.argv) > 1:
        year_arg = sys.argv[1]
    else:
        year_arg = '8'  # Default year if not provided
    generate_season_wise_plots_updated(year_arg)
    print("All plots generated successfully.")"""
    # Print average and variation for each year's seasons
    # Collect stats for each season across all years
    season_stats = {}
    for year, seasons in dict_data.items():
        for season, stats in seasons.items():
            if season not in season_stats:
                season_stats[season] = {'min': [], 'max': [], 'years': []}
            season_stats[season]['min'].append(stats['min_magnitude'])
            season_stats[season]['max'].append(stats['max_magnitude'])
            season_stats[season]['years'].append(year)

    # Calculate averages and deviations
    output_lines = []
    for season, vals in season_stats.items():
        min_arr = np.array(vals['min'])
        max_arr = np.array(vals['max'])
        avg_min = np.mean(min_arr)
        avg_max = np.mean(max_arr)
        dev_min = min_arr - avg_min
        dev_max = max_arr - avg_max
        output_lines.append(f"\nSeason: {season}")
        output_lines.append(f"  Average Min Magnitude: {avg_min:.4f}")
        output_lines.append(f"  Average Max Magnitude: {avg_max:.4f}")
        output_lines.append("  Year-wise deviations:")
        for i, year in enumerate(vals['years']):
            output_lines.append(f"    Year: {year} | Min: {min_arr[i]:.4f} (dev: {dev_min[i]:+.4f}), Max: {max_arr[i]:.4f} (dev: {dev_max[i]:+.4f})")

    # Print to console
    for line in output_lines:
        print(line)

    # Write to file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"variation_log_{timestamp}.txt"
    with open(log_filename, "w") as f:
        for line in output_lines:
            f.write(line + "\n")
    print(f"\nVariation log written to: {log_filename}")
