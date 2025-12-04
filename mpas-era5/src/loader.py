import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime

def parse_mpas_time(time_bytes):
    """Parses MPAS xtime character array to datetime objects."""
    # MPAS xtime is often bytes, e.g., b'2021-01-01_00:00:00   '
    time_str = time_bytes.decode('utf-8').strip()
    return datetime.strptime(time_str, '%Y-%m-%d_%H:%M:%S')

def load_mpas_dataset(file_path):
    """
    Loads an MPAS NetCDF file and standardizes time and dimensions.
    """
    ds = xr.open_dataset(file_path)
    
    # Parse time if it exists and is a character array
    if 'xtime' in ds:
        # xtime is (Time, StrLen) char array
        # We need to convert it to a pandas datetime index
        # Stack the char array to strings
        try:
            # This works if xtime is read as bytes
            times = [parse_mpas_time(t) for t in ds['xtime'].values.astype('S64')]
            ds = ds.assign_coords(Time=pd.DatetimeIndex(times))
        except Exception as e:
            print(f"Warning: Could not parse xtime: {e}")
            
    return ds
