# Project Charter: MPAS to ERA5 Converter

## 1. Project Title
MPAS to ERA5 Data Conversion and Regridding Tool

## 2. Project Goal
Develop a Python-based solution to convert MPAS atmospheric NetCDF files into ERA5-formatted Zarr files. The tool will handle variable mapping, regridding to the ERA5 grid, and the generation of statistical auxiliary files (mean, standard deviation, latitude weights).

## 3. Background
The project aims to bridge the gap between MPAS model output and ERA5 data structures, facilitating comparison or integration of MPAS data with workflows designed for ERA5. The conversion involves specific variable mapping and spatial regridding using provided mapping files.

## 4. Scope
### In-Scope
- **Data Ingestion**: Scanning and loading MPAS NetCDF files from a specified directory.
- **Variable Conversion**: Mapping and converting MPAS variables to ERA5 equivalents:
    - 3D variables: U, V, T, Q (and potentially U500, V500, T500, Z500, Q500 if derived or extracted).
    - Surface/2D variables: SP (Surface Pressure), t2m (2-meter Temperature).
- **Regridding**: Interpolating data from the MPAS mesh to the ERA5 latitude-longitude grid using a provided mapping NetCDF file.
- **Dimension Handling**: Ensuring output dimensions match ERA5 specifications.
- **Auxiliary Data Generation**: Creating corresponding mean, standard deviation, and latitude-weight files.
- **Output Format**: Saving processed data as Zarr files matching ERA5 metadata standards.

### Out-of-Scope
- Development of the regridding weights/mapping file itself (it is provided).
- Analysis of the data post-conversion (unless part of validation).

## 5. Key Deliverables
1. **Conversion Script(s)**: Python script(s) to perform the batch conversion of MPAS NetCDF to ERA5 Zarr.
2. **Statistical Generation**: Functionality to compute and save mean, standard deviation, and static files.
3. **Documentation**: Instructions on how to run the scripts and configure input/output paths.

## 6. Technical Requirements & Dependencies
- **Input Data**:
    - MPAS NetCDF files (structure per `data/ncdump_mpas.txt`).
    - Mapping file for regridding (`data/ncdump_map.txt`).
- **Reference Implementations**:
    - `data/script_extract_var_and_interlopation.py` (logic for extraction/regridding).
    - `data/zarr_U` (metadata reference for Zarr output).
- **Output Specifications**:
    - Zarr format.
    - Auxiliary files structure per `data/ncdump_era5_mean.txt`, `data/ncdump_era5_std.txt`, `data/ncdump_era5_static.txt`.
- **Language**: Python.
- **Libraries**: Likely `xarray`, `numpy`, `zarr`, `netCDF4`, `scipy` (or specific regridding libs if used in reference).

## 7. Assumptions
- The provided mapping file is sufficient for the required regridding accuracy.
- The input MPAS files are consistent in structure.
- Sufficient computational resources are available for processing the NetCDF files.
