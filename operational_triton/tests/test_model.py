import pytest
from unittest.mock import MagicMock, patch
import sys

# Ensure mocks are in place
# (Handled by conftest.py)

from src.model import TritonModel

@pytest.fixture
def model(config_object):
    return TritonModel(config_object)

def test_generate_hydrograph_trigger(model):
    # The current implementation has hardcoded total_runoff = 10.0
    # Site config in conftest has threshold 5.0
    # So it should return True
    
    # We need to ensure site_config is retrieved correctly
    # The fixture mock_config_data has "sites.site_A"
    
    result = model.generate_hydrograph("2023-12-01", site_name="site_A")
    assert result is True

def test_generate_hydrograph_no_trigger(model, config_object):
    # We can modify the config object to have a high threshold
    # But config_object is a fixture, so we should patch the get method or modify the dict if it's mutable
    
    # Since our MockConfig in conftest inherits from dict, we can modify it
    config_object["sites"]["site_A"]["threshold_trigger"] = 20.0
    
    result = model.generate_hydrograph("2023-12-01", site_name="site_A")
    assert result is False

def test_generate_hydrograph_missing_site(model):
    result = model.generate_hydrograph("2023-12-01", site_name="non_existent_site")
    assert result is None

def test_submit_job(model):
    job_id = model.submit_job("script.sh")
    assert job_id == "12345"

def test_monitor_job(model):
    status = model.monitor_job("12345")
    assert status == "COMPLETED"
