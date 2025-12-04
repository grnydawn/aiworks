import xarray as xr
import numpy as np
import scipy.sparse as sp

class Regridder:
    def __init__(self, map_file_path):
        """
        Initializes the regridder with a mapping file.
        
        Args:
            map_file_path (str): Path to the NetCDF mapping file.
        """
        self.map_ds = xr.open_dataset(map_file_path)
        self._init_weights()
        
    def _init_weights(self):
        """Reads weights and creates a sparse matrix."""
        # Load mapping data
        # ESMF weights are typically 1-based indices, so we subtract 1 for Python (0-based)
        row = self.map_ds['row'].values - 1
        col = self.map_ds['col'].values - 1
        s = self.map_ds['S'].values
        
        n_a = self.map_ds.dims['n_a'] # Source size (MPAS nCells)
        n_b = self.map_ds.dims['n_b'] # Dest size (ERA5 lat*lon)
        
        # Create sparse matrix: (n_b, n_a)
        # We want to map FROM source TO dest, so Dest = Weights * Source
        self.weights = sp.csr_matrix((s, (row, col)), shape=(n_b, n_a))
        
        # Default shape
        self.dst_shape = (720, 1440)
        
        # Try to get from dimensions
        if 'dst_grid_dims' in self.map_ds.dims:
             self.dst_shape = (self.map_ds.dims['dst_grid_dims'][0], self.map_ds.dims['dst_grid_dims'][1])
        # Try to get from variable (ESMF standard)
        elif 'dst_grid_dims' in self.map_ds:
             dims = self.map_ds['dst_grid_dims'].values
             self.dst_shape = (dims[1], dims[0]) # ESMF is usually [lon, lat] or [lat, lon]. 
             # ncdump_map.txt shows dst_grid_dims(dst_grid_rank). 
             # If it's [1440, 720], we want (720, 1440).
             # Let's assume the values are [nx, ny] or [ny, nx].
             # If n_b = 1036800 (720*1440), and dims are [1440, 720], then dims[1]=720, dims[0]=1440.
             # We want (lat, lon) = (720, 1440).
             # So if dims[0]*dims[1] == n_b, we can try to guess or just trust the order.
             # Usually ESMF writes [lon_size, lat_size].
             if dims[0] * dims[1] == n_b:
                 # Heuristic: if one is 720 and other 1440
                 if dims[1] == 720:
                     self.dst_shape = (720, 1440)
                 else:
                     self.dst_shape = (dims[1], dims[0])
        # Try to get from attributes (Test case)
        elif 'dst_grid_dims' in self.map_ds.attrs:
             dims = self.map_ds.attrs['dst_grid_dims']
             self.dst_shape = (dims[0], dims[1])

    def regrid(self, data_array):
        """
        Regrids a DataArray from MPAS to ERA5 grid.
        
        Args:
            data_array (xr.DataArray): Input data with dimension (..., nCells)
            
        Returns:
            xr.DataArray: Regridded data with dimensions (..., lat, lon)
        """
        # Ensure the last dimension is nCells
        if data_array.dims[-1] != 'nCells':
            raise ValueError("Last dimension of input data must be 'nCells'")
            
        # Flatten input data to (N, nCells) where N is product of other dims
        input_data = data_array.values
        original_shape = input_data.shape
        n_cells = original_shape[-1]
        
        if n_cells != self.weights.shape[1]:
             raise ValueError(f"Input nCells ({n_cells}) does not match mapping source size ({self.weights.shape[1]})")

        # Reshape to 2D for matrix multiplication: (Samples, nCells)
        input_flat = input_data.reshape(-1, n_cells)
        
        # Apply weights: (Samples, n_b) = (Samples, n_a) * (n_a, n_b)^T 
        # Or rather: Output = Weights * Input^T ? 
        # Weights is (n_b, n_a). Input is (Samples, n_a).
        # We want (Samples, n_b).
        # So: (Weights * Input.T).T -> (n_b, Samples).T -> (Samples, n_b)
        # Or: Input * Weights.T -> (Samples, n_a) * (n_a, n_b) -> (Samples, n_b)
        
        output_flat = self.weights.dot(input_flat.T).T
        
        # Reshape back to original dimensions + lat, lon
        new_shape = original_shape[:-1] + self.dst_shape
        output_data = output_flat.reshape(new_shape)
        
        # Create new coordinates
        # We might want to attach lat/lon coords from the mapping file if available
        # For now, returning a DataArray with generic dims or copying coords if possible
        
        coords = {k: v for k, v in data_array.coords.items() if 'nCells' not in v.dims}
        
        # Add lat/lon coords if we can extract them from map file or generate them
        # The map file has yc_b (lat) and xc_b (lon) as 1D arrays of size n_b
        # We can reshape them to (lat, lon)
        
        lat_1d = self.map_ds['yc_b'].values
        lon_1d = self.map_ds['xc_b'].values
        
        # Assuming row-major ordering for the grid
        lat = lat_1d.reshape(self.dst_shape)[:, 0]
        lon = lon_1d.reshape(self.dst_shape)[0, :]
        
        coords['latitude'] = lat
        coords['longitude'] = lon
        
        dims = list(data_array.dims[:-1]) + ['latitude', 'longitude']
        
        return xr.DataArray(output_data, coords=coords, dims=dims, name=data_array.name)
