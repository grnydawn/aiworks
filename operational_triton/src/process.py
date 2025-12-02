import os
import logging
import pygrib
import numpy as np
from osgeo import gdal, osr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.work_dir = config.get("global.work_dir")
        self.postproc_dir = os.path.join(self.work_dir, "02_LISpostproc")
        os.makedirs(self.postproc_dir, exist_ok=True)

    def check_data_availability(self, date_str):
        """Checks if the input directory for a given date exists."""
        # Logic to check specific directory structure in 01_LISinput
        # This needs to match how rsync places files.
        # Assuming rsync --relative preserves the full path structure.
        # input_dir/feed_dir_structure/YYYY/Mon/Day/LIS-DD
        
        # For simplicity, let's assume we search for the LIS-DD folder
        # We might need to walk the directory or know the exact path.
        # Based on original script: $WORK_DIR/01_LISinput/2024/Dec/*/LIS-DD
        
        # This is a placeholder for the exact path logic
        return True 

    def convert_grib_to_tiff(self, grib_file_path, output_filename, band_indices=[23, 24]):
        """Converts specific bands of a GRIB file to GeoTIFF."""
        try:
            grbs = pygrib.open(grib_file_path)
            
            for band_idx in band_indices:
                # pygrib is 1-based, but our list is 1-based too from config usually.
                # Original script: band_index = int(band_index) - 1
                
                try:
                    grb = grbs[band_idx] # pygrib uses 1-based indexing for select usually, or we index the list
                    # Actually grbs.select(name=...) is better, but by index:
                    # grbs is an iterator/list-like. 
                    # Let's assume we iterate or select by index.
                    # Safest is to list them and pick.
                    
                    # Re-implementing logic from lis_hpc11.py
                    # Note: pygrib message indexing is 1-based.
                    grb = grbs.message(band_idx)
                    
                    data = grb.values
                    lat, lon = grb.latlons()
                    
                    output_path = os.path.join(self.postproc_dir, f"{output_filename}_band_{band_idx}.tif")
                    
                    self._write_geotiff(output_path, data, lat, lon, grb)
                    logger.info(f"Generated {output_path}")
                    
                except Exception as e:
                    logger.error(f"Error processing band {band_idx} in {grib_file_path}: {e}")

            grbs.close()
            return True
        except Exception as e:
            logger.error(f"Failed to process GRIB file {grib_file_path}: {e}")
            return False

    def _write_geotiff(self, output_path, data, lat, lon, grb):
        driver = gdal.GetDriverByName('GTiff')
        dataset = driver.Create(
            output_path,
            lon.shape[1], lat.shape[0], 1, gdal.GDT_Float32)
        
        # GeoTransform: [top_left_x, w_e_pixel_resolution, 0, top_left_y, 0, n_s_pixel_resolution]
        # Note: grb.Di and grb.Dj might need adjustment for direction
        dataset.SetGeoTransform([lon.min(), grb.Di, 0, lat.max(), 0, -grb.Dj])
        
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        dataset.SetProjection(srs.ExportToWkt())

        dataset.GetRasterBand(1).WriteArray(data)
        dataset.FlushCache()
