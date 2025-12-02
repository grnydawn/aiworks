#!/usr/bin/env bash
set -euo pipefail

# Default values
MODE=""
DATE=""
FEED_DIR="/lustre/active/nwp602/archive/nwp602/lcmc/"
WORK_DIR="/lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/TRITON_Operation/"
LEAD_TIME="5"  # optional default for forecast
LOG_FILE="/lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/logfile.log"

# Python environement activate
# module load afw-python
# cd 
# source /sw/afw/python/anaconda3/base/bin/activate ./.conda/envs/my_env
# conda activate afw-py39-202203-metplus
# echo Python module activated. 

# this is hardcoded - it needs to happen based on the dates
 cd $FEED_DIR
 echo "Syncing LIS inputs..." | tee -a "$LOG_FILE"
 pwd 
 ls
 rsync -av --relative 2024/Dec/*/LIS-DD "$WORK_DIR/01_LISinput/" | tee -a "$LOG_FILE"
 cd $WORK_DIR
 pwd
  

# ============================
# USAGE INFO
# ============================
usage() {
  echo
  echo "Usage:"
  echo "  $0 --mode [forecast|hindcast] --feed-dir PATH --work-dir PATH [--start-date YYYY-MM-DD --end-date YYYY-MM-DD]"
  echo
  echo "Examples:"
  echo "  # Forecast (uses today's date automatically)"
  echo "  $0 --mode forecast --feed-dir /data/feed --work-dir /scratch/work"
  echo
  echo "  # Hindcast (requires explicit dates)"
  echo "  $0 --mode hindcast --feed-dir /data/archive --work-dir /scratch/work --start-date 2024-06-01 --end-date 2024-06-02"
  echo
  exit 1
}

# ============================
# PARSE ARGUMENTS
# ============================
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--mode) MODE="${2:-}"; shift 2 ;;
    -f|--feed-dir) FEED_DIR="${2:-}"; shift 2 ;;
    -w|--work-dir) WORK_DIR="${2:-}"; shift 2 ;;
    --start-date) START_DATE="${2:-}"; shift 2 ;;
    --end-date) END_DATE="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

# Validate required args
[[ -z "$MODE" ]] && { echo "Error: --mode required."; usage; }
[[ -z "$FEED_DIR" ]] && { echo "Error: --feed-dir required."; usage; }
[[ -z "$WORK_DIR" ]] && { echo "Error: --work-dir required."; usage; }

[[ -d "$FEED_DIR" ]] || { echo "Feed directory not found: $FEED_DIR"; exit 1; }
mkdir -p "$WORK_DIR"

echo "=== $(date) | Mode: $MODE ===" >> "$LOG_FILE"

# ============================
# FORECAST MODE
# ============================
if [[ "$MODE" == "forecast" ]]; then
  echo "[Forecast mode]" | tee -a "$LOG_FILE"



  # Date calculations
  today_date=$(date +"%Y-%m-%d")
  date_5_days_ago=$(date -d "5 days ago" +"%Y-%m-%d")
  date_10_days_ago=$(date -d "10 days ago" +"%Y-%m-%d")

  echo "Today's date:        $today_date"     | tee -a "$LOG_FILE"
  echo "Date 5 days ago:     $date_5_days_ago" | tee -a "$LOG_FILE"
  echo "Date 10 days ago:    $date_10_days_ago" | tee -a "$LOG_FILE"

  echo "Running LIS conversion for forecast window..." | tee -a "$LOG_FILE"
  sh 01_check_newday_convert.sh "$WORK_DIR/01_LISinput/" "$date_10_days_ago" "$date_5_days_ago" "$WORK_DIR/02_LISpostproc/" | tee -a "$LOG_FILE"

  echo "=== Forecast Sync Completed ===" | tee -a "$LOG_FILE"
fi

# ============================
# HINDCAST MODE
# ============================
if [[ "$MODE" == "hindcast" ]]; then
  echo "[Hindcast mode]" | tee -a "$LOG_FILE"

  # Validate that both dates are provided
  if [[ -z "$START_DATE" || -z "$END_DATE" ]]; then
    echo "Error: In hindcast mode, you must specify both --start-date and --end-date."
    usage
  fi

  # Validate date format (YYYY-MM-DD)
  if [[ ! "$START_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ || ! "$END_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "Error: Dates must be in YYYY-MM-DD format."
    exit 1
  fi

  echo "Running LIS conversion for $START_DATE to $END_DATE..." | tee -a "$LOG_FILE"
  sh 01_check_newday_convert.sh "$WORK_DIR/01_LISinput/" "$START_DATE" "$END_DATE" "$WORK_DIR/02_LISpostproc/" | tee -a "$LOG_FILE"

  echo "=== Hindcast Sync Completed ===" | tee -a "$LOG_FILE"
fi
