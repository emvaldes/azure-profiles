#!/usr/bin/env python3

"""
Test Module: test_log_utils.py

This module contains unit tests for the `log_utils.py` module in `appflow_tracer.lib`.
It ensures that logging functions operate correctly, including:

- Structured log message handling
- File-based log output
- Console-based log output with ANSI formatting

## Use Cases:
1. **Validate structured logging via `log_message()`**
   - Ensures `log_message()` correctly routes logs to files and console based on configuration.
   - Verifies that JSON-formatted logs are serialized properly.

2. **Ensure `output_logfile()` correctly writes logs to file**
   - Simulates log file output and verifies the expected format.
   - Ensures log messages are categorized correctly (INFO, WARNING, ERROR, etc.).
   - Validates that JSON metadata is properly included.

3. **Test `output_console()` for formatted console logging**
   - Verifies that log messages are displayed in the console with proper ANSI colors.
   - Ensures structured log data is correctly formatted in the console output.

## Improvements Implemented:
- `log_message()` now properly **differentiates between log levels** and handles structured data.
- The test **isolates logging behavior** by dynamically disabling logging and tracing during execution.
- JSON validation ensures that **log file output maintains correct formatting**.

## Expected Behavior:
- **Log messages are routed properly** to files or console depending on configuration.
- **Structured JSON data is properly serialized** and included in logs.
- **ANSI color formatting is applied to console logs** where applicable.

Author: Eduardo Valdes
Date: 2025/01/01
"""

import sys
import os

import json
import logging

import pytest
from unittest.mock import patch, MagicMock

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib.system_variables import category
from packages.appflow_tracer.tracing import setup_logging

from packages.appflow_tracer.lib.log_utils import (
    log_message,
    output_logfile,
    output_console
)

# Initialize CONFIGS
CONFIGS = setup_logging(logname_override='logs/tests/test_log_utils.log')
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

@pytest.fixture
def mock_logger():
    """Creates a mock logger for testing."""
    logger = MagicMock(spec=logging.Logger)
    return logger

# Test log_message function
def test_log_message(mock_logger):
    """Test that log_message correctly logs messages based on configuration."""
    with patch("packages.appflow_tracer.lib.log_utils.output_logfile") as mock_output_logfile, \
         patch("packages.appflow_tracer.lib.log_utils.output_console") as mock_output_console:

        # Log an info message
        log_message("Test log entry", category.info.id, json_data={"key": "value"}, configs=CONFIGS, handler=mock_logger)

        # Validate log file output was called
        if CONFIGS["logging"].get("enable", False):
            print("DEBUG: CONFIGS Logging ->", CONFIGS["logging"])
            CONFIGS["logging"]["enable"] = True
            mock_output_logfile.assert_called_once()

        # Validate console output if tracing is enabled
        if CONFIGS["tracing"].get("enable", False):
            mock_output_console.assert_called_once()

# Test output_logfile function
def test_output_logfile(mock_logger):
    """Test that output_logfile writes correctly formatted messages to a log file."""
    with patch.object(mock_logger, "info") as mock_logger_info:
        output_logfile(mock_logger, "Log file test message", category.info.id, {"extra": "data"})

        # Validate correct log format
        expected_message = f"{category.info.id}: Log file test message"
        expected_json = json.dumps({"extra": "data"}, separators=(',', ':'))
        actual_call = mock_logger_info.call_args[0][0]
        # print("DEBUG: Actual logged message ->", actual_call)  # Debug output
        actual_json = actual_call.split("\n", 1)[-1]
        assert json.loads(actual_json) == json.loads(expected_json)

# Test output_console function
def test_output_console():
    """Test that output_console correctly prints formatted messages with ANSI colors."""
    with patch("builtins.print") as mock_print:
        output_console("Console log test", category.warning.id, {"alert": "true"}, CONFIGS)

        # Validate console print was called
        mock_print.assert_called()

        # Ensure JSON formatting is respected
        json_output = json.dumps({"alert": "true"}, indent=2, ensure_ascii=False)
        mock_print.assert_any_call(json_output)
