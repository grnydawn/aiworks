import pytest
import xarray as xr
import numpy as np
import scipy.sparse as sp
import os
from src.regridder import Regridder

def test_regridder_init(tmp_path):
    # Create a mock mapping file
    map_path = tmp_path / "map.nc"
    
    # 2 source cells, 2 dest cells
    # Identity mapping: 1->1, 2->2
    # ESMF is 1-based
    row = np.array([1, 2]) 
    col = np.array([1, 2])
    s = np.array([1.0, 1.0])
    
    ds = xr.Dataset(
        {
            'row': (('n_s',), row),
            'col': (('n_s',), col),
            'S': (('n_s',), s),
            'yc_b': (('n_b',), [0.0, 1.0]), # lat
            'xc_b': (('n_b',), [0.0, 1.0]), # lon
        },
        coords={},
        attrs={'dst_grid_dims': [1, 2]} # 1 lat, 2 lon
    )
    # Dimensions
    ds = ds.assign_coords(n_a=np.arange(2), n_b=np.arange(2))
    ds.to_netcdf(map_path)
    
    regridder = Regridder(str(map_path))
    
    assert regridder.weights.shape == (2, 2)
    assert regridder.weights[0, 0] == 1.0
    assert regridder.weights[1, 1] == 1.0

def test_regridder_regrid(tmp_path):
    # Create a mock mapping file
    map_path = tmp_path / "map.nc"
    
    # Source: 4 cells. Dest: 2x2 = 4 cells.
    # Mapping: Reverse order. 1->4, 2->3, 3->2, 4->1
    row = np.array([4, 3, 2, 1]) 
    col = np.array([1, 2, 3, 4])
    s = np.array([1.0, 1.0, 1.0, 1.0])
    
    ds = xr.Dataset(
        {
            'row': (('n_s',), row),
            'col': (('n_s',), col),
            'S': (('n_s',), s),
            'yc_b': (('n_b',), [10, 10, 20, 20]), 
            'xc_b': (('n_b',), [1, 2, 1, 2]), 
        },
        attrs={'dst_grid_dims': [2, 2]} # 2 lat, 2 lon
    )
    # Add n_a and n_b dims
    ds = ds.assign_coords(n_a=np.arange(4), n_b=np.arange(4))
    ds.to_netcdf(map_path)
    
    regridder = Regridder(str(map_path))
    
    # Create input data: (Time=1, nCells=4)
    data = xr.DataArray(
        np.array([[10.0, 20.0, 30.0, 40.0]]),
        dims=('Time', 'nCells'),
        coords={'Time': [0]}
    )
    
    result = regridder.regrid(data)
    
    # Expected output: 
    # Dest cell 1 (row 1) gets Source cell 4 (col 4) -> 40.0
    # Dest cell 2 (row 2) gets Source cell 3 (col 3) -> 30.0
    # ...
    # Result shape should be (1, 2, 2)
    
    assert result.shape == (1, 2, 2)
    # Check values. Flattened result should be [40, 30, 20, 10]
    expected = np.array([[[40.0, 30.0], [20.0, 10.0]]])
    np.testing.assert_array_equal(result.values, expected)
