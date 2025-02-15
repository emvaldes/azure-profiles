#!/usr/bin/env python3

"""
File Path: packages/appflow_tracer/lib/__init__.py

Description:

AppFlow Tracer Library Initialization

This file marks the `lib` directory as a valid Python subpackage. It serves as a
container for utilities and modules that support the appflow_tracer’s core
functionality.

Features:

- Defines the `lib` subpackage structure.
- Exposes specific submodules for logging, file operations, and utility functions.
- Allows these modules to be used throughout the appflow_tracer package.

Submodules:
- `log_utils`: Contains functions for structured logging and message handling.
- `file_utils`: Provides utilities for file and directory management.
- `config_loader`: Offers tools for reading and parsing configuration files.

Usage:
To use functions from this library:
```python
from packages.appflow_tracer.lib import log_utils, file_utils

log_utils.log_message("Log message example")
file_utils.manage_logfiles()
"""

# Import and expose key submodules
from . import (
    log_utils,
    file_utils,
    trace_utils,
    serialize_utils
)

__all__ = [
    "log_utils",
    "file_utils",
    "trace_utils",
    "serialize_utils"
]
