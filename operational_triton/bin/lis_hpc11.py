import sys
import pygrib
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from osgeo import gdal, osr
import os

def list_bands(grbs):
    print("Available bands in the GRIB file:")
    for i, grb in enumerate(grbs, start=1):
        print(f"Index {i}: {grb.name} - {grb.typeOfLevel} {grb.level}")

def process_grib(file_path, output_dir, output_filename, band_index):
    try:
        grbs = pygrib.open(file_path)
        list_bands(grbs)

        band_index = int(band_index) - 1
        grb = grbs[band_index]

        data = grb.values
        lat, lon = grb.latlons()
        print(f"Data stats - Min: {data.min()}, Max: {data.max()}, Mean: {data.mean()}")  # Data statistics

        # Plotting the data without coastline data
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_global()
        contour = plt.contourf(lon, lat, data, 60, transform=ccrs.PlateCarree())
        plt.colorbar(contour, ax=ax, orientation='vertical')
        plt.title(f'{grb.name} - {grb.typeOfLevel} {grb.level}\n{os.path.basename(file_path)}')
        
        # Save the plot to a file
        plot_file_path = os.path.join(output_dir, f"{output_filename}_band_{band_index + 1}_plot.png")
        plt.savefig(plot_file_path)
        plt.close(fig)
        print(f"Plot saved: {plot_file_path}")

        # Save data as GeoTIFF
        driver = gdal.GetDriverByName('GTiff')
        dataset = driver.Create(
            os.path.join(output_dir, f"{output_filename}_band_{band_index + 1}.tif"),
            lon.shape[1], lat.shape[0], 1, gdal.GDT_Float32)
        dataset.SetGeoTransform([lon.min(), grb.Di, 0, lat.max(), 0, -grb.Dj])
        
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        dataset.SetProjection(srs.ExportToWkt())

        dataset.GetRasterBand(1).WriteArray(data)
        dataset.FlushCache()  # Write to disk
        print(f"Written: {os.path.join(output_dir, f'{output_filename}_band_{band_index + 1}.tif')}")

        grbs.close()

    except (ValueError, IndexError) as e:
        print(f"Error: {str(e)}. Please check the band index and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <list_of_files> <base_directory> <output_directory> <band_index>")
    else:
        list_of_files = sys.argv[1]
        base_directory = sys.argv[2]
        output_dir = sys.argv[3]
        band_index = sys.argv[4]

        with open(list_of_files, 'r') as file:
            for line in file:
                relative_path = line.strip()
                file_path = os.path.join(base_directory, relative_path)
                grib_file_name = os.path.basename(file_path)
                output_filename = os.path.splitext(grib_file_name)[0]
                process_grib(file_path, output_dir, output_filename, band_index)
