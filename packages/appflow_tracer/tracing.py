#!/usr/bin/env python3

"""
File Path: packages/appflow_tracer/tracing.py

Description:

AppFlow Tracing System

This module provides structured logging and tracing functionality within the framework,
enabling automatic function call tracking, detailed execution monitoring, and structured logging
to both console and file. It captures function call details, manages structured logs, and
supports self-inspection when run directly, all without requiring changes to existing function behavior.

Core Features:
- Function Call Tracing: Captures function calls, arguments, and return values dynamically.
- Structured Logging: Logs execution details in JSON format, supporting both console and file output.
- Self-Inspection: When executed directly, logs its own execution flow for debugging purposes.
- Automatic Log Management: Controls log file retention to prevent excessive storage use.

Primary Functions:
- `main()` – Entry point for self-executing the module for tracing.
- `setup_logging(configs)` – Configures and initializes global logging.

Dependencies:
Python Standard Library:
- `sys` → Interacts with runtime environment and manages import paths.
- `inspect` → Enables function call tracking.
- `datetime` → Handles timestamped logging.
- `logging` → Manages structured log entries.
- `builtins` → Intercepts standard `print()` for structured logging.
- `json` → Serializes logs in structured JSON format.
- `re` → Supports regular expressions for log sanitization.
- `pathlib` → Manages file paths and log directories.

Project Dependencies:

- `file_utils`: Provides file handling utilities.
    - `file_utils.is_project_file(filename)` – Determines if a file belongs to the project’s directory structure.
    - `file_utils.manage_logfiles()` – Cleans up old log files to maintain storage limits.
    - `file_utils.relative_path(filepath)` – Converts an absolute path to a project-relative path.
    - `file_utils.remove_ansi_escape_codes(text)` – Strips ANSI codes from strings.

- `log_utils`: Manages structured logging.
    - `log_utils.log_message(message, category, json_data, ...)` – Logs messages with structured output.
    - `log_utils.output_console(message, category, json_data, configs)` – Prints structured logs to the console.
    - `log_utils.output_logfile(logger, message, json_data)` – Writes log entries to a log file.

- `serialize_utils`: Handles serialization tasks.
    - `serialize_utils.safe_serialize(data, verbose)` – Safely serializes data into JSON format.
    - `serialize_utils.sanitize_token_string(line)` – Cleans up and formats source code strings.

- `trace_utils`: Contains tracing logic.
    - `trace_utils.start_tracing(configs)` – Initiates tracing for function calls and events.
    - `trace_utils.trace_all(configs)` – Main tracing logic to monitor call and return events.

- `lib.system_variables` → Defines project-wide configuration paths.
- `lib.pkgconfig_loader` → Loads and applies log-tracing configurations.

Usage:

To enable function call tracing and log execution details:
> python tracing.py ;
"""

import sys
import logging
import json

import builtins

from typing import Optional, Union
from pathlib import Path

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f"  - {path}")

# Import trace_utils from lib.*_utils
from .lib import (
    file_utils,
    log_utils,
    trace_utils
)

from lib import (
    pkgconfig_loader as pkgconfig
)

# ---------- Module functions:

def setup_logging(configs: Optional[dict] = None) -> Union[bool, dict]:
    """
    Configures and initializes the global logging system.

    This function sets up the logging environment, creating log files and
    adding handlers for both file-based and console-based logging. If no
    configuration is provided, it uses a default set of configurations to
    ensure proper logging behavior.

    Args:
        configs (dict, optional): A dictionary of logging configurations. If
        None, the global configurations will be used.

    Returns:
        dict: The effective configuration dictionary after applying any
        defaults or user-provided values.

    Example:
        >>> setup_logging()
        {
            "logging": {
                "log_filename": "/path/to/logfile.log",
                "max_logfiles": 10,
                ...
            },
            ...
        }
    """

    # Ensure the variable exists globally
    global LOGGING, CONFIGS, logger

    try:
        if not LOGGING:  # Check if logging has already been initialized
            LOGGING = True  # Mark logging as initialized
            # print(f'\n----------> Initializing Setup Logging ... \n')
    except NameError:
        return False

    if configs:
        print(f'Inheriting log-configs')
        CONFIGS = configs
    else:
        print(f'Initializing log-configs')
        CONFIGS = pkgconfig.setup_configs()
    # print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

    logfile = CONFIGS["logging"].get("log_filename", False)
    logger = logging.getLogger(f"{CONFIGS['logging']['package_name']}.{CONFIGS['logging']['module_name']}")
    logger.propagate = False  # Prevent handler duplication
    logger.setLevel(logging.DEBUG)

    # Ensure the log file directory exists
    Path(logfile).parent.mkdir(parents=True, exist_ok=True)

    # Remove existing handlers before adding new ones (Prevents duplicate logging)
    if logger.hasHandlers():
        logger.handlers.clear()  # Ensure handlers are properly cleared before adding new ones
    else:
        # Use ANSIFileHandler as logfile handler
        file_handler = ANSIFileHandler(logfile, mode='a')
        logger.addHandler(file_handler)
        # formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # file_handler.setFormatter(formatter)
        # file_handler.setLevel(logging.DEBUG)
        # Console handler (keeps ANSI color but ensures immediate output)
        console_handler = PrintCapture()
        logger.addHandler(console_handler)
        # console_handler.setFormatter(formatter)
        # console_handler.setLevel(logging.DEBUG)

    # Redirect print() statements to logger
    builtins.print = lambda *args, **kwargs: logger.info(" ".join(str(arg) for arg in args))
    # if CONFIGS["logging"].get("enable", False):
    #     builtins.print = lambda *args, **kwargs: sys.__stdout__.write(" ".join(str(arg) for arg in args) + "\n")

    # Ensure all logs are flushed immediately
    sys.stdout.flush()
    sys.stderr.flush()

    # if not LOGGING:  # Check if logging has already been initialized
    if CONFIGS["tracing"].get("enable", True):
        try:
            # start_tracing(CONFIGS)
            trace_utils.start_tracing(CONFIGS)
            print("🔍 \nTracing system initialized.\n")
        except NameError:
            return False

    return CONFIGS

class PrintCapture(logging.StreamHandler):
    """ Custom logging handler that captures print() and logs it while displaying in the console. """
    def emit(self, record):
        log_entry = self.format(record)
        sys.__stdout__.write(log_entry + "\n")  # Write to actual stdout
        sys.__stdout__.flush()  # Ensure immediate flushing

class ANSIFileHandler(logging.FileHandler):
    """Custom FileHandler that removes ANSI codes and filters out logging system entries."""
    def emit(self, record):
        # Ensure only Python's internal logging system is ignored
        if "logging/__init__.py" in record.pathname:
            return  # Skip internal Python logging module logs
        super().emit(record)  # Proceed with normal logging

# ---------- Module Global variables:

LOGGING = None
CONFIGS = None
logger = None  # Global logger instance

# ---------- Module operations:

def main():
    """
    Entry point for running the tracing module as a standalone program.

    When executed directly, this function sets up the logging environment,
    manages old log files, and optionally starts the tracing system. This
    is useful for self-inspection and verifying that all components of the
    module work correctly in isolation.

    Args:
        None

    Returns:
        None

    Example:
        >>> python tracing.py
        # Sets up logging, manages logs, and starts tracing.
    """

    global LOGGING, CONFIGS, logger  # Ensure CONFIGS is globally accessible

    # Ensure logging is set up globally before anything else
    CONFIGS = setup_logging()
    print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

    # Manage log files before starting new tracing session
    file_utils.manage_logfiles(CONFIGS)

    # Debug: Read and display log content to verify logging works
    try:
        log_file = CONFIGS["logging"].get("log_filename", False)
        print( f'\nReading Log-file: {log_file}' )
        with open(log_file, "r") as file:
            # print("\n📄 Log file content:")
            print(file.read())
    except Exception as e:
        print(f"⚠️ Unable to read log file: {e}")

# Automatically start tracing when executed directly
if __name__ == "__main__":
    main()
