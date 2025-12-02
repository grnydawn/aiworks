import subprocess
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DataIngestor:
    def __init__(self, config):
        self.config = config
        self.feed_dir = config.get("global.feed_dir")
        self.work_dir = config.get("global.work_dir")
        self.input_dir = os.path.join(self.work_dir, "01_LISinput")

    def sync_data(self, date_str):
        """
        Syncs LIS data for a specific date using rsync.
        Constructs the source path dynamically: YYYY/Mon/DD/LIS-DD
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        year = date_obj.strftime("%Y")
        month_abbr = date_obj.strftime("%b") # e.g., Dec
        day = date_obj.strftime("%d")

        # Dynamic source path construction
        # Pattern: /feed_dir/YYYY/Mon/*/LIS-DD
        # Note: The wildcard * in the middle (from original script) needs to be handled.
        # rsync doesn't expand remote wildcards like shell does if not using a shell.
        # We assume the structure is consistent.
        
        source_pattern = f"{year}/{month_abbr}/*/LIS-DD"
        source_path = os.path.join(self.feed_dir, source_pattern)
        
        # Since we can't easily use wildcards in the middle of a path with simple rsync calls 
        # without shell expansion, we might need to be more specific or use shell=True.
        # For now, we'll use the shell expansion capability of rsync or python glob if local.
        # Assuming feed_dir is mounted locally as per the original script.
        
        full_source_pattern = os.path.join(self.feed_dir, year, month_abbr, "*", "LIS-DD")
        
        cmd = [
            "rsync",
            "-av",
            "--relative",
            full_source_pattern,
            self.input_dir
        ]

        logger.info(f"Syncing data for {date_str}...")
        logger.debug(f"Command: {' '.join(cmd)}")

        try:
            # Using shell=True to allow wildcard expansion by the shell
            subprocess.run(f"rsync -av --relative {full_source_pattern} {self.input_dir}", shell=True, check=True, executable="/bin/bash")
            logger.info(f"Successfully synced data for {date_str}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Rsync failed for {date_str}: {e}")
            return False
