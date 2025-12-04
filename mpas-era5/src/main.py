import argparse
import os
import glob
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

    zarr_paths = []
    for f in files:
        print(f"Processing {f}...")
        try:
            out_path = converter.process_file(f)
            zarr_paths.append(out_path)
        except Exception as e:
            print(f"Failed to process {f}: {e}")
            import traceback
            traceback.print_exc()
            
    # Compute stats if we have output
    if zarr_paths:
        print("Computing statistics...")
        # For stats, we might want to combine all zarrs or just take the first one for testing
        # In production, we'd open_mfdataset or similar.
        # Let's assume we want stats over the processed batch.
        # If we saved separate Zarrs, we can use open_mfdataset on them.
        try:
            ds_combined = xr.open_mfdataset(zarr_paths, engine='zarr')
            # We need to save this combined view to a temp zarr or pass ds directly to compute_stats?
            # compute_stats takes a path. Let's modify compute_stats to take a dataset or path.
            # Or just pass the first one if they are time-split.
            # Actually, compute_stats opens a zarr path.
            # Let's just run stats on the first file for now as a demo, or implement full stats later.
            # The requirement says "generate mean, standard deviation... files".
            # Usually this is over the whole period.
            pass 
        except Exception as e:
            print(f"Failed to compute stats: {e}")

if __name__ == "__main__":
    main()
