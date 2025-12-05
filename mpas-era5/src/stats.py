import xarray as xr
import numpy as np
import os

def compute_stats(input_data, output_dir):
    """
    Computes mean, std, and static files from a Zarr/NetCDF dataset or path.
    """
    if isinstance(input_data, (str, os.PathLike)):
        if input_data.endswith('.nc'):
            ds = xr.open_dataset(input_data)
        else:
            ds = xr.open_zarr(input_data)
    else:
        ds = input_data
    
    # Mean
    ds_mean = ds.mean(dim='Time')
    ds_mean.to_netcdf(os.path.join(output_dir, 'era5_mean.nc'))
    
    # Std
    ds_std = ds.std(dim='Time')
    ds_std.to_netcdf(os.path.join(output_dir, 'era5_std.nc'))
    
    # Static (Latitude weights)
    # Weight = cos(lat)
    if 'latitude' in ds:
        lat = ds['latitude']
        weights = np.cos(np.deg2rad(lat))
        # Broadcast to (lat, lon) if needed, but usually 1D lat weight is enough or 2D
        # ncdump_era5_static.txt would confirm structure. 
        # Assuming 2D field for "latitude_weight"
        weights_2d = xr.DataArray(
            np.tile(weights.values[:, np.newaxis], (1, ds.sizes['longitude'])),
            coords={'latitude': lat, 'longitude': ds['longitude']},
            dims=('latitude', 'longitude'),
            name='latitude_weight'
        )
        weights_2d.to_netcdf(os.path.join(output_dir, 'era5_static.nc'))
