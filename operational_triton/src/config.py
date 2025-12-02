import os
import yaml
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """Loads configuration from a YAML file."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file {self.config_path} not found. Using defaults.")
            return self._default_config()
        
        with open(self.config_path, 'r') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.error(f"Error parsing config file: {e}")
                return self._default_config()

    def _default_config(self):
        """Returns default configuration."""
        return {
            "global": {
                "feed_dir": "/lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/TRITON_Operation/",
                "work_dir": "/lustre/cyclone/nwp500/proj-shared/youngsung/TRITON_Operation/",
                "log_dir": "logs"
            },
            "sites": {
                "osan": {
                    "enabled": True,
                    "shapefile": "/ccs/home/g7h/afw-cyclone/ETE_Forecasting/LIS_Sample/GIS/osan_LIS_UniqueId_90m.shp",
                    "lis_grid": "/ccs/home/g7h/afw-cyclone/ETE_Forecasting/LIS_Sample/GIS/LIS_UniqueId.tif",
                    "threshold_trigger": 5.0 # Example threshold
                }
            },
            "workflow": {
                "data_check_interval_seconds": 300,
                "max_retries": 3
            }
        }

    def get(self, key, default=None):
        """Retrieves a configuration value using dot notation (e.g., 'global.feed_dir')."""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
