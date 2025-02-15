#!/usr/bin/env python3

import json  # If structured data is part of logging
import logging

from datetime import datetime  # If timestamps are used or manipulated

"""
Logging Utilities (log_utils.py)

log_message(): Handles structured logging logic.
output_logfile(): Manages writing log entries to log files.
output_console(): Directs logging output to the console with formatting.
"""

def log_message(
    message: str,
    category: str = "INFO",
    json_data: dict = None,
    serialize_json: bool = False,
    configs: dict = None
) -> None:
    """
    Logs a structured message to the appropriate logger and optionally outputs it to the console.

    This function supports various log levels, appends additional data in JSON format,
    and ensures that all logs follow a consistent structured format. It also integrates
    with the global configurations to determine logging behavior.

    Args:
        message (str): The message text to be logged.
        category (str): The logging category (e.g., "INFO", "WARNING", "ERROR").
        json_data (dict, optional): Additional structured data to log alongside the message.
        serialize_json (bool, optional): If True, the `json_data` is serialized to a JSON string.
        configs (dict, optional): A configuration dictionary. Defaults to the global `CONFIGS`.

    Returns:
        None

    Example:
        >>> log_message("This is an info message")
        >>> log_message("This is a warning", category="WARNING")
        >>> log_message("Structured log", json_data={"key": "value"})
    """

    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    logger = logging.getLogger(f"{configs['logging']['package_name']}.{configs['logging']['module_name']}")  # Use full module logger name

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
    Writes a log message to the file associated with the given logger.

    The function appends the structured log message and any additional JSON
    data to the log file, ensuring a consistent format and order. It does not
    print anything to the console.

    Args:
        logger (logging.Logger): The logger instance used for writing the log.
        message (str): The main log message text.
        json_data (dict, optional): Additional structured data to include in the log entry.

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
    Outputs a log message to the console with optional colored formatting.

    This function formats the given message according to the specified logging category
    and appends any JSON data provided. It uses the configurations to determine color
    coding and ensures that console output is distinct from file-based logging.

    Args:
        message (str): The message text to print.
        category (str): The logging category (e.g., "INFO", "WARNING", "ERROR").
        json_data (dict, optional): Additional structured data to print.
        configs (dict, optional): A configuration dictionary for colors and formatting.

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
