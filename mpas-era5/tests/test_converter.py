import pytest
import xarray as xr
import numpy as np
import pandas as pd
import os
from src.converter import Converter

# Mock Regridder
class MockRegridder:
    def __init__(self, map_file):
        pass
        
    def regrid(self, da):
        # Return a dummy DataArray with lat/lon dims
        # Input has (Time, nCells) or (nCells)
        # Output should have (Time, lat, lon)
        
        dims = list(da.dims)
        if 'nCells' in dims:
            dims.remove('nCells')
        
        dims = dims + ['latitude', 'longitude']
        
        # Create dummy shape
        shape = [da.sizes[d] for d in dims if d in da.dims] + [2, 2] # 2x2 lat/lon
        
        # Handle case where da.dims doesn't match shape construction exactly due to remove
        # Simpler: just use the input values mean or something
        
        coords = {d: da.coords[d] for d in dims if d in da.coords}
        coords['latitude'] = [0, 1]
        coords['longitude'] = [0, 1]
        
        return xr.DataArray(np.zeros(shape), dims=dims, coords=coords)

@pytest.fixture
def mock_regridder(monkeypatch):
    monkeypatch.setattr("src.converter.Regridder", MockRegridder)

def test_converter_process(tmp_path, mock_regridder):
    # Create dummy MPAS input
    input_path = tmp_path / "mpas_in.nc"
    ds = xr.Dataset(
        {
            'mslp': (('Time', 'nCells'), np.random.rand(1, 10)),
            't2m': (('Time', 'nCells'), np.random.rand(1, 10)),
            'xtime': (('Time',), np.array([b'2021-01-01_00:00:00   ']))
        },
        coords={'Time': [0]}
    )
    ds.to_netcdf(input_path)
    
    output_dir = tmp_path / "output"
    os.makedirs(output_dir)
    
    converter = Converter("dummy_map.nc", str(output_dir))
    out_path = converter.process_file(str(input_path), output_format='netcdf')
    
    assert os.path.exists(out_path)
    ds_out = xr.open_dataset(out_path)
    assert 'SP' in ds_out
    assert 't2m' in ds_out
    assert ds_out.dims['latitude'] == 2
    assert ds_out.dims['longitude'] == 2
    assert 'time' in ds_out.dims
    assert 'forecast' in ds_out.dims
    assert ds_out['SP'].dims == ('time', 'forecast', 'latitude', 'longitude')

def test_forecast_dimension_standardization(tmp_path, mock_regridder):
    """
    Test that processing multiple files with different absolute times 
    results in consistent 'forecast' integer coordinates (0, 1, 2...)
    so that they can be combined without expanding the forecast dimension.
    """
    output_dir = tmp_path / "output_combine"
    os.makedirs(output_dir)
    converter = Converter("dummy_map.nc", str(output_dir))
    
    files = []
    # Create 2 files with different absolute times
    # File 1: starts at 00:00
    p1 = tmp_path / "f1.nc"
    xr.Dataset(
        {
            'mslp': (('Time', 'nCells'), np.random.rand(5, 10)),
            'xtime': (('Time',), np.array([b'2021-01-01_00:00:00   '] * 5)) # Simplified time for mock
        },
        coords={'Time': np.arange(5)}
    ).to_netcdf(p1)
    files.append(p1)
    
    # File 2: starts at 06:00
    p2 = tmp_path / "f2.nc"
    xr.Dataset(
        {
            'mslp': (('Time', 'nCells'), np.random.rand(5, 10)),
            'xtime': (('Time',), np.array([b'2021-01-01_06:00:00   '] * 5))
        },
        coords={'Time': np.arange(5) + 100} # Different raw time coords if they were used
    ).to_netcdf(p2)
    files.append(p2)
    
    zarr_paths = []
    for f in files:
        zarr_paths.append(converter.process_file(str(f), output_format='zarr'))
        
    # Open both and check forecast coords
    ds1 = xr.open_zarr(zarr_paths[0])
    ds2 = xr.open_zarr(zarr_paths[1])
    
    np.testing.assert_array_equal(ds1.forecast.values, ds2.forecast.values, 
                                  err_msg="Forecast coordinates should be identical integers")
    
    # Try combining logic (mocking what main.py does)
    combined = xr.open_mfdataset(zarr_paths, engine='zarr', combine='nested', concat_dim='time')
    
    assert combined.dims['forecast'] == 5, f"Forecast dimension should remain 5, got {combined.dims['forecast']}"
    assert combined.dims['forecast'] == 5, f"Forecast dimension should remain 5, got {combined.dims['forecast']}"
    assert combined.dims['time'] == 2
    
    # Verify that we preserved the years and didn't default to 1970
    times = pd.to_datetime(combined.time.values)
    assert (times.year == 2021).all(), f"Years should be 2021, got {times.year}"

