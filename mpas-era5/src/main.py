import argparse
import os
import glob
import xarray as xr
import pandas as pd
from .converter import Converter
from .stats import compute_stats

def main():
    parser = argparse.ArgumentParser(description="Convert MPAS NetCDF to ERA5 Zarr")
    parser.add_argument("--input_dir", required=True, help="Directory containing MPAS NetCDF files")
    parser.add_argument("--map_file", required=True, help="Path to regridding mapping NetCDF file")
    parser.add_argument("--output_dir", required=True, help="Directory to save output Zarr files")
    parser.add_argument("--skip_conversion", action="store_true", help="Skip conversion and only combine existing files in temp_parts")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    converter = Converter(args.map_file, args.output_dir)
    
    # Create temp dir for intermediate files
    temp_dir = os.path.join(args.output_dir, "temp_parts")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    zarr_paths = []
    
    if not args.skip_conversion:
        # Find files
        files = sorted(glob.glob(os.path.join(args.input_dir, "*.nc")))
        if not files:
            print(f"No .nc files found in {args.input_dir}")
            return

        for f in files:
            print(f"Processing {f}...")
            try:
                # We temporarily save to temp_dir
                converter.output_dir = temp_dir
                out_path = converter.process_file(f)
                zarr_paths.append(out_path)
            except Exception as e:
                print(f"Failed to process {f}: {e}")
                import traceback
                traceback.print_exc()
    else:
        print(f"Skipping conversion. Looking for existing files in {temp_dir}...")
        zarr_paths = sorted(glob.glob(os.path.join(temp_dir, "*.zarr")))
        if not zarr_paths:
            print(f"No Zarr files found in {temp_dir}")
            return
            
    if zarr_paths:
        try:
            print("Combining files...")
            # Combine all processed files
            ds_combined = xr.open_mfdataset(zarr_paths, engine='zarr', combine='nested', concat_dim='time', consolidated=False)
            
            # Determine start and end time
            times = pd.to_datetime(ds_combined.time.values)
            start_date = times.min().strftime('%Y-%m-%d')
            end_date = times.max().strftime('%Y-%m-%d')
            
            output_filename = f"SixHourly_TOTAL_{start_date}_{end_date}.zarr"
            output_path = os.path.join(args.output_dir, output_filename)
            
            # Rechunk to ensure uniform chunks for Zarr
            # Using chunk size of 1 for time dimension to be safe and uniform
            ds_combined = ds_combined.chunk({'time': 1})
            
            # Clear encoding to avoid chunk mismatch errors
            for var in ds_combined.variables:
                if 'chunks' in ds_combined[var].encoding:
                    del ds_combined[var].encoding['chunks']
            
            print(f"Saving combined dataset to {output_path}...")
            ds_combined.to_zarr(output_path, mode='w', consolidated=False)
            
            print("Computing statistics...")
            # Re-open the combined zarr to ensure we compute stats on the final artifact
            ds_final = xr.open_zarr(output_path)
            compute_stats(ds_final, args.output_dir)
            print("Statistics computed and saved.")
            
            # Optional: Clean up temp_parts? 
            # For now, leaving them might be safer for debugging, but user asked for "one zarr file".
            # I will leave them in temp_parts so the main output dir is clean.
            
        except Exception as e:
            print(f"Failed to combine/stats: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
