#!/usr/bin/env python3

"""
File Path: packages/appflow_tracer/__main__.py

Description:

AppFlow Tracing Package Entry Point

This file serves as the entry point for executing the `appflow_tracer` package in standalone mode.
It initializes the logging system using `setup_logging()`.

Features:

- Ensures structured logging is initialized when executed directly.
- Provides a standalone execution mode for quick validation.
- Supports `python -m packages.appflow_tracer` execution.

Usage:

> python -m packages.appflow_tracer
"""
import json
from .tracing import setup_logging

if __name__ == "__main__":
    CONFIGS = setup_logging()
    # print("Logging system initialized via standalone execution.")
