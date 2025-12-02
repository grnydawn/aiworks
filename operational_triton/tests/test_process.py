import pytest
from unittest.mock import MagicMock, patch
import numpy as np
import sys

# Ensure mocks are in place before importing
# (This is handled by conftest.py, but we need to access the mocks to configure them)

from src.process import DataProcessor

@pytest.fixture
def processor(config_object):
    return DataProcessor(config_object)

def test_check_data_availability(processor):
    assert processor.check_data_availability("2023-12-01") is True

def test_convert_grib_to_tiff(processor):
    # Retrieve the mocks from sys.modules
    mock_pygrib = sys.modules["pygrib"]
    mock_gdal = sys.modules["osgeo.gdal"]
    mock_osr = sys.modules["osgeo.osr"]

    # Setup pygrib mock
    mock_grbs = MagicMock()
    mock_pygrib.open.return_value = mock_grbs
    
    mock_message = MagicMock()
    mock_grbs.message.return_value = mock_message
    
    # Mock data
    mock_message.values = np.zeros((10, 10))
    mock_message.latlons.return_value = (np.zeros((10, 10)), np.zeros((10, 10)))
    mock_message.Di = 0.1
    mock_message.Dj = 0.1
    
    # Setup GDAL mock
    mock_driver = MagicMock()
    mock_gdal.GetDriverByName.return_value = mock_driver
    mock_dataset = MagicMock()
    mock_driver.Create.return_value = mock_dataset
    
    # Run the method
    result = processor.convert_grib_to_tiff("dummy.grib", "output", band_indices=[1])
    
    assert result is True
    mock_pygrib.open.assert_called_with("dummy.grib")
    mock_grbs.message.assert_called_with(1)
    mock_driver.Create.assert_called()
    mock_dataset.GetRasterBand(1).WriteArray.assert_called()

def test_convert_grib_to_tiff_failure(processor):
    mock_pygrib = sys.modules["pygrib"]
    mock_pygrib.open.side_effect = Exception("File not found")
    
    result = processor.convert_grib_to_tiff("missing.grib", "output")
    
    assert result is False
