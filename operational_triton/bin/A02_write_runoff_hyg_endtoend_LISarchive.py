import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for matplotlib
import matplotlib.pyplot as plt
from osgeo import gdal
import shapefile
from datetime import datetime, timedelta

# Configure matplotlib for image display
plt.rcParams['image.cmap'] = 'viridis'

# Function to read GeoTIFF files
def read_geotiff(file_path, flip=True):
    print(f"Reading GeoTIFF file: {file_path}")
    dataset = gdal.Open(file_path)
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    if flip:
        array = np.flipud(array)
    array[array == 9999] = np.nan
    print(f"GeoTIFF data - dtype: {array.dtype}, shape: {array.shape}, min: {np.nanmin(array)}, max: {np.nanmax(array)}")
    return array.astype(np.float32), dataset  # Ensure the array is in float32

# Function to read shapefiles
def read_shapefile(file_path):
    print(f"Reading shapefile: {file_path}")
    sf = shapefile.Reader(file_path)
    records = sf.records()
    shapes = sf.shapes()
    print(f"Shapefile data - Number of records: {len(records)}, Number of shapes: {len(shapes)}")
    return records, shapes

# Function to generate dates
def generate_dates(start_date, end_date, interval_hours):
    delta = timedelta(hours=interval_hours)
    current = start_date
    dates = []
    while current <= end_date:
        dates.append(current)
        current += delta
    return dates

# Function to create flood event hydrograph runoff
def create_floodevent_hydrograph_runoff(extracted_hyg, time):
    rows, cols = extracted_hyg.shape
    temp_r_timesrs = np.zeros((rows, cols + 1))  # Create array with one additional column
    temp_r_timesrs[:, 1:] = extracted_hyg
    out_hyg = np.column_stack((time, temp_r_timesrs))
    return out_hyg

# Function to save hydrograph data
def save_hydrograph(file_path, data):
    with open(file_path, 'w') as f:
        f.write('%Time(hr) Runoff(mm/hr)\n')
        np.savetxt(f, data, delimiter=',', fmt='%.4f')

# Function to log array details
def log_array_details(name, array):
    print(f"Array {name} details - dtype: {array.dtype}, min: {np.nanmin(array)}, max: {np.nanmax(array)}, shape: {array.shape}")

# Function to plot the data and visualize overlapping
def plot_overlapping(LIS_grid, unique_id_table_triton, Total_Runoff):
    plt.figure(figsize=(12, 8))
    plt.subplot(1, 3, 1)
    plt.imshow(LIS_grid, cmap='viridis')
    plt.title('LIS_grid')

    plt.subplot(1, 3, 2)
    plt.imshow(Total_Runoff, cmap='viridis', vmin=0, vmax=5)
    plt.title('Total_Runoff')

    plt.subplot(1, 3, 3)
    plt.imshow(LIS_grid, cmap='gray', alpha=0.5)
    for unique_id in unique_id_table_triton[:, 0]:
        loc = np.where(LIS_grid == unique_id)
        plt.scatter(loc[1], loc[0], color='red')  # Correctly plotting the coordinates
    plt.title('Unique IDs on LIS_grid')

    plt.tight_layout()
    plt.savefig('overlapping_visualization.png')
    plt.close()
    print("Saved overlapping visualization as 'overlapping_visualization.png'")

# Main script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <start_date> <end_date>")
        print("Date format: YYYY-MM-DD")
        sys.exit(1)

    start_date_str = sys.argv[1]
    end_date_str = sys.argv[2]

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(hours=23)
    except ValueError as e:
        print(f"Error parsing dates: {e}")
        sys.exit(1)

    # Read the LIS_grid GeoTIFF without flipping
    LIS_grid, _ = read_geotiff('/ccs/home/g7h/afw-cyclone/ETE_Forecasting/LIS_Sample/GIS/LIS_UniqueId.tif', flip=False)

    # Read the shapefile
    shapefile_path = '/ccs/home/g7h/afw-cyclone/ETE_Forecasting/LIS_Sample/GIS/osan_LIS_UniqueId_90m.shp'
    records, shapes = read_shapefile(shapefile_path)
    unique_id_table_triton = np.array([[r.DN, r.TRITON_Run] for r in records])
    print(f"Unique ID table - shape: {unique_id_table_triton.shape}, first 5 entries: {unique_id_table_triton[:5]}")

    # Generate dates
    dates = generate_dates(start_date, end_date, 3)  # 3-hour intervals

    # Prepare output directory
    output_dir = 'Output_Plots'
    os.makedirs(output_dir, exist_ok=True)

    PathName = '/lustre/cyclone/nwp500/scratch/g7h/TRITON_Operation/02_LISpostproc/'
    FilePrefix = 'PS.557WW_SC.U_DI.C_GP.LIS-NOAH_GR.C0P09DEG_AR.GLOBAL_PA.LIS_DD.'
    roff_hyg = np.zeros((len(dates), unique_id_table_triton.shape[0]))  # Initialize roff_hyg

    for i, date in enumerate(dates):
        date_str = date.strftime('%Y%m%d_DT.%H00_DF')
        FileName_24 = f'{PathName}/{FilePrefix}{date_str}_band_24.tif'
        FileName_25 = f'{PathName}/{FilePrefix}{date_str}_band_25.tif'
        
        print(f"Processing files: {FileName_24} and {FileName_25}")

        if not os.path.exists(FileName_24) or not os.path.exists(FileName_25):
            print(f"Files {FileName_24} or {FileName_25} do not exist. Skipping...")
            continue

        A24, _ = read_geotiff(FileName_24, flip=True)
        A25, _ = read_geotiff(FileName_25, flip=True)

        A = (A24 + A25).astype(np.float32)  # Ensure the combined array is in float32

        # Additional validation: Replace any non-finite values with 0
        A[~np.isfinite(A)] = 0

        alphaData = ~np.isnan(A)

        # Debugging: Print data type information and value ranges
        log_array_details("A", A)
        log_array_details("alphaData", alphaData)

        # Ensure all values in A are valid floats before plotting
        try:
            assert np.issubdtype(A.dtype, np.floating), f"Unsupported dtype: {A.dtype}"
        except AssertionError as e:
            print(f"AssertionError for date {date_str}: {e}")
            continue

        # Simplified plotting to isolate issue
        try:
            plt.imshow(A, alpha=alphaData, vmin=0, vmax=5)
            plt.colorbar()
            plt.title(f'{FilePrefix}{date_str}')
            plt.savefig(os.path.join(output_dir, f'figure_{date_str}.png'))
        except Exception as e:
            print(f"Error during plotting for date {date_str}: {e}")
        finally:
            plt.close()

        Total_Runoff = A

        # Ensure shape matching and log debug info
        mask_indices = np.isin(LIS_grid, unique_id_table_triton[:, 0])
        if mask_indices.shape != LIS_grid.shape:
            print(f"Skipping date {date_str} due to shape mismatch.")
            continue

        print(f"Unique IDs in unique_id_table_triton: {unique_id_table_triton[:, 0][:5]}")
        print(f"Mask unique values: {np.unique(mask_indices)}, count: {np.sum(mask_indices)}")

        # Log some specific values to debug the mapping process
        unique_ids = unique_id_table_triton[:, 0]
        for unique_id in unique_ids[:50]:  # Check the first 50 unique IDs
            loc = np.where(LIS_grid == unique_id)
            for (r, c) in zip(loc[0], loc[1]):
                print(f"Unique ID {unique_id} found at location: ({r}, {c})")
                print(f"Runoff value at this location: {Total_Runoff[r, c]}")

        # Check if there are non-zero values in the Total_Runoff array
        non_zero_values = Total_Runoff[Total_Runoff != 0]
        print(f"Total number of non-zero values in Total_Runoff: {len(non_zero_values)}")
        print(f"First 5 non-zero values in Total_Runoff: {non_zero_values[:5]}")

        # Extract runoff data using the mask
        filtered_runoff = np.where(mask_indices, Total_Runoff, np.nan)
        print(f"Filtered runoff max: {np.nanmax(filtered_runoff)}, shape: {filtered_runoff.shape}")

        # Update roff_hyg with filtered runoff data
        for idx, (unique_id, triton_run) in enumerate(unique_id_table_triton):
            loc = np.where(LIS_grid == unique_id)
            for (r, c) in zip(loc[0], loc[1]):
                roff_hyg[i, idx] += filtered_runoff[r, c]  # Accumulate runoff values

    # Replace NaN values with zero; possible because of ocean
    roff_hyg[np.isnan(roff_hyg)] = 0

    # Save hydrograph data
    out_hyg = create_floodevent_hydrograph_runoff(roff_hyg / 3, np.arange(3, 3 * len(dates) + 1, 3))
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    file_name = f'osan_{start_date_str}_{end_date_str}.hyg'
    save_hydrograph(file_name, out_hyg)

    print('FINAL WRITING COMPLETE')

    # Plot the overlapping areas to visualize potential issues
    plot_overlapping(LIS_grid, unique_id_table_triton, Total_Runoff)
