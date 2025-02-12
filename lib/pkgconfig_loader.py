#!/usr/bin/env python3

"""
File Path: lib/pkgconfig_loader.py

Description:

Configuration Loader Module

This module provides a centralized function for loading configuration settings
for various packages in the framework. It dynamically loads settings from a JSON
configuration file if present, otherwise it falls back to predefined defaults.

Features:

- Checks for a module-specific JSON configuration file.
- Loads settings dynamically based on the package and module name.
- Provides logging configurations to standardize logging across the framework.
- Automatically determines logging paths based on the module executing it.
- Ensures consistent logging behavior across all packages.

Enhancements:

- Standardizes logging configurations across multiple packages.
- Avoids redundant code by centralizing configuration loading.
- Enables seamless integration with `enable_tracing.py` and other logging utilities.
- Supports future scalability for additional configuration parameters.

Dependencies:

- sys
- json
- datetime
- pathlib

Usage:

To use this module in other packages:

from lib.pkgconfig_loader import (
  load_config,
  get_logfile
)
CONFIG = load_config()
LOG_FILE = get_logfile(CONFIG)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

To execute and inspect the generated configuration:
> python pkgconfig_loader.py ;
"""

import json
import sys
import datetime

from pathlib import Path

from system_variables import (
    project_root,
    project_logs
)

def get_logfile(config, caller_log_path=None):
    """Determine the correct log file path based on the caller module's request or self-inspection."""
    package_logsdir = Path(config["logging"]["package_logs"])
    package_logsdir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if caller_log_path:
        log_path = Path(caller_log_path).resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        return log_path / f"{config['logging']['log_filename']}_{timestamp}.log"
    else:
        return package_logsdir / f"{config['logging']['log_filename']}_{timestamp}.log"

def load_configs(overrides=None):
    """
    Load configuration from a JSON file if present, otherwise use defaults.
    Args: overrides (dict): Dictionary with values to override defaults.
    Returns: tuple: The loaded configuration.
    """
    # config_file = Path(__file__).with_suffix(".json")
    config_file = project_root / "configs" / f"{Path(__file__).stem}.json"
    try:
        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)

        # print( f'Config File does not exists: {Path(config_file).stem}.json' )
        # Default configuration if JSON file is missing
        logs_dirname = "logs"
        logs_basedir = str(project_root / logs_dirname)
        module_name = Path(__file__).stem
        package_name = Path(__file__).resolve().parent.name
        package_logs = str(project_logs / package_name)
        log_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        config = {
            "colors": {
                "IMPORT": "\033[94m",  # Blue
                "CALL": "\033[92m",    # Green
                "RETURN": "\033[93m",  # Yellow
                "RESET": "\033[0m"     # Reset to default
            },
            "logging": {
                "enable_tracing": True,
                "enable_logging": True,
                "max_logfiles": 10,
                "logs_basedir": logs_basedir,
                "package_logs": package_logs,
                "log_timestamp": log_timestamp,
                "log_filename": module_name,
                "logs_dirname": logs_dirname,
                "package_name": package_name
            }
        }
        # Apply any overrides if provided
        if overrides:
            for key, value in overrides.items():
                if key in config:
                    config[key].update(value)  # Merge nested dictionaries
                else:
                    config[key] = value  # Add new keys

        # Generate log file path
        log_file = get_logfile(config)  # Generate the log file path

        # print( f'Config Type: {type( config )}' )
        # print( f'Config: {config}' )
        return config, log_file  # ✅ Ensure tuple is returned

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Error loading {config_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    config = load_config()
    print(json.dumps(config, indent=4))  # Print config for debugging
