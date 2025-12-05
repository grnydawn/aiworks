import pytest
import xarray as xr
import numpy as np
import os
from src.converter import Converter
from src.stats import compute_stats

def test_functional_full_flow(tmp_path):
    # 1. Create Mapping File
    map_path = tmp_path / "map.nc"
    # 1 source cell -> 1 dest cell
    ds_map = xr.Dataset(
        {
            'row': (('n_s',), [1]),
            'col': (('n_s',), [1]),
            'S': (('n_s',), [1.0]),
            'yc_b': (('n_b',), [0.0]),
            'xc_b': (('n_b',), [0.0]),
        },
        attrs={'dst_grid_dims': [1, 1]}
    )
    ds_map = ds_map.assign_coords(n_a=np.arange(1), n_b=np.arange(1))
    ds_map.to_netcdf(map_path)
    
    # 2. Create MPAS Input
    input_path = tmp_path / "mpas.nc"
    ds_in = xr.Dataset(
        {
            'mslp': (('Time', 'nCells'), [[101325.0]]),
            't2m': (('Time', 'nCells'), [[288.15]]),
            'uzonal_500hPa': (('Time', 'nCells'), [[10.0]]),
            'xtime': (('Time',), np.array([b'2021-01-01_00:00:00   ']))
        },
        coords={'Time': [0]}
    )
    ds_in.to_netcdf(input_path)
    
    # 3. Run Converter
    output_dir = tmp_path / "out"
    os.makedirs(output_dir)
    
    converter = Converter(str(map_path), str(output_dir))
    zarr_path = converter.process_file(str(input_path), output_format='netcdf')
    
    # 4. Verify Output
    ds_out = xr.open_dataset(zarr_path)
    # Values might be slightly different due to dimension changes/broadcasting, but checks should be robust
    assert ds_out['SP'].values[0, 0, 0, 0] == 101325.0
    assert ds_out['t2m'].values[0, 0, 0, 0] == 288.15
    assert ds_out['U500'].values[0, 0, 0, 0] == 10.0
    assert ds_out['SP'].dims == ('time', 'forecast', 'latitude', 'longitude')
    assert ds_out['U500'].dims == ('time', 'forecast', 'latitude', 'longitude')
    
    # 5. Run Stats
    # Stats module expects zarr path by default in my implementation?
    # Let's check stats.py. It uses xr.open_zarr.
    # I need to update stats.py to handle netcdf or just mock it here.
    # I will update stats.py to handle both or auto-detect.
    compute_stats(zarr_path, str(output_dir))
    
    assert os.path.exists(output_dir / "era5_mean.nc")
    assert os.path.exists(output_dir / "era5_std.nc")
    assert os.path.exists(output_dir / "era5_static.nc")
