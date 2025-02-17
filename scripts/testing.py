#!/usr/bin/env python3

"""
File Path: ./scripts/testing.py

Description:

Standalone Testing Script for Framework Logging

This script serves as a test module to verify logging and tracing capabilities.
It initializes structured logging via `packages.appflow_tracer.tracing`,
prints configuration details, and runs a simple test output.

Features:

- Configures logging using `tracing.setup_logging()`.
- Prints the loaded logging configuration in JSON format.
- Serves as a standalone script that can be run independently.

Expected Behavior:

- The script prints the structured logging configuration.
- Demonstrates logging setup and verification for debugging purposes.
- Can be used as a simple test script for logging functionality.

Dependencies:

- `packages.appflow_tracer.tracing` (for structured logging)
- `sys`, `json`, `logging`, `pathlib` (for system interaction and logging setup)

Usage:

To execute the test:
> python scripts/testing.py
"""

import sys
import json
import logging

from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from packages.appflow_tracer import tracing

def main() -> None:
    """
    Execute a standalone test to verify the structured logging system.

    This function:
    - Configures logging using `tracing.setup_logging()`.
    - Prints the loaded logging configuration in JSON format.
    - Displays a test output message.

    Expected Behavior:
    - The script prints structured logging configuration details.
    - Demonstrates the integration of logging setup in a simple, standalone script.

    Raises:
        Exception: If an error occurs during logging setup.

    Returns:
        None

    Example:
        >>> python scripts/testing.py
        CONFIGS: {
            "logging": { ... }
        }
        I am a stand-alone script minding my own business.
    """

    global LOGGING, CONFIGS, logger  # Ensure CONFIGS is globally accessible

    CONFIGS = tracing.setup_logging()
    print(f'CONFIGS: {json.dumps(CONFIGS, indent=2)}')

    print("I am a stand-alone script minding my own business")

if __name__ == "__main__":
    main()
