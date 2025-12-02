# Codebase Analysis Report (Phase 2.1)

## 1. Introduction
This report provides an analysis of the existing codebase located in the `bin` directory. The analysis covers inputs/outputs, functionalities, strengths, weaknesses, missing requirements, and technical suggestions for the Operational TRITON project.

## 2. Codebase Overview
The current codebase consists of a mix of Shell scripts and Python scripts designed to ingest LIS data, process it, and generate runoff hydrographs for the TRITON model.

### 2.1 Files Analyzed
- `bin/00_rsync.sh`
- `bin/01_check_newday_convert.sh`
- `bin/A02_write_runoff_hyg_endtoend_LISarchive.py`
- `bin/lis_hpc11.py`

## 3. Detailed Analysis

### 3.1 `bin/00_rsync.sh`
- **Functionality:** Synchronizes LIS input data from a source feed directory to a local work directory. It supports a 'forecast' mode (defaulting to the last 5 days) and a 'hindcast' mode (specific date range). It triggers `01_check_newday_convert.sh`.
- **Inputs:**
    - Arguments: `--mode`, `--feed-dir`, `--work-dir`, `--start-date`, `--end-date`.
- **Outputs:**
    - Synced files in `WORK_DIR/01_LISinput/`.
    - Logs appended to `LOG_FILE`.
- **Strengths:**
    - Clear separation of forecast and hindcast modes.
    - Basic argument parsing.
- **Weaknesses:**
    - **Hardcoded Paths:** Contains hardcoded paths like `/lustre/active/...` and `/lustre/cyclone/...`.
    - **Hardcoded Patterns:** The `rsync` source pattern `2024/Dec/*/LIS-DD` is hardcoded to a specific year/month, which will fail for other dates.
    - **Error Handling:** Minimal error handling; relies on `set -e` but doesn't gracefully handle `rsync` failures or partial syncs.

### 3.2 `bin/01_check_newday_convert.sh`
- **Functionality:** Iterates through a date range, checks for the existence of data directories, converts GRIB files to TIFF (using `lis_hpc11.py`), runs runoff processing (`A02...py`), and submits a SLURM job for the TRITON model.
- **Inputs:** `basedir`, `start_date`, `end_date`, `temparchive`.
- **Outputs:**
    - GeoTIFF files.
    - Log files (`log_$current_date`).
    - SLURM job submission.
- **Strengths:**
    - Modular `check_directory` function.
    - Handles date iteration logic.
- **Weaknesses:**
    - **Hardcoded Logic:** `days_to_add=4` is hardcoded.
    - **Hardcoded Bands:** Explicitly calls `lis_hpc11.py` for bands 23 and 24.
    - **Busy Waiting:** Uses a `while true` loop with `sleep 0.6` to check for directory existence, which is inefficient.
    - **Job Monitoring:** Implements a custom loop to monitor SLURM jobs via `scontrol`, which is brittle.
    - **Template Dependencies:** Relies on hardcoded paths for templates (`$WORK_DIR/03_TRITON_NRT/template/*`).

### 3.3 `bin/A02_write_runoff_hyg_endtoend_LISarchive.py`
- **Functionality:** Processes GeoTIFFs (bands 24 and 25), sums them, applies a shapefile mask to aggregate runoff by unique ID, and saves the result as a `.hyg` hydrograph file.
- **Inputs:** `start_date`, `end_date`.
- **Outputs:**
    - `.hyg` file (e.g., `osan_YYYYMMDD_YYYYMMDD.hyg`).
    - Visualization plots in `Output_Plots/`.
- **Strengths:**
    - Uses standard libraries (`gdal`, `shapefile`, `numpy`).
    - Includes visualization for verification (`plot_overlapping`).
- **Weaknesses:**
    - **Hardcoded Paths:** Absolute paths to shapefiles and input directories (`/ccs/home/...`, `/lustre/...`).
    - **Hardcoded Bands:** Specifically looks for `_band_24.tif` and `_band_25.tif`.
    - **Visualization:** Plotting code is mixed with processing logic.

### 3.4 `bin/lis_hpc11.py`
- **Functionality:** Converts a specific band from a GRIB file to GeoTIFF and generates a PNG plot.
- **Inputs:** File list, base directory, output directory, band index.
- **Outputs:** GeoTIFF files and PNG plots.
- **Strengths:**
    - specific utility for GRIB to TIFF conversion.
- **Weaknesses:**
    - **Band Indexing:** Logic `band_index = int(band_index) - 1` assumes 1-based input.
    - **Error Handling:** Basic try-except blocks.

## 4. Missing Requirements
Based on `charter.md` and `project_plan.md`, the following are missing or inadequate:

1. **Scalability (Multi-site Support):** The current scripts are heavily hardcoded for "Osan" (e.g., `osan_xx_...` directories, specific shapefiles). There is no configuration mechanism to easily switch to Offutt or McConnell AFBs.
2. **Robust Automation:** The "daemon" behavior is simulated with shell loops and sleeps. A proper scheduling or event-driven architecture is missing.
3. **Threshold-based Trigger:** There is no logic to check for flood thresholds and trigger high-resolution modeling accordingly.
4. **Redundancy:** No logic for dual execution or failover.
5. **Remote Monitoring:** No mechanism to report status to a remote system; only local log files are used.
6. **Configuration Management:** All paths and parameters are hardcoded in the scripts, making deployment to new environments (like AFW HPC11) difficult.

## 5. Technical Suggestions

### 5.1 Code Organization
- **Refactor into a Python Package:** Move logic from shell scripts and standalone Python scripts into a structured Python package (e.g., `triton_operational`).
    - `triton_operational/config.py`: Centralized configuration.
    - `triton_operational/ingest.py`: Data ingestion logic.
    - `triton_operational/process.py`: GRIB/TIFF processing.
    - `triton_operational/model.py`: TRITON/AutoRoute interface.
    - `triton_operational/workflow.py`: Orchestration logic.

### 5.2 Configuration
- **Centralized Config:** Use a YAML or JSON file to store all paths, site-specific settings (shapefiles, coordinates), and parameters (thresholds, intervals).
- **Environment Variables:** Use environment variables for secrets or environment-specific paths.

### 5.3 Operation Configuration
- **Workflow Orchestration:** Replace shell loops with a robust scheduler (e.g., Cron, Systemd timers) or a workflow engine (e.g., Airflow, Prefect) if complexity grows. For a lightweight solution, a Python-based daemon with proper logging and signal handling is better than shell scripts.
- **Logging:** Implement structured logging (JSON format) to facilitate future remote monitoring integration.

### 5.4 Specific Improvements
- **Dynamic Rsync:** Update `00_rsync.sh` to construct the source path dynamically based on the requested date.
- **Efficient Polling:** Replace `sleep` loops with `inotify` (if available) or exponential backoff polling.
- **Job Management:** Use a Python interface to SLURM (like `pyslurm` or subprocess calls with robust parsing) instead of `scontrol` text parsing in bash.
