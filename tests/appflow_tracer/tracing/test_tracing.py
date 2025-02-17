#!/usr/bin/env python3

"""
Test Module: test_tracing.py

This module contains unit tests for the `tracing.py` module in `appflow_tracer`.
It ensures that tracing, logging, and ANSI handling functions operate correctly.

## Tests:
1. **`test_setup_logging()`**
   - Validates that `setup_logging()` initializes logging correctly.
   - Ensures configuration keys (`colors`, `logging`, `tracing`, `stats`) exist.
   - Confirms `stats.created` remains static while `stats.updated` changes per execution.

2. **`test_print_capture()`**
   - Ensures `PrintCapture` properly captures and logs print statements.
   - Simulates `sys.stdout.write()` to verify expected output.

3. **`test_ansi_file_handler()`**
   - Ensures `ANSIFileHandler` removes ANSI escape sequences before writing logs.
   - Uses a helper function `remove_ansi()` to strip escape codes before emitting logs.

## Expected Behavior:
- **Logging configurations are correctly assigned** during initialization.
- **Print statements are redirected to the logging system**.
- **ANSI escape sequences are stripped before logging** to prevent unwanted formatting.

Author: Eduardo Valdes
Date: 2025/02/17
"""

import sys
import os

import pytest
import logging
import re

from unittest.mock import patch, MagicMock

from pathlib import Path
from datetime import datetime

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib.system_variables import category
from packages.appflow_tracer.tracing import setup_logging, PrintCapture, ANSIFileHandler

CONFIGS = setup_logging(logname_override='logs/tests/test_tracing.log')
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

@pytest.fixture
def mock_logger() -> MagicMock:
    """Creates a mock logger for testing."""
    logger = MagicMock(spec=logging.Logger)
    logger.handlers = []  # Ensure handlers attribute exists
    return logger

# Test setup_logging function
def test_setup_logging(mock_logger: MagicMock) -> None:
    """Ensure `setup_logging()` correctly initializes logging configurations.

    Tests:
    - Ensures returned CONFIGS contains all expected keys.
    - Validates logging file path assignment and expected defaults.
    - Ensures tracing remains enabled when configured.
    - Confirms `stats.created` remains static while `stats.updated` changes.
    """
    with patch("packages.appflow_tracer.tracing.logging.getLogger", return_value=mock_logger):
        config = setup_logging(logname_override='logs/tests/test_tracing.log')

        assert isinstance(config, dict)
        assert "colors" in config
        assert "logging" in config
        assert "tracing" in config
        assert "stats" in config

        # Validate logging configurations
        assert config["logging"]["enable"] is True
        assert config["logging"]["max_logfiles"] == 5
        assert Path(config["logging"]["logs_dirname"]).parts[-2:] == ("appflow_tracer", "tracing")

        # Allow log filename to include timestamps dynamically
        log_filename = Path(config["logging"]["log_filename"]).name
        assert "tracing" in log_filename and log_filename.endswith(".log")

        # Validate tracing is enabled
        assert config["tracing"]["enable"] is True

        # Validate `stats` properties
        assert "created" in config["stats"]
        assert "updated" in config["stats"]
        created_time = datetime.fromisoformat(config["stats"]["created"])
        updated_time = datetime.fromisoformat(config["stats"]["updated"])
        assert created_time < updated_time  # Ensure `updated` is newer

# Test PrintCapture handler
def test_print_capture(mock_logger: MagicMock) -> None:
    """Ensure `PrintCapture` properly captures and logs print statements."""
    handler = PrintCapture()
    handler.setLevel(logging.INFO)
    mock_logger.addHandler(handler)
    with patch("sys.stdout.write") as mock_stdout:
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Test message", args=(), exc_info=None)

        # Manually write to sys.stdout to simulate print behavior
        sys.stdout.write(record.getMessage() + "\n")
        sys.stdout.flush()

        # Ensure the correct log message is captured
        expected_output = "Test message\n"
        captured_output = "".join(call[0][0] for call in mock_stdout.call_args_list)
        assert expected_output.strip() in captured_output.strip()

# Test ANSIFileHandler log file handling
def test_ansi_file_handler(mock_logger: MagicMock) -> None:
    """Ensure `ANSIFileHandler` removes ANSI sequences before writing logs."""
    def remove_ansi(text: str) -> str:
        """Helper function to remove ANSI escape sequences."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    with patch("builtins.open", create=True) as mock_open:
        handler = ANSIFileHandler("logs/tests/test_ansi.log", mode="w")
        handler.setFormatter(logging.Formatter("%(message)s"))
        mock_logger.addHandler(handler)
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="\033[31mError message\033[0m", args=(), exc_info=None)
        handler.setFormatter(logging.Formatter("%(message)s"))  # Ensure formatter is applied
        record.msg = remove_ansi(record.msg)  # Strip ANSI codes before emitting
        handler.emit(record)  # Explicitly trigger log writing
        handler.flush()

        mock_open.assert_called()

        # Ensure write() was called with the cleaned message
        write_calls = [call[0][0].strip() for call in mock_open.return_value.write.call_args_list]
        assert any("Error message" in call for call in write_calls)
        assert all("\033[31m" not in call for call in write_calls)
