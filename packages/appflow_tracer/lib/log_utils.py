#!/usr/bin/env python3

"""
File Path: packages/appflow_tracer/lib/log_utils.py

Description:

Structured Logging Utilities

This module provides structured logging functionality, enabling detailed
logging to both console and log files. It supports logging levels,
custom formats, and structured data output.

Core Features:

- **Structured Log Messages**: Formats logs in a consistent manner.
- **Console and File Logging**: Sends logs to both console and files.
- **Custom Log Levels**: Supports INFO, WARNING, ERROR, DEBUG, etc.
- **ANSI Color Support**: Enables colored output for console logs.

Primary Functions:

- `log_message(message, category, json_data, serialize_json, configs, handler)`:
  Handles structured logging and directs output to the appropriate destination.
- `output_logfile(logger, message, json_data)`: Writes logs to a structured log file.
- `output_console(message, category, json_data, configs)`: Displays formatted logs in the console.

Expected Behavior:

- Logs are written to both the console and log files based on configuration settings.
- JSON data is formatted properly if included in log messages.
- Log categories map to appropriate logging levels (INFO, DEBUG, ERROR, etc.).

Dependencies:

- `json`, `logging`, `datetime`
- `CONFIGS` (global configuration dictionary, must be available)
- `file_utils` (for log file management)

Usage:

To log a structured message:
> log_message("This is a log entry", category="INFO", json_data={"key": "value"})

To log a message with a warning level:
> log_message("Something might be wrong", category="WARNING")
"""

import json  # If structured data is part of logging
import logging

from datetime import datetime  # If timestamps are used or manipulated

# Determine the correct logging level
log_levels = {
    "CALL": logging.INFO,     # Map CALL to INFO for clarity
    "RETURN": logging.DEBUG,  # Map RETURN to DEBUG
    "IMPORT": logging.WARNING,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

def log_message(
    message: str,
    category: str = "INFO",
    json_data: dict = None,
    serialize_json: bool = False,
    configs: dict = None,
    handler: logging.Logger = None
) -> None:
    """
    Log a structured message with optional JSON data to both console and log files.

    This function supports multiple log levels, formats messages in a structured manner,
    and appends additional structured JSON data if provided. The behavior is influenced
    by global configurations, such as whether logs should be written to a file or displayed
    on the console.

    Args:
        message (str): The main log message.
        category (str, optional): The log level/category (e.g., "INFO", "WARNING", "ERROR").
            Defaults to "INFO".
        json_data (dict, optional): Additional structured JSON data to log.
        serialize_json (bool, optional): If True, the `json_data` is serialized into a JSON string.
        configs (dict, optional): Configuration dictionary. Defaults to global `CONFIGS` if not provided.
        handler (logging.Logger, optional): The specific logger instance to use. Defaults to the global logger.

    Returns:
        None

    Example:
        >>> log_message("This is an info message")
        >>> log_message("This is a warning", category="WARNING")
        >>> log_message("Structured log", json_data={"key": "value"})
    """

    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    # Define logger if not available
    logger = handler or logging.getLogger(f"{configs['logging']['package_name']}.{configs['logging']['module_name']}")
    # print(f'Logger: {logger}')

    log_level = log_levels.get(category.upper(), logging.INFO)

    # If json_data exists, append it to the message
    if json_data:
        if serialize_json:
            # json_data = safe_serialize(json_data, verbose=serialize_json)
            json_data = json.dumps(json_data, separators=(",", ":"), ensure_ascii=False)

    if configs["logging"].get("enable", False) and not configs["tracing"].get("enable", False):
        if message.strip():
            output_logfile(logger, message, json_data or False)  # Write ONLY to log file if tracing is disabled

    if configs["tracing"].get("enable", False):
        if message.strip():
            output_console(message, category, json_data or False, configs)  # Write to console

def output_logfile(
    logger: logging.Logger,
    message: str,
    json_data: dict = None
) -> None:
    """
    Write a structured log message to a log file.

    This function appends the formatted log message to a log file associated with the
    given logger. If structured data (`json_data`) is provided, it is included in the
    log entry.

    Args:
        logger (logging.Logger): The logger instance used for writing logs.
        message (str): The log message text.
        json_data (dict, optional): Additional structured JSON data for the log entry.

    Returns:
        None

    Example:
        >>> logger = logging.getLogger("example_logger")
        >>> output_logfile(logger, "This is a log message", {"extra_key": "value"})
    """

    logfile_message = message
    if json_data:
        logfile_message += f"\n{json_data}"
    # Disabling the removal of ANSI escape codes allowing end-users to see the original output experience.
    # message = file_utils.remove_ansi_escape_codes(message)
    logger.info(logfile_message)  # Write to log file

def output_console(
    message: str,
    category: str,
    json_data: dict = None,
    configs: dict = None
) -> None:
    """
    Display a structured log message in the console with optional ANSI color formatting.

    This function formats the given message according to the specified logging category
    and appends structured JSON data if provided. ANSI color codes are applied based on
    the logging configuration.

    Args:
        message (str): The main message to display.
        category (str): The logging category (e.g., "INFO", "WARNING", "ERROR").
        json_data (dict, optional): Additional structured JSON data for output.
        configs (dict, optional): Configuration dictionary for colors and formatting.

    Returns:
        None

    Example:
        >>> output_console("This is an info message", "INFO")
        >>> output_console("This is a warning", "WARNING", {"details": "some data"})
    """

    color = configs["colors"].get(category.upper(), configs["colors"]["RESET"])
    if not color.startswith("\033"):  # Ensure it's an ANSI color code
        color = configs["colors"]["RESET"]
    console_message = f"{color}{message}{configs['colors']['RESET']}"
    print(console_message)  # Print colored message
    if json_data:
        if isinstance(json_data, str):
            # Print strings as-is (no JSON formatting)
            print(json_data)
        else:
            # Pretty-print JSON while keeping Unicode characters
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
