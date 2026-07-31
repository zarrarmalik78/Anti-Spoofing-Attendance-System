import yaml
import os
import logging
from typing import Dict, Any

def load_config(path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Loads and validates the YAML configuration file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found at {path}")

    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Validate required keys
    required_keys = [
        "camera", "models", "detection", "recognition", 
        "registration", "attendance", "database", "logging", "gui"
    ]
    
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

    return config
