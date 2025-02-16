#!/usr/bin/env python3

"""
File Path: ./lib/system_variables.py

Description:

System-Wide Configuration Paths and Variables

This module defines system-wide constants and configuration file paths
that serve as references throughout the framework.

Core Features:

- **Standardized Configuration Paths**: Defines paths for `.env`, `runtime-params.json`, etc.
- **Project Root Management**: Establishes a unified reference for directory traversal.
- **Dynamic Configuration Aggregation**: Aggregates available configuration files.
- **Log File Quota Management**: Restricts the number of stored logs for efficiency.

Primary Variables:

- `project_root`: Base directory for resolving project files.
- `env_filepath`: Location of the `.env` file for runtime parameters.
- `runtime_params_filepath`: Stores dynamically generated runtime parameters.
- `system_params_filepath`: Stores global system-wide configurations.
- `project_params_filepath`: Stores project-level configurations.
- `default_params_filepath`: Defines framework default parameters.
- `system_params_listing`: Aggregates configuration sources dynamically.
- `max_logfiles`: Restricts the number of stored logs (default: `5`).

Expected Behavior:

- Configuration paths should always resolve correctly, ensuring consistency.
- `max_logfiles` should ideally be configurable via an environment variable.
- System parameter files should be aggregated dynamically for flexibility.

Dependencies:

- `pathlib` (for filesystem path handling)

Usage:

This module is imported wherever system-wide file path references are required.
"""


from pathlib import Path

"""
The root directory of the project.
This is used to resolve paths for all configurations and logs dynamically.
"""
project_root = Path(__file__).resolve().parent.parent


"""
Directory path where all log files are stored.
Logs are structured under `logs/<package-name>/<module-name>-<timestamp>.log`.
"""
project_logs = project_root / "logs"

"""
Directory path where all Python packages (`packages/`) are stored.
"""
project_packages = project_root / "packages"

"""
Path to the `.env` file containing runtime environment variables.
Used by the `dotenv` package for loading environment configurations dynamically.
"""
env_filepath = project_root / ".env"

"""
Path to the `runtime-params.json` file.
This file is dynamically generated at runtime by merging system-wide (`default-params.json`)
and project-specific (`project-params.json`) parameters.
"""
runtime_params_filename = "runtime-params.json"
runtime_params_filepath = project_root / "configs" / runtime_params_filename

"""
Path to the `system-params.json` file.
This file stores global system-wide configurations.
"""
system_params_filename = "system-params.json"
system_params_filepath = project_root / "configs" / system_params_filename

"""
Path to the `project-params.json` file.
This file stores project-specific configurations, typically customized by the user.
"""
project_params_filename = "project-params.json"
project_params_filepath = project_root / "configs" / project_params_filename

"""
Path to the `default-params.json` file.
This file contains standardized, framework-wide default parameters.
"""
default_params_filename = "default-params.json"
default_params_filepath = project_root / "configs" / default_params_filename

"""
List of JSON configuration files used for system parameter aggregation.

Includes:
- `project-params.json`
- `default-params.json`
"""
system_params_listing = [
    project_params_filepath,
    default_params_filepath
]

"""
Maximum number of log files allowed per module.
If the number of logs exceeds this limit, older logs are pruned automatically.
Default: `5`
"""
max_logfiles = 5
