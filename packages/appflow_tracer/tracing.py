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

- **Function Call Tracing**: Captures function calls, arguments, and return values dynamically.
- **Structured Logging**: Logs execution details in JSON format, supporting both console and file output.
- **Self-Inspection**: When executed directly, logs its own execution flow for debugging purposes.
- **Automatic Log Management**: Controls log file retention to prevent excessive storage use.

Expected Behavior:

- Logs execution details automatically when tracing is enabled.
- Logs function calls with arguments and return values.
- Logs are stored in a structured format for debugging and analysis.

Dependencies:

- `sys`, `json`, `inspect`, `datetime`, `logging`, `builtins`, `pathlib`
- `packages.appflow_tracer.lib.file_utils` (for log file handling)
- `packages.appflow_tracer.lib.log_utils` (for structured logging)
- `packages.appflow_tracer.lib.trace_utils` (for tracing logic)
- `lib.system_variables`, `lib.pkgconfig_loader` (for configuration handling)

Usage:

To enable function call tracing and log execution details:
> python tracing.py
"""

import sys
import json
import inspect
import logging
import builtins
import warnings

from datetime import datetime
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

# Import system_variables from lib.system_variables
from lib.system_variables import (
    project_root,
    project_logs
)

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

def setup_logging(
    configs: Optional[dict] = None,
    logname_override: Optional[str] = None
) -> Union[bool, dict]:
    """
    Configures and initializes the global logging system.

    This function sets up the logging environment, creating log files and adding handlers
    for both file-based and console-based logging. It ensures proper logging behavior
    even when no configuration is provided.

    Args:
        configs (dict, optional): A dictionary containing logging configurations.
            If None, the default global configurations are used.
        logname_override (str, optional): A custom name for the log file.
            If None, the log file name is derived from the calling script.

    Raises:
        ValueError: If the provided logging configurations are not in a dictionary format.

    Returns:
        dict: The effective logging configuration after applying defaults.

    Example:
        >>> setup_logging()
        {
            "logging": {
                "log_filename": "/path/to/logfile.log",
                "max_logfiles": 5,
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
            # print(f'\nInitializing Setup Logging ... \n')
    except NameError:
        return False

    if logname_override:
        log_filename = logname_override
# else:
    # Inspect the stack to find the caller’s module name or file
    caller_frame = inspect.stack()[1]
    # Determine the caller's module or file
    caller_module = inspect.getmodule(caller_frame[0])

    if caller_module and caller_module.__file__:
        # Extract the script/module name without extension
        log_filename = Path(caller_module.__file__).stem
    else:
        # Fallback if the name can’t be determined
        log_filename = "unknown"

    # Handle the case where __main__ is used
    if log_filename == "__main__":
        # Use the module that defines setup_logging as a fallback
        current_frame = inspect.currentframe()
        this_module = inspect.getmodule(current_frame)
        if this_module and this_module.__file__:
            log_filename = Path(this_module.__file__).stem
        else:
            # Fallback if the name can’t be determined
            log_filename = "default"

    absolute_path = None
    # Construct the full log path separately
    if caller_module and caller_module.__file__:
        caller_path = Path(caller_module.__file__).resolve()
        absolute_path = caller_path.with_name(log_filename)
        if caller_path.is_relative_to(project_root):
            # If the caller is within project_root, construct a relative log path
            relative_path = caller_path.relative_to(project_root)
            log_filename = relative_path.parent / f"{log_filename}"
        else:
            # If the caller is outside project_root, just use its absolute path under logs
            log_filename = caller_path.parent.relative_to(caller_path.anchor) / f"{log_filename}"
    # else:
    #     # If we couldn’t determine the caller file, fallback to a default
    #     log_filename = f"default"

    # Determining configs parameter
    if configs:
        CONFIGS = configs
    else:
        CONFIGS = pkgconfig.setup_configs(
            absolute_path=Path(absolute_path),
            logname_override=log_filename
        )

    if not isinstance(CONFIGS, dict):
        raise ValueError("Configs must be a dictionary")
    # print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

    logfile = CONFIGS["logging"].get("log_filename", False)
    logger = logging.getLogger(f"{CONFIGS['logging']['package_name']}.{CONFIGS['logging']['module_name']}")
    logger.propagate = False  # Prevent handler duplication
    logger.setLevel(logging.DEBUG)

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

    # Redirect print function statements to logger
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
            trace_utils.start_tracing(
                logger=logger,
                configs=CONFIGS
            )
            # log_utils.log_message("🔍 \nTracing system initialized.\n", "INFO", configs=CONFIGS)
        except NameError:
            return False

    # Manage log files before starting new tracing session
    file_utils.manage_logfiles(CONFIGS)

    return CONFIGS

class PrintCapture(logging.StreamHandler):
    """
    Custom logging handler that captures print statements and logs them
    while ensuring they are displayed in the console.

    This ensures that print statements are properly logged without affecting
    real-time console output.
    """

    def emit(self, record):
        log_entry = self.format(record)
        sys.__stdout__.write(log_entry + "\n")  # Write to actual stdout
        sys.__stdout__.flush()  # Ensure immediate flushing

    def emit(self, record):
        log_entry = self.format(record)
        sys.__stdout__.write(log_entry + "\n")  # Write to actual stdout
        sys.__stdout__.flush()  # Ensure immediate flushing

class ANSIFileHandler(logging.FileHandler):
    """
    Custom FileHandler that removes ANSI codes from log output
    and filters out logs from the internal Python logging module.

    This prevents unnecessary ANSI escape codes from appearing in log files
    and ensures only relevant logs are recorded.
    """
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

    This function initializes the logging environment, manages log files, and
    optionally starts the tracing system when executed directly. It helps with
    self-inspection and ensures the module operates correctly in isolation.

    Raises:
        Exception: If logging setup fails or an unexpected error occurs.

    Returns:
        None

    Example:
        >>> python tracing.py
        # Sets up logging, manages logs, and starts tracing.
    """

    global LOGGING, CONFIGS, logger  # Ensure CONFIGS is globally accessible

    # Ensure logging is set up globally before anything else
    CONFIGS = setup_logging()
    # print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

# Automatically start tracing when executed directly
if __name__ == "__main__":
    main()

# # Debug: Read and display log content to verify logging works
# try:
#     log_file = CONFIGS["logging"].get("log_filename", False)
#     print( f'\nReading Log-file: {log_file}' )
#     with open(log_file, "r") as file:
#         # print("\n📄 Log file content:")
#         print(file.read())
# except Exception as e:
#     print(f"⚠️ Unable to read log file: {e}")
