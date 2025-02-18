#!/usr/bin/env python3

"""
File Path: lib/pkgconfig_loader.py

Description:

Package Configuration Loader

This module provides a centralized mechanism for dynamically loading
package-specific configurations. It ensures consistency across logging,
tracing, and runtime parameters.

Core Features:

- **Dynamic Configuration Loading**: Reads settings from JSON config files.
- **Logging Standardization**: Ensures uniform logging across all packages.
- **Self-Inspection Mechanism**: Determines module-specific log file paths.
- **Resilient JSON Parsing**: Handles corrupt or missing configuration files gracefully.

Primary Functions:

- `package_configs(overrides)`: Loads package configuration with optional overrides.
- `setup_configs(absolute_path, logname_override)`: Initializes logging configuration for a module.

Expected Behavior:

- If a config file is missing, a default one is created.
- JSON parsing errors trigger a warning and result in regeneration.
- Logging configurations are structured for uniformity across modules.

Dependencies:

- `os`, `sys`, `json`, `pathlib`, `datetime`
- `system_variables` (for directory paths and project settings)

Usage:

To load a package-specific configuration:
> from lib.pkgconfig_loader import package_configs
> config = package_configs()

To set up logging for a module:
> setup_configs("/path/to/module.py")
"""

import os
import sys
import json
import inspect

from typing import Optional, Union

from pathlib import Path
from datetime import datetime, timezone

from system_variables import (
    project_root,
    project_logs,
    project_packages,
    max_logfiles,
    default_indent,
    category
)

# Generate unique timestamp for log filename (avoiding collisions)
# timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

def config_logfile(
    config: dict,
    caller_log_path: str = None
) -> Path:
    """
    Determine the correct log file path based on the caller module's request or self-inspection.

    This function generates a log file path based on the provided configuration. If a
    specific caller log path is provided, it resolves the path accordingly; otherwise,
    it defaults to the logging directory specified in the configuration.

    Args:
        config (dict): The configuration dictionary containing logging settings.
        caller_log_path (str, optional): A specific log directory path requested by the caller.

    Returns:
        Path: The resolved path for the log file.
    """

    logs_dirname = Path(config["logging"]["logs_dirname"])
    if caller_log_path:
        log_path = Path(caller_log_path).resolve()
        return log_path / f"{config['logging']['package_name']}_{timestamp}.log"
    else:
        return logs_dirname / f"{config['logging']['package_name']}_{timestamp}.log"

def package_configs(overrides: dict = None) -> dict:
    """
    Load package configuration from a JSON file, or generate a default configuration if missing.

    This function attempts to load a package-specific configuration file. If the file is
    not found or is corrupted, a default configuration is generated, ensuring consistency
    across packages. The function supports overriding specific configuration keys.

    Args:
        overrides (dict, optional): A dictionary containing configuration values to override defaults.

    Raises:
        FileNotFoundError: If the JSON file is not found.
        json.JSONDecodeError: If the JSON file contains invalid syntax.

    Returns:
        dict: The loaded or generated package configuration.
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
                category.calls.id    : category.calls.color,     # Green
                category.returns.id  : category.returns.color,   # Yellow
                category.imports.id  : category.imports.color,   # Blue
                category.debug.id    : category.debug.color,     # Cyan
                category.info.id     : category.info.color,      # White
                category.warning.id  : category.warning.color,   # Red
                category.error.id    : category.error.color,     # Bright Red
                category.critical.id : category.critical.color,  # Red Background
                category.reset.id    : category.reset.color      # Reset to default
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
                "enable": True,
                "json": {
                    "compressed": True
                }
            },
            "events": {
                category.calls.id.lower(): True,
                category.returns.id.lower(): True,
                category.imports.id.lower(): True
            },
            "stats": {
                "created": datetime.now(timezone.utc).isoformat(),
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
        # print( f'Config Object: {json.dumps(config, indent=default_indent)}' )

        return config

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Error loading {config_file}: {e}")
        sys.exit(1)

def setup_configs(
    absolute_path: Path,
    logname_override: str = None,
    events: Optional[Union[bool, list, dict]] = None
) -> dict:
    """
    Dynamically initialize and update logging configuration for the calling module.

    This function identifies the calling module, determines its package structure,
    and ensures logging configuration is properly set up, including log directory
    creation and configuration file management.

    Args:
        absolute_path (Path): The absolute path of the module requesting logging setup.
        logname_override (str, optional): A custom name for the log file, if needed.
        events (dict, optional): Events control settings.

    Raises:
        RuntimeError: If the function is called in an environment where the module path cannot be determined.
        OSError: If an error occurs while reading or writing the configuration file.

    Returns:
        dict: The updated logging configuration for the module.
    """

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

    # print(f'Package Name: {package_name}\nModule Name: {module_name}')

    target_filename = absolute_path.stem
    # Determine expected configuration file path (stored in the package)
    config_file = Path(absolute_path.parent / f'{target_filename}.json')
    # print(f'\nConfig File: {config_file}')

    if not config_file.exists():
        # Ensure the parent directories exist
        config_file.parent.mkdir(parents=True, exist_ok=True)
        # Create the file if it does not exist
        config_file.touch(exist_ok=True)
        # print(f"Config File '{config_file}' created successfully.")

    config = None  # Default state if the file doesn't exist or is invalid

    if config_file.exists():
        try:
            # Try to open and read the file
            with open(config_file, "r") as f:
                content = f.read().strip()  # Read the content and strip whitespace
                # Check if the file is empty
                if not content:
                    # print(f"⚠️ {config_file} is empty. Regenerating...")
                    config = None
                else:
                    try:
                        # Attempt to parse as JSON
                        config = json.loads(content)
                        # Check if the structure is correct
                        if not isinstance(config, dict) or "logging" not in config:
                            # print(f"⚠️ {config_file} JSON structure is invalid. Regenerating...")
                            config = None
                        # else:
                        #     needs_update = True  # The file is valid and we just need to update the logging section
                    except json.JSONDecodeError:
                        # print(f"⚠️ {config_file} is not valid JSON. Regenerating...")
                        config = None
        except (OSError, IOError) as e:
            print(f"⚠️ Unable to read {config_file}: {e}")
            config = None  # Proceed to regenerate or handle as needed

    if config is None:
        config = package_configs()  # Call `package_configs()` to create a base config

    # Default event settings
    default_events = config["events"]
    # Transform `events` into the proper format
    if events is None or events is False:
        # Disable all event logging
        config["events"] = {key: False for key in default_events}
    elif events is True:
        # Enable all event logging
        config["events"] = {key: True for key in default_events}
    elif isinstance(events, list):
        # Enable only specified events
        config["events"] = {key: (key in events) for key in default_events}
    elif isinstance(events, dict):
        # Merge user-defined settings with defaults (keeping unspecified settings unchanged)
        config["events"] = {**default_events, **events}
    else:
        raise ValueError("Invalid `events` format. Must be None, bool, list, or dict.")

    # Ensure the "logging" section is properly updated
    logs_dirname = project_logs / package_name
    logs_dirname.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists
    target_logfile = logs_dirname.relative_to(project_root) / module_name
    # print( logs_dirname, target_logfile )

    config["logging"].update({
        "package_name": str(package_name),
        "module_name": str(module_name),
        "logs_dirname": str(logs_dirname.relative_to(project_root)),  # Relative path
        "log_filename": str(f'{target_logfile}.log')      # Relative path
    })
    # print(json.dumps(config, indent=4))

    # Update "updated" timestamp only if modifications were needed
    config["stats"]["updated"] = datetime.now(timezone.utc).isoformat()
    # Save the modified configuration to disk in the correct package location
    with open(config_file, "w") as f:
        json.dump(config, f, indent=default_indent)
    # print(f"Configuration updated: {config_file}")

    # Config -> Logging -> Log Filename (current log-file)
    config["logging"]["log_filename"] = str(f'{target_logfile}_{timestamp}.log')
    # print(json.dumps(config, indent=4))

    return config

if __name__ == "__main__":
    config = setup_configs()
    # print(json.dumps(config, indent=4))  # Print config for debugging
