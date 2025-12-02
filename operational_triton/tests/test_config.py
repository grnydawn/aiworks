import pytest
import os
import yaml
from src.config import Config

def test_config_defaults(tmp_path):
    # Point to a non-existent file to trigger defaults
    config_path = tmp_path / "non_existent.yaml"
    config = Config(str(config_path))
    
    assert config.get("global.log_dir") == "logs"
    assert config.get("workflow.max_retries") == 3

def test_config_load_file(tmp_path):
    data = {
        "global": {"work_dir": "/custom/path"},
        "workflow": {"max_retries": 5}
    }
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(data, f)
        
    config = Config(str(config_path))
    assert config.get("global.work_dir") == "/custom/path"
    assert config.get("workflow.max_retries") == 5

def test_config_get_nested(tmp_path):
    data = {"a": {"b": {"c": 10}}}
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(data, f)
        
    config = Config(str(config_path))
    assert config.get("a.b.c") == 10
    assert config.get("a.b.d", "default") == "default"
    assert config.get("x.y.z") is None
