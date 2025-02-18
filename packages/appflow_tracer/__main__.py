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

from .tracing import main
if __name__ == "__main__":
    main()
