#!/usr/bin/env python3

"""
File Path: ./lib/system_variables.py

Description:

System Variables and Configuration Paths

This module defines key system-wide variables, file paths, and configuration locations
that are referenced throughout the framework.

Features:

- Defines paths for essential configuration files (`.env`, `runtime-params.json`, etc.).
- Establishes the project root directory for consistent file access.
- Manages aggregated configuration sources for parameter merging.
- Restricts log file quota to maintain storage efficiency.

This module ensures a structured and consistent reference for file paths and configurations.

Dependencies:

- pathlib

Usage:

This module is imported where system-wide configuration file paths are needed.
"""

from pathlib import Path

## Project Root (path) for parent elements
project_root = Path(__file__).resolve().parent.parent
project_logs = project_root / "logs"

## Target .env file for the dotenv module (load_dotenv, dotenv_values)
env_filepath = project_root / ".env"

## ./configs/runtime-params.json: Runtime Configurations
runtime_params_filename = "runtime-params.json"
runtime_params_filepath = project_root / "configs" / runtime_params_filename

## ./configs/system-params.json: Global Configurations
system_params_filename = "system-params.json"
system_params_filepath = project_root / "configs" / system_params_filename

## ./configs/project-params.json: Project Global Configurations
project_params_filename = "project-params.json"
project_params_filepath = project_root / "configs" / project_params_filename

## ./configs/default-params.json: Defaults Global Configurations
default_params_filename = "default-params.json"
default_params_filepath = project_root / "configs" / default_params_filename

## Aggregated Parameters Configuration files.
system_params_listing = [ project_params_filepath, default_params_filepath ]

## Restricting ./.logs/* files quota
max_logfiles = 10
