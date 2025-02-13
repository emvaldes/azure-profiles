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

- os
- sys
- json
- pathlib
- datetime

- system_variables

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

import os
import sys
import json

from pathlib import Path
from datetime import datetime

from system_variables import (
    project_root,
    project_logs
)

def get_logfile(config, caller_log_path=None):
    """Determine the correct log file path based on the caller module's request or self-inspection."""
    package_logsdir = Path(config["logging"]["package_logs"])
    package_logsdir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if caller_log_path:
        log_path = Path(caller_log_path).resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        return log_path / f"{config['logging']['package_name']}_{timestamp}.log"
    else:
        return package_logsdir / f"{config['logging']['package_name']}_{timestamp}.log"

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
        log_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

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
                "logs_dirname": logs_dirname,
                "log_timestamp": log_timestamp,
                "package_name": package_name,
                "module_name": None,
                "logs_basedir": logs_basedir,
                "package_logs": package_logs,
                "log_filename": None
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
        config["logging"]["log_filename"] = str(get_logfile(config))  # Generate the log file path
        # print( f'Config Type:   {type( config )}' )
        # print( f'Config Object: {json.dumps(config, indent=2)}' )

        return config

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Error loading {config_file}: {e}")
        sys.exit(1)

import sys
import json
from pathlib import Path
from datetime import datetime

def setup_configs():
    """Dynamically initializes logging configuration for the calling module."""

    # Identify the calling module's file path
    caller_path = sys._getframe(1).f_globals.get("__file__", None)
    if caller_path is None:
        raise RuntimeError("Cannot determine calling module's file path. Ensure this function is called within a script, not an interactive shell.")

    # Convert to Path object before extracting details
    caller_path = Path(caller_path).resolve()
    package_name = caller_path.parent.name  # e.g., "appflow_tracer" or "requirements"
    module_name = caller_path.stem          # e.g., "enable_tracing" or "dependencies"

    # Use a default fallback or global override for logs location
    logs_basedir = globals().get("project_logs", Path.home() / ".logs")

    # Ensure log directories exist
    package_logs = logs_basedir / package_name
    package_logs.mkdir(parents=True, exist_ok=True)

    # Generate unique timestamp for log filename (avoiding collisions)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]
    log_filename = package_logs / f"{module_name}_{timestamp}.log"

    # Load configurations dynamically
    configs = load_configs({
        "logging": {
            "log_timestamp": timestamp,
            "package_name": package_name,
            "module_name": module_name,
            "logs_basedir": str(logs_basedir),   # ✅ Convert Path -> String
            "package_logs": str(package_logs),   # ✅ Convert Path -> String
            "log_filename": str(log_filename)    # ✅ Convert Path -> String
        }
    })

    return configs

if __name__ == "__main__":
    config = load_config()
    print(json.dumps(config, indent=4))  # Print config for debugging
