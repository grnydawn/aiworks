import logging
import json
import os
from datetime import datetime, timedelta

def setup_logging(log_dir="logs", log_level=logging.INFO):
    """Sets up structured logging."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"triton_{datetime.now().strftime('%Y%m%d')}.log")

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def get_date_range(start_date_str, end_date_str):
    """Generates a list of dates between start and end date (inclusive)."""
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    delta = end - start
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]

def get_previous_days(days=5):
    """Returns the date string for 'days' ago."""
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
