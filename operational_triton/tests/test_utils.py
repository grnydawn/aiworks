import pytest
import os
import logging
from datetime import datetime, timedelta
from src.utils import setup_logging, get_date_range, get_previous_days

def test_get_date_range():
    start = "2023-01-01"
    end = "2023-01-03"
    dates = get_date_range(start, end)
    assert dates == ["2023-01-01", "2023-01-02", "2023-01-03"]

def test_get_date_range_single_day():
    start = "2023-01-01"
    end = "2023-01-01"
    dates = get_date_range(start, end)
    assert dates == ["2023-01-01"]

def test_get_previous_days():
    days = 5
    expected = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    assert get_previous_days(days) == expected

def test_setup_logging(tmp_path):
    log_dir = tmp_path / "logs"
    setup_logging(log_dir=str(log_dir), log_level=logging.DEBUG)
    
    assert os.path.exists(log_dir)
    # Check if a log file was created
    files = list(os.listdir(log_dir))
    assert len(files) > 0
    assert files[0].startswith("triton_")
    assert files[0].endswith(".log")
