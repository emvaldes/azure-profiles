#!/usr/bin/env python3

"""
File Path: packages/appflow_tracer/__init__.py

Description: AppFlow Tracing Package Initialization

This file marks the `appflow_tracer` directory as a valid Python package.
It provides an entry point for the tracing functionality by exposing `setup_logging`,
which is the primary function needed for logging setup.

Features:

- Imports and exposes `setup_logging` as the main entry point.
- Allows the `appflow_tracer` package to be used as an importable module.

Usage:

To initialize logging:
    from packages.appflow_tracer import setup_logging
    CONFIGS = setup_logging()

To log messages:
    from packages.appflow_tracer import log_message
    log_message("This is a test log message.")
"""

# Export only necessary functions
from .tracing import (
    setup_logging
)

from .lib import (
    log_utils,
    file_utils,
    trace_utils,
    serialize_utils
)

# Explicitly define available functions
__all__ = [
    "setup_logging",
    "log_utils",
    "file_utils",
    "trace_utils",
    "serialize_utils"
]
