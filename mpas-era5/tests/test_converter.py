import pytest
import xarray as xr
import numpy as np
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
