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
- Enables seamless integration with `tracing.py` and other logging utilities.
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
  load_configs
)

To execute and inspect the generated configuration:
> python pkgconfig_loader.py ;
"""

import os
import sys
import json
import inspect

from pathlib import Path
from datetime import datetime

from system_variables import (
    project_root,
    project_logs,
    project_packages,
    max_logfiles
)

# Generate unique timestamp for log filename (avoiding collisions)
# timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

def config_logfile(config, caller_log_path=None):
    """Determine the correct log file path based on the caller module's request or self-inspection."""
    logs_dirname = Path(config["logging"]["logs_dirname"])
    if caller_log_path:
        log_path = Path(caller_log_path).resolve()
        return log_path / f"{config['logging']['package_name']}_{timestamp}.log"
    else:
        return logs_dirname / f"{config['logging']['package_name']}_{timestamp}.log"

def package_configs(overrides=None):
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
        module_name = Path(__file__).stem
        package_name = Path(__file__).resolve().parent.name
        logs_dirname = str(project_logs / package_name)
        # log_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        config = {
            "colors": {
                "IMPORT": "\033[94m",  # Blue
                "CALL": "\033[92m",    # Green
                "RETURN": "\033[93m",  # Yellow
                "RESET": "\033[0m"     # Reset to default
            },
            "logging": {
                "enable": True,
                "max_logfiles": max_logfiles,
                "package_name": package_name,
                "module_name": None,
                "logs_dirname": logs_dirname,
                "log_filename": None
            },
            "tracing": {
                "enable": True
            },
            "stats": {
                "created": datetime.utcnow().isoformat(),
                "updated": None
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
        config["logging"]["log_filename"] = str(config_logfile(config))  # Generate the log file path
        # print( f'Config Type:   {type( config )}' )
        # print( f'Config Object: {json.dumps(config, indent=2)}' )

        return config

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Error loading {config_file}: {e}")
        sys.exit(1)

def setup_configs(absolute_path, logname_override=None):
    """Dynamically initializes logging configuration for the calling module."""

    # Identify the calling module's file path
    caller_path = sys._getframe(1).f_globals.get("__file__", None)
    if caller_path is None:
        raise RuntimeError("Cannot determine calling module's file path. Ensure this function is called within a script, not an interactive shell.")

    # Convert to Path object before extracting details
    caller_path = Path(caller_path).resolve()

    # Identify the package directory and name
    package_path = caller_path.parent
    package_name = package_path.name

    # Coller-specific location and naming
    if logname_override:
        module_name = logname_override

    # Check if given_path is in the hierarchy of check_path
    if project_packages in absolute_path.parents:
        module_name = absolute_path.relative_to(project_packages)
    package_name = module_name.parent
    module_name = module_name.stem

    print(f'Package Name: {package_name}\nModule Name: {module_name}')

    target_filename = absolute_path.stem
    # Determine expected configuration file path (stored in the package)
    config_file = Path(absolute_path.parent / f'{target_filename}.json')
    # print(f'\nConfig File: {config_file}')

    if not config_file.exists():
        # Ensure the parent directories exist
        config_file.parent.mkdir(parents=True, exist_ok=True)
        # Create the file if it does not exist
        config_file.touch(exist_ok=True)
        print(f"Config File '{config_file}' created successfully.")

    config = None  # Default state if the file doesn't exist or is invalid

    if config_file.exists():
        try:
            # Try to open and read the file
            with open(config_file, "r") as f:
                content = f.read().strip()  # Read the content and strip whitespace
                # Check if the file is empty
                if not content:
                    print(f"⚠️ {config_file} is empty. Regenerating...")
                    config = None
                else:
                    try:
                        # Attempt to parse as JSON
                        config = json.loads(content)
                        # Check if the structure is correct
                        if not isinstance(config, dict) or "logging" not in config:
                            print(f"⚠️ {config_file} JSON structure is invalid. Regenerating...")
                            config = None
                        # else:
                        #     needs_update = True  # The file is valid and we just need to update the logging section
                    except json.JSONDecodeError:
                        print(f"⚠️ {config_file} is not valid JSON. Regenerating...")
                        config = None
        except (OSError, IOError) as e:
            print(f"⚠️ Unable to read {config_file}: {e}")
            config = None  # Proceed to regenerate or handle as needed

    if config is None:
        config = package_configs()  # Call `package_configs()` to create a base config

    # Ensure the "logging" section is properly updated
    logs_dirname = project_logs / package_name
    logs_dirname.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists
    target_logfile = logs_dirname.relative_to(project_root) / module_name
    # print( logs_dirname, target_logfile )

    config["logging"].update({
        "package_name": str(package_name),
        "module_name": str(module_name),
        "logs_dirname": str(logs_dirname.relative_to(project_root)),  # Relative path
        "log_filename": str(f'{target_logfile}_{timestamp}.log')  # Relative path
    })
    # print(json.dumps(config, indent=4))

    # Update "updated" timestamp only if modifications were needed
    config["stats"]["updated"] = datetime.utcnow().isoformat()
    # Save the modified configuration to disk in the correct package location
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    # print(f"Configuration updated: {config_file}")
    # print(json.dumps(config, indent=4))

    return config

if __name__ == "__main__":
    config = setup_configs()
    print(json.dumps(config, indent=4))  # Print config for debugging
