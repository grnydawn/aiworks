#!/bin/bash

# Function to check if a directory exists
check_directory() {
    local dir=$1
    if [ -d "$dir" ]; then
        echo "Directory found: $dir"
        return 0
    else
        echo "Directory not found: $dir"
        return 1
    fi
}

# Get the base directory, start date, end date, and temparchive from arguments
basedir=$1
start_date=$2
end_date=$3
temparchive=$4
WORK_DIR="/lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/TRITON_Operation/"



export MPLCONFIGDIR=/lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/
export FONTCONFIG_PATH=/lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/
export XDG_CACHE_HOME=/lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/

# Check if basedir, start_date, end_date, and temparchive arguments are provided
if [ -z "$basedir" ] || [ -z "$start_date" ] || [ -z "$end_date" ] || [ -z "$temparchive" ]; then
    echo "Usage: $0 basedir YYYY-MM-DD YYYY-MM-DD temparchive"
    exit 1
fi

# Initialize current date to start date
current_date=$start_date

# Iterate through the dates until the end date
while [ "$(date -d "$current_date" +%Y-%m-%d)" != "$(date -d "$end_date + 1 day" +%Y-%m-%d)" ]; do
    year=$(date -d "$current_date" +%Y)
    month=$(date -d "$current_date" +%b)
    day=$(date -d "$current_date" +%d)

    dir="$basedir/$year/$month/$day"
    while true; do
        if check_directory "$dir"; then
            
            echo $dir/LIS-DD
			pwd
            ls $dir/LIS-DD > files_to_process_$current_date
			
			
			
            echo I am here  .. for $current_date launching step 1 .. converting grib to tiff and visualize for surface and subsurface runoff
            
            time python lis_hpc11.py  files_to_process_$current_date $basedir/$year/$month/$day/LIS-DD $temparchive 23 > log_$current_date 
            time python lis_hpc11.py  files_to_process_$current_date $basedir/$year/$month/$day/LIS-DD $temparchive 24 >> log_$current_date 
			
			
			
			# Define the number of days to add (in this case, 4 days #hardcode)
			days_to_add=4

			# Calculate the end date
			end_date_triton=$(date -d "$current_date + $days_to_add days" +%Y-%m-%d)

			time python A02_write_runoff_hyg_endtoend_LISarchive.py $current_date $end_date_triton >> log_$current_date 
			pwd
			
			mkdir -p $WORK_DIR/03_TRITON_NRT/osan_xx_$current_date
			
			cp -r $WORK_DIR/03_TRITON_NRT/template/* $WORK_DIR/03_TRITON_NRT/osan_xx_$current_date
			cp $WORK_DIR/03_TRITON_NRT/osan_xx_$current_date/input/osan_XXdateXX_template.cfg $WORK_DIR/03_TRITON_NRT/osan_xx_$current_date/input/osan_$current_date.cfg
			
			cp ~/afw-cyclone/ETE_Forecasting/osan_${current_date//-/}_${end_date_triton//-/}.hyg $WORK_DIR/03_TRITON_NRT/osan_xx_$current_date/input/
			
			sed -i "s/XXXosan_HYGXXX/osan_${current_date//-/}_${end_date_triton//-/}.hyg/g" $WORK_DIR/03_TRITON_NRT/osan_xx_$current_date/input/osan_$current_date.cfg
			
			
			sed -i "s/XXdateXX/$current_date/g" $WORK_DIR/03_TRITON_NRT/osan_xx_$current_date/job_afw.sbatch
			
			cd $WORK_DIR/03_TRITON_NRT/osan_xx_$current_date/
			# Submit the job and capture the job ID
			job_id=$(sbatch job_afw.sbatch | awk '{print $4}')
			
			cd /lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/
			
			echo "Job $job_id has been submitted. Waiting ...."

			# Wait for the job to finish
			# scontrol wait_job $job_id
			# Wait for the job to finish using scontrol
			while true; do
				# Get job information and extract only the first occurrence of JobState
				job_info=$(scontrol show jobid -dd $job_id)
				job_state=$(echo "$job_info" | grep -oP 'JobState=\K\S+' | head -n 1)

				echo "Current job state is $job_state"

				if [[ "$job_state" == "COMPLETED" || "$job_state" == "FAILED" || "$job_state" == "CANCELLED" || "$job_state" == "TIMEOUT" ]]; then
					echo "Job $job_id has finished with state: $job_state"
					break
				fi

				sleep 30  # Adjust the sleep interval as needed
			done
			# Proceed with the next step after the job completes
			echo "Job $job_id has completed. Moving to the next step."
			
			cd /lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/
			
            echo $current_date day complete 
            sleep 10
            break
        else
            # Directory does not exist, print message and wait before trying again
            echo "Directory does not exist, waiting to retry: $dir"
            sleep 0.6 # Adjust the sleep duration as needed
        fi
    done

    # Move to the next day
	
	
    current_date=$(date -I -d "$current_date + 1 day")
	echo going to next day ... $current_date
done
