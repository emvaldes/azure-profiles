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
  load_configs
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

def config_logfile(config, caller_log_path=None):
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
        logs_dirname = "logs"
        logs_basedir = str(project_root / logs_dirname)
        module_name = Path(__file__).stem
        package_name = Path(__file__).resolve().parent.name
        package_logs = str(project_logs / package_name)
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
                "max_logfiles": 10,
                "logs_dirname": logs_dirname,
                "package_name": package_name,
                "module_name": None,
                "package_logs": package_logs,
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

def __1setup_configs():
    """Dynamically initializes logging configuration for the calling module."""

    # Identify the calling module's file path
    caller_path = sys._getframe(1).f_globals.get("__file__", None)
    if caller_path is None:
        raise RuntimeError("Cannot determine calling module's file path. Ensure this function is called within a script, not an interactive shell.")

    # Convert to Path object before extracting details
    caller_path = Path(caller_path).resolve()

    # Identify the package directory and name correctly
    package_path = caller_path.parent
    package_name = package_path.name  # Correct package name

    module_name = caller_path.stem  # e.g., "enable_tracing" or "dependencies"

    # Determine expected configuration file path (stored next to module)
    config_file = package_path / f"{module_name}.json"

    # Step 1: Check if config file already exists
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)  # ✅ Load the existing configuration
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON format in {config_file}, regenerating...")
            config = None
    else:
        config = None  # If config file doesn't exist, we need to generate one

    # Step 2: If no valid config file, generate a new default config
    if config is None:
        config = package_configs()  # Call `package_configs()` to create a base config

        # Modify the configuration for the specific module
        logs_basedir = Path(config["logging"]["logs_basedir"])  # Ensure correct base logs path
        package_logs = logs_basedir / package_name  # Ensure logs are inside correct package

        config["logging"].update({
            "package_name": package_name,
            "module_name": module_name,
            "logs_basedir": str(logs_basedir),  # Store base logs path
            "package_logs": str(package_logs),  # Store logs inside correct package
            "log_filename": str(package_logs / f"{module_name}.log")  # Static log file name
        })

        # Save the modified configuration to disk in the correct package location
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuration saved: {config_file}")

    # Step 3: Dynamically update `log_filename` at runtime (without modifying the file)

    logs_basedir = Path(config["logging"]["logs_basedir"])  # Ensure correct log directory
    package_logs = logs_basedir / package_name  # Ensure logs go inside correct package directory

    # Ensure log directory exists
    package_logs.mkdir(parents=True, exist_ok=True)

    # Generate unique timestamp for log filename (avoiding collisions)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]

    # Dynamically update `log_filename` at runtime (but do not modify the saved config file)
    config["logging"]["log_filename"] = str(package_logs / f"{module_name}_{timestamp}.log")

    # Step 4: Return the final configuration (with updated log filename)
    return config

def setup_configs():
    """Dynamically initializes logging configuration for the calling module."""

    # Identify the calling module's file path
    caller_path = sys._getframe(1).f_globals.get("__file__", None)
    if caller_path is None:
        raise RuntimeError("Cannot determine calling module's file path. Ensure this function is called within a script, not an interactive shell.")

    # Convert to Path object before extracting details
    caller_path = Path(caller_path).resolve()

    # Identify the project root directory (Assumes package is inside `packages/`)
    project_root = caller_path.parents[2]

    # Identify the package directory and name
    package_path = caller_path.parent
    package_name = package_path.name
    module_name = caller_path.stem  # e.g., "enable_tracing" or "dependencies"

    # Determine expected configuration file path (stored in the package)
    config_file = package_path / f"{module_name}.json"

    config = None  # Default state if the file doesn't exist or is invalid
    needs_update = False  # Flag to determine if the file requires updates

    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)  # ✅ Load the existing configuration
                if not isinstance(config, dict) or "logging" not in config:
                    print(f"⚠️ Invalid JSON structure in {config_file}, regenerating...")
                    config = None  # Force regeneration if structure is incorrect
                else:
                    needs_update = True  # If valid, we only update the logging section
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON format in {config_file}, regenerating...")
            config = None  # Force regeneration if decoding fails

    if config is None:
        config = package_configs()  # Call `package_configs()` to create a base config

        # Ensure log paths are stored as **relative** to `project_root`
        package_logs = project_root / "logs" / package_name
        package_logs.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists

        needs_update = True  # Mark for saving since it's newly created

    # Ensure the "logging" section is properly updated
    package_logs = project_root / "logs" / package_name
    config["logging"].update({
        "package_name": package_name,
        "module_name": module_name,
        "package_logs": str(package_logs.relative_to(project_root)),  # ✅ Relative path
        "log_filename": str((package_logs / f"{module_name}.log").relative_to(project_root))  # ✅ Relative path
    })

    # Update "updated" timestamp only if modifications were needed
    if needs_update:
        config["stats"]["updated"] = datetime.utcnow().isoformat()

        # Save the modified configuration to disk in the correct package location
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuration updated: {config_file}")

    # Generate unique timestamp for log filename (avoiding collisions)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]

    # Update `log_filename` at runtime (without modifying the saved config file)
    config["logging"]["log_filename"] = str((package_logs / f"{module_name}_{timestamp}.log").relative_to(project_root))

    return config

if __name__ == "__main__":
    config = setup_configs()
    print(json.dumps(config, indent=4))  # Print config for debugging
