import pytest
import sys
from unittest.mock import MagicMock
import os
import yaml

# Mock heavy dependencies that might not be present in the test environment
# This allows unit tests to run on generic linux/mac without complex installs
module_names = ["pygrib", "osgeo", "osgeo.gdal", "osgeo.osr", "pyslurm", "cartopy", "cartopy.crs"]
for module_name in module_names:
    sys.modules[module_name] = MagicMock()

# Link osgeo.gdal to osgeo.gdal in case of from osgeo import gdal
sys.modules["osgeo"].gdal = sys.modules["osgeo.gdal"]
sys.modules["osgeo"].osr = sys.modules["osgeo.osr"]

# Now we can safely import modules that use these
# (Imports in test files will use these mocks)

@pytest.fixture
def mock_config_data():
    return {
        "global": {
            "work_dir": "/tmp/triton_work",
            "log_dir": "/tmp/triton_logs",
            "input_dir": "/tmp/triton_input",
            "feed_dir": "/tmp/triton_feed"
        },
        "ingest": {
            "source_host": "remote_host",
            "source_base_path": "/data/lis",
            "dry_run": False
        },
        "sites": {
            "site_A": {
                "enabled": True,
                "lat": 34.0,
                "lon": -118.0,
                "threshold_trigger": 5.0
            },
            "site_B": {
                "enabled": False
            }
        },
        "workflow": {
            "data_check_interval_seconds": 1
        }
    }

@pytest.fixture
def mock_config_file(tmp_path, mock_config_data):
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(mock_config_data, f)
    return str(config_path)

@pytest.fixture
def config_object(mock_config_data):
    """Returns a Config object with mocked data"""
    # We need to import Config here, but it might depend on other things.
    # Assuming Config is a simple class or we just use the dict for now if the class is simple.
    # Let's import the actual class if possible, or just return the dict if the tests use the dict.
    # Looking at config.py, it likely has a load function.
    # For unit tests of other modules, passing the dict (or an object wrapping it) is often enough
    # if the code uses config.get().
    
    # Let's create a simple wrapper that behaves like the config dictionary
    class MockConfig(dict):
        def get(self, key, default=None):
            # Support nested keys like "global.work_dir"
            if "." in key:
                parts = key.split(".")
                val = self
                try:
                    for part in parts:
                        val = val[part]
                    return val
                except KeyError:
                    return default
            return super().get(key, default)
            
    return MockConfig(mock_config_data)
