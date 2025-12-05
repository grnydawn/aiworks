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
        
        # We keep all time steps as 'forecast' steps
        # The 'time' dimension will be the initialization time (first step)
        
        # ... (rest of logic is same until save) ...
        
        # Define mappings and derivations
        # ...
        
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
        levels = [50, 100, 200, 250, 500, 700, 850, 925]
        
        for var_name, mpas_prefix, is_derived_q in [
            ('U', 'uzonal', False),
            ('V', 'umeridional', False),
            ('T', 'temperature', False),
            ('Q', 'relhum', True) 
        ]:
            var_levels = []
            valid_levels = []
            
            for lvl in levels:
                mpas_var = f"{mpas_prefix}_{lvl}hPa"
                if mpas_var in ds:
                    regridded = self.regridder.regrid(ds[mpas_var])
                    
                    if is_derived_q:
                        t_var = f"temperature_{lvl}hPa"
                        if t_var in ds:
                            t_regridded = self.regridder.regrid(ds[t_var])
                            regridded = calculate_specific_humidity(regridded, t_regridded, lvl * 100.0)
                        else:
                            continue
                            
                    var_levels.append(regridded)
                    valid_levels.append(lvl)
            
            if var_levels:
                combined = xr.concat(var_levels, dim='level')
                combined = combined.assign_coords(level=valid_levels)
                out_ds[var_name] = combined

        # Handle Dimensions: (time, forecast, level, latitude, longitude)
        
        # 1. Rename 'Time' (from MPAS) to 'forecast'
        if 'Time' in out_ds.dims:
            # Standardize Time to integer steps (0, 1, 2, ...) to ensure alignment across files
            # This prevents dimension expansion when combining multiple files with different absolute times
            out_ds = out_ds.assign_coords(Time=np.arange(out_ds.sizes['Time']))
            out_ds = out_ds.rename({'Time': 'forecast'})
            
        # 2. Add 'time' dimension (Initialization time)
        # We take the first time value as the initialization time
        if 'forecast' in out_ds.dims:
            init_time = out_ds.forecast.values[0]
            out_ds = out_ds.expand_dims(time=[init_time])
            
        # 3. Transpose dimensions
        # 3D Variables: (time, forecast, level, latitude, longitude)
        # 2D Variables: (time, forecast, latitude, longitude)
        
        for var in out_ds.data_vars:
            dims = out_ds[var].dims
            if 'level' in dims:
                out_ds[var] = out_ds[var].transpose('time', 'forecast', 'level', 'latitude', 'longitude')
            else:
                out_ds[var] = out_ds[var].transpose('time', 'forecast', 'latitude', 'longitude')

        # Save
        time_str = pd.to_datetime(init_time).strftime('%Y%m%d%H')
        
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
