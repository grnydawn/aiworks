import xarray as xr
import sys
import os
import glob

def inspect_zarr(temp_dir):
    zarr_files = sorted(glob.glob(os.path.join(temp_dir, "*.zarr")))
    if not zarr_files:
        print(f"No Zarr files found in {temp_dir}")
        return

    first_file = zarr_files[0]
    print(f"Inspecting first file: {first_file}")
    
    try:
        ds = xr.open_zarr(first_file, consolidated=False)
        print("Dimensions:", ds.dims)
        print("Variables:", ds.data_vars)
        if 'U' in ds:
            print("U shape:", ds['U'].shape)
        if 'time' in ds:
            print("Time size:", ds.sizes['time'])
            print("Time values:", ds['time'].values)
            
    except Exception as e:
        print(f"Failed to open {first_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_zarr.py <temp_parts_dir>")
        sys.exit(1)
    
    inspect_zarr(sys.argv[1])
