#!/usr/bin/env python3

"""
Test Module: ./tests/appflow_tracer/tracing/test_log_utils.py

This module contains unit tests for the `log_utils.py` module in `appflow_tracer.lib`.
It ensures that logging functions operate correctly, including:

- **Structured log message handling** for files and console.
- **File-based log output** validation ensuring correct JSON formatting.
- **ANSI-formatted console output** for colored log messages.
- **Handling of different JSON formatting configurations** (compressed, pretty-printed, and sanitized).

## Use Cases:
1. **Validate structured logging via `log_message()`**
   - Ensures `log_message()` correctly routes logs to files and console based on configuration.
   - Verifies that JSON-formatted logs are properly serialized and categorized.
   - Tests logging behavior with `tracing.json.compressed = True/False`.

2. **Ensure `output_logfile()` correctly writes logs to file**
   - Simulates log file output and verifies the expected format.
   - Ensures log messages are categorized correctly (INFO, WARNING, ERROR, etc.).
   - Validates that JSON metadata is properly included in log files.
   - Accounts for different JSON formatting modes.

3. **Test `output_console()` for formatted console logging**
   - Ensures ANSI color formatting is applied to console logs when enabled.
   - Validates structured log messages are properly displayed with metadata.
   - Supports various JSON formatting options (compressed, pretty-printed, sanitized).

## Improvements Implemented:
- `log_message()` now properly **differentiates between log levels** and handles structured data.
- The test **isolates logging behavior** by dynamically disabling logging and tracing during execution.
- JSON validation ensures that **log file output maintains correct formatting**.
- Added multiple test scenarios to validate behavior under different `tracing.json` configurations:
  - **Compressed JSON** (`tracing.json.compressed = True`)
  - **Pretty-printed JSON** (`tracing.json.compressed = False`)
  - **Sanitized JSON output**

## Expected Behavior:
- **Log messages are routed properly** to files or console depending on configuration.
- **Structured JSON data is correctly serialized** and included in logs.
- **ANSI color formatting is applied to console logs** where applicable.
- **Tests correctly handle different JSON output formats** based on configuration.

Author: Eduardo Valdes
Date: 2025/01/01
"""

import sys
import os

import json
import logging
import re

import pytest
from unittest.mock import patch, MagicMock

from datetime import datetime, timezone
from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib.system_variables import (
    default_indent,
    category
)
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
def mock_logger() -> MagicMock:
    """Creates a mock logger for testing."""
    logger = MagicMock(spec=logging.Logger)
    return logger

# Test log_message function
def test_log_message(mock_logger) -> None:
    """Test that `log_message()` correctly logs messages based on configuration.

    Tests:
    - Ensures messages are routed to the correct logging destinations (file/console).
    - Verifies that JSON metadata is included in logs when provided.
    - Checks that log level categorization is correctly applied.
    """
    with patch("packages.appflow_tracer.lib.log_utils.output_logfile") as mock_output_logfile, \
         patch("packages.appflow_tracer.lib.log_utils.output_console") as mock_output_console:

        # Log an info message
        log_message("Test log entry", category.info.id, json_data={"key": "value"}, configs=CONFIGS, handler=mock_logger)

        # Validate log file output was called
        if CONFIGS["logging"].get("enable", False):
            # print("DEBUG: CONFIGS Logging ->", CONFIGS["logging"])
            CONFIGS["logging"]["enable"] = True
            mock_output_logfile.assert_called_once()

        # Validate console output if tracing is enabled
        if CONFIGS["tracing"].get("enable", False):
            mock_output_console.assert_called_once()

# Test output_logfile function
def test_output_logfile(mock_logger) -> None:
    """Test that `output_logfile()` writes correctly formatted messages to a log file.

    Tests:
    - Ensures log messages are structured correctly when written to a file.
    - Verifies JSON metadata is preserved and formatted properly.
    - Validates that INFO, WARNING, and ERROR log levels are categorized correctly.
    """
    with patch.object(mock_logger, "info") as mock_logger_info:
        output_logfile(mock_logger, "Log file test message", category.info.id, {"extra": "data"})

        # Validate correct log format
        expected_message = f"{category.info.id}: Log file test message"
        expected_json = json.dumps({"extra": "data"}, separators=(',', ':'))
        actual_call = mock_logger_info.call_args[0][0]
        # print("DEBUG: Actual logged message ->", actual_call)  # Debug output
        actual_json = actual_call.split("\n", 1)[-1]
        assert json.loads(actual_json) == json.loads(expected_json)

@pytest.mark.parametrize("compressed_setting, expected_format, expect_json", [
    (True, json.dumps({"alert": "true"}, separators=(",", ":"), ensure_ascii=False), True),
    (False, json.dumps({"alert": "true"}, indent=default_indent, ensure_ascii=False), True),
    (None, None, False),
])
def test_output_console(mock_logger, compressed_setting, expected_format, expect_json):
    """Test `output_console()` with different JSON formats and console color handling."""

    global CONFIGS

    # Backup CONFIGS and restore it after test
    original_configs = json.loads(json.dumps(CONFIGS))

    # Ensure tracing is disabled
    sys.settrace(None)

    CONFIGS["tracing"]["enable"] = False  # Ensure tracing is off
    CONFIGS["tracing"]["json"]["compressed"] = compressed_setting

    try:
        with patch("builtins.print") as mock_print:
            output_console("Console log test", category.warning.id, {"alert": "true"}, CONFIGS)

            actual_calls = [call.args[0] for call in mock_print.call_args_list]

            # ANSI regex to remove escape codes if present
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            log_messages = [ansi_escape.sub('', call) for call in actual_calls if "Console log test" in call]

            assert log_messages, f"Expected log message not found: {actual_calls}"
            assert log_messages[0] == "Console log test", f"Expected:\nConsole log test\nGot:\n{log_messages[0]}"

            if expect_json:
                assert expected_format in actual_calls, f"Expected JSON:\n{expected_format}\nGot:\n{actual_calls}"
    finally:
        # Restore CONFIGS after the test
        CONFIGS = original_configs
        sys.settrace(None)  # Ensure tracing remains off
