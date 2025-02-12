#!/usr/bin/env python3

"""
File Path: lib/config_loader.py

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
> from lib.config_loader import load_config
> CONFIG = load_config()

To execute and inspect the generated configuration:
> python config_loader.py ;
"""

import json
import sys
import datetime

from pathlib import Path

from system_variables import (
    project_root
)

def load_config():
    """Load configuration from a JSON file if present, otherwise use defaults."""
    # config_file = Path(__file__).with_suffix(".json")
    config_file = project_root / "configs" / f"{Path(__file__).stem}.json"
    try:
        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)

        # Default configuration if JSON file is missing
        package_name = Path(__file__).resolve().parent.name
        logs_dirname = "logs"
        logs_basedir = str(project_root / logs_dirname)
        module_name = Path(__file__).stem
        package_logsdirname = str(project_root / logs_dirname / package_name)
        log_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        return {
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
                "package_logsdirname": package_logsdirname,
                "log_timestamp": log_timestamp,
                "log_filename": module_name,
                "logs_dirname": logs_dirname,
                "package_name": package_name
            }
        }

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Error loading {config_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    config = load_config()
    print(json.dumps(config, indent=4))  # Print config for debugging
