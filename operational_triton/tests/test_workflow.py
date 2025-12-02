import pytest
from unittest.mock import MagicMock, patch
from src.workflow import WorkflowEngine

@pytest.fixture
def mock_components():
    with patch("src.workflow.DataIngestor") as MockIngestor, \
         patch("src.workflow.DataProcessor") as MockProcessor, \
         patch("src.workflow.TritonModel") as MockModel:
        
        ingestor_instance = MockIngestor.return_value
        processor_instance = MockProcessor.return_value
        model_instance = MockModel.return_value
        
        yield {
            "ingestor": ingestor_instance,
            "processor": processor_instance,
            "model": model_instance,
            "MockIngestor": MockIngestor,
            "MockProcessor": MockProcessor,
            "MockModel": MockModel
        }

def test_workflow_init(config_object, mock_components):
    engine = WorkflowEngine(config_object)
    
    mock_components["MockIngestor"].assert_called_with(config_object)
    mock_components["MockProcessor"].assert_called_with(config_object)
    mock_components["MockModel"].assert_called_with(config_object)

def test_run_pipeline_success(config_object, mock_components):
    engine = WorkflowEngine(config_object)
    
    # Setup mocks
    mock_components["ingestor"].sync_data.return_value = True
    mock_components["model"].generate_hydrograph.return_value = True
    
    engine.run_pipeline("2023-12-01")
    
    mock_components["ingestor"].sync_data.assert_called_with("2023-12-01")
    # Verify model is called for enabled sites (site_A is enabled in mock_config_data)
    mock_components["model"].generate_hydrograph.assert_called_with("2023-12-01", "site_A")

def test_run_pipeline_ingest_fail(config_object, mock_components):
    engine = WorkflowEngine(config_object)
    
    mock_components["ingestor"].sync_data.return_value = False
    
    engine.run_pipeline("2023-12-01")
    
    mock_components["ingestor"].sync_data.assert_called_with("2023-12-01")
    # Model should not be called if ingest fails
    mock_components["model"].generate_hydrograph.assert_not_called()
