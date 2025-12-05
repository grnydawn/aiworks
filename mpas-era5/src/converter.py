import xarray as xr
import numpy as np
import pandas as pd
import os
from .loader import load_mpas_dataset
from .regridder import Regridder

# Constants
G = 9.80665

def calculate_specific_humidity(relhum_percent, temp_k, pressure_pa):
    """
    Approximates specific humidity from relative humidity, temperature, and pressure.
    
    q = 0.622 * e / (p - 0.378 * e)
    e = es * (rh / 100)
    es = 611.2 * exp(17.67 * (T - 273.15) / (T - 29.65))  (Bolton 1980)
    """
    t_c = temp_k - 273.15
    es = 611.2 * np.exp(17.67 * t_c / (t_c + 243.5))
    e = es * (relhum_percent / 100.0)
    q = 0.622 * e / (pressure_pa - 0.378 * e)
    return q

class Converter:
    def __init__(self, map_file, output_dir):
        self.regridder = Regridder(map_file)
        self.output_dir = output_dir
        
    def process_file(self, input_file, output_format='zarr'):
        ds = load_mpas_dataset(input_file)
        
        # ... (rest of logic is same until save) ...
        
        # Define mappings and derivations
        # Target Variable -> (Source Variable, Derivation Function)
        # If Source Variable is a list, function takes multiple args
        
        # We need to handle 3D variables (on pressure levels) and 2D variables
        # MPAS file has pre-interpolated pressure levels: 50, 100, 200, 250, 500, 700, 850, 925
        
        # ERA5 typically expects separate files or variables for different levels or a 'level' dimension.
        # Based on idea.txt, we are producing "ERA5-formatted Zarr files".
        # It lists: U, V, T, Q, SP, t2m, U500, V500, T500, Z500, Q500
        
        # Let's assume we output separate variables for the single levels requested (500)
        # and maybe full profiles if U, V, T, Q implies all levels?
        # For simplicity and matching the explicit list, I will produce the specific variables listed.
        # If "U" means U on all levels, I would need to combine them. 
        # Given "U500" is listed separately, "U" might mean U on model levels? 
        # But MPAS model levels are on unstructured grid. Regridding 3D unstructured to 3D lat/lon is heavy.
        # The MPAS file provided ONLY has the interpolated pressure levels (50, 100... 925).
        # So "U" probably means "U at all available pressure levels".
        
        # Let's construct a dataset with the requested variables.
        
        out_ds = xr.Dataset()
        
        # 1. Surface Variables
        if 'mslp' in ds:
            out_ds['SP'] = self.regridder.regrid(ds['mslp'])
        
        if 't2m' in ds:
            out_ds['t2m'] = self.regridder.regrid(ds['t2m'])
            
        # 2. 500hPa Variables
        if 'uzonal_500hPa' in ds:
            out_ds['U500'] = self.regridder.regrid(ds['uzonal_500hPa'])
            
        if 'umeridional_500hPa' in ds:
            out_ds['V500'] = self.regridder.regrid(ds['umeridional_500hPa'])
            
        if 'temperature_500hPa' in ds:
            out_ds['T500'] = self.regridder.regrid(ds['temperature_500hPa'])
            
        if 'height_500hPa' in ds:
            # Z = H * g
            h500 = self.regridder.regrid(ds['height_500hPa'])
            out_ds['Z500'] = h500 * G
            
        if 'relhum_500hPa' in ds and 'temperature_500hPa' in ds:
            rh = self.regridder.regrid(ds['relhum_500hPa'])
            t = self.regridder.regrid(ds['temperature_500hPa'])
            out_ds['Q500'] = calculate_specific_humidity(rh, t, 50000.0)
            
        # 3. "U", "V", "T", "Q" (All levels)
        # We need to combine the available levels into a 'level' dimension
        levels = [50, 100, 200, 250, 500, 700, 850, 925]
        
        for var_name, mpas_prefix, is_derived_q in [
            ('U', 'uzonal', False),
            ('V', 'umeridional', False),
            ('T', 'temperature', False),
            ('Q', 'relhum', True) # Source is RH, we derive Q
        ]:
            var_levels = []
            valid_levels = []
            
            for lvl in levels:
                mpas_var = f"{mpas_prefix}_{lvl}hPa"
                if mpas_var in ds:
                    regridded = self.regridder.regrid(ds[mpas_var])
                    
                    if is_derived_q:
                        # Need T for this level
                        t_var = f"temperature_{lvl}hPa"
                        if t_var in ds:
                            t_regridded = self.regridder.regrid(ds[t_var])
                            regridded = calculate_specific_humidity(regridded, t_regridded, lvl * 100.0)
                        else:
                            continue
                            
                    var_levels.append(regridded)
                    valid_levels.append(lvl)
            
            if var_levels:
                # Concat along level dimension
                combined = xr.concat(var_levels, dim='level')
                combined = combined.assign_coords(level=valid_levels)
                
                # Ensure dimension order: (Time, level, latitude, longitude)
                # If input was (Time, nCells), regridded is (Time, lat, lon)
                # Concat adds level -> (level, Time, lat, lon) usually?
                # Let's check dims.
                if 'Time' in combined.dims:
                     combined = combined.transpose('Time', 'level', 'latitude', 'longitude')
                
                out_ds[var_name] = combined

        # Rename Time to time if present
        if 'Time' in out_ds.dims:
            out_ds = out_ds.rename({'Time': 'time'})
        
        # Ensure 2D variables are (time, latitude, longitude)
        for var in out_ds.data_vars:
            if 'level' not in out_ds[var].dims and 'time' in out_ds[var].dims:
                out_ds[var] = out_ds[var].transpose('time', 'latitude', 'longitude')

        # Save
        time_val = ds.Time.values[0] if 'Time' in ds else (out_ds.time.values[0] if 'time' in out_ds else None)
        if time_val is None:
             raise ValueError("Could not find time dimension")
             
        time_str = pd.to_datetime(time_val).strftime('%Y%m%d%H')
        
        if output_format == 'zarr':
            output_path = os.path.join(self.output_dir, f"era5_converted_{time_str}.zarr")
            out_ds.to_zarr(output_path, mode='w', consolidated=False)
        elif output_format == 'netcdf':
            output_path = os.path.join(self.output_dir, f"era5_converted_{time_str}.nc")
            out_ds.to_netcdf(output_path)
        else:
            raise ValueError(f"Unknown output format: {output_format}")
            
        print(f"Saved {output_path}")
        return output_path
