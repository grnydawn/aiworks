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
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    converter = Converter(args.map_file, args.output_dir)
    
    # Find files
    files = sorted(glob.glob(os.path.join(args.input_dir, "*.nc")))
    if not files:
        print(f"No .nc files found in {args.input_dir}")
        return

    # Create temp dir for intermediate files
    temp_dir = os.path.join(args.output_dir, "temp_parts")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    zarr_paths = []
    for f in files:
        print(f"Processing {f}...")
        try:
            # We temporarily save to temp_dir
            # We need to modify converter to accept an output dir or we just pass temp_dir
            # Converter takes output_dir in init. 
            # Let's re-instantiate converter or modify it? 
            # Converter.output_dir is public.
            converter.output_dir = temp_dir
            out_path = converter.process_file(f)
            zarr_paths.append(out_path)
        except Exception as e:
            print(f"Failed to process {f}: {e}")
            import traceback
            traceback.print_exc()
            
    if zarr_paths:
        try:
            print("Combining files...")
            # Combine all processed files
            ds_combined = xr.open_mfdataset(zarr_paths, engine='zarr', combine='nested', concat_dim='time')
            
            # Determine start and end time
            times = pd.to_datetime(ds_combined.time.values)
            start_date = times.min().strftime('%Y-%m-%d')
            end_date = times.max().strftime('%Y-%m-%d')
            
            output_filename = f"SixHourly_TOTAL_{start_date}_{end_date}.zarr"
            output_path = os.path.join(args.output_dir, output_filename)
            
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
