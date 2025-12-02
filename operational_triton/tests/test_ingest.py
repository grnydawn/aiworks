import pytest
from unittest.mock import patch, MagicMock
from src.ingest import DataIngestor
import subprocess

@pytest.fixture
def ingestor(config_object):
    return DataIngestor(config_object)

def test_sync_data_success(ingestor):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        result = ingestor.sync_data("2023-12-01")
        
        assert result is True
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        command = args[0]
        assert "rsync -av --relative" in command
        assert "2023/Dec/*/LIS-DD" in command
        assert kwargs.get("shell") is True

def test_sync_data_failure(ingestor):
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "rsync")
        
        result = ingestor.sync_data("2023-12-01")
        
        assert result is False
