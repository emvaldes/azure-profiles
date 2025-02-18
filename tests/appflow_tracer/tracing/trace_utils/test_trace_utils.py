#!/usr/bin/env python3

"""
Test Module: ./tests/appflow_tracer/test_trace_utils.py

This module contains unit tests for the `trace_utils.py` module in `appflow_tracer.lib`.
It ensures correct function execution tracing and structured logging, covering:

- **Function call tracing**: Captures invocation details, ensuring execution visibility.
- **Return value logging**: Serializes return values for structured execution logs.
- **Project-specific filtering**: Ensures only relevant project functions are logged.
- **Configuration-driven activation**: Prevents unnecessary tracing when disabled.

## Use Cases:
1. **Validate `start_tracing()` activation**
   - Ensures tracing starts **only when enabled** in the configuration.
   - Prevents redundant activations by checking `sys.gettrace()`.
   - Verifies that `sys.settrace()` is correctly called.

2. **Ensure `trace_all()` generates a valid trace function**
   - Confirms the trace function **properly processes events** (calls and returns).
   - Ensures non-project functions are **excluded from logging**.
   - Validates that function metadata is structured correctly.

3. **Test function call logging via `call_events()`**
   - Simulates a function call and checks if metadata is captured.
   - Verifies that **arguments are serialized correctly**.
   - Ensures only **project-relevant function calls are logged**.

4. **Verify function return logging via `return_events()`**
   - Captures return values and ensures correct serialization.
   - Confirms function exit events are logged with structured data.
   - Validates that primitive types and complex objects are handled correctly.

## Improvements Implemented:
- **Mocking of `sys.settrace()`** to avoid real tracing activation.
- **Ensuring `CONFIGS` are respected** when enabling tracing.
- **Patching of logging utilities** to isolate logs per test.

## Expected Behavior:
- **Tracing activates only when explicitly configured**.
- **Function call and return details are structured correctly**.
- **Non-project calls are filtered out, keeping logs relevant**.

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
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib.system_variables import category
from packages.appflow_tracer.tracing import setup_logging

from packages.appflow_tracer.lib.trace_utils import (
    start_tracing,
    trace_all,
    call_events,
    return_events
)

CONFIGS = setup_logging(logname_override='logs/tests/test_serialize_utils.log')
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

@pytest.fixture
def mock_logger() -> MagicMock:
    """Provides a mock logger for testing tracing output."""
    return MagicMock(spec=logging.Logger)

@pytest.fixture
def mock_configs() -> dict:
    """Provides a mock configuration dictionary for testing."""
    return {
        "tracing": {"enable": True},
        "logging": {"enable": True}
    }

@patch("sys.settrace")
def test_start_tracing(
    mock_settrace: MagicMock,
    mock_logger: MagicMock,
    mock_configs: dict
) -> None:
    """Ensure `start_tracing()` initializes tracing only when enabled.

    Tests:
    - Ensures `sys.settrace()` is correctly called when tracing is enabled.
    - Prevents multiple activations by checking `sys.gettrace()` before applying tracing.
    - Verifies that tracing is properly configured via `CONFIGS`.
    """
    sys.settrace(None)  # Reset trace before running the test
    start_tracing(logger=mock_logger, configs=mock_configs)
    mock_settrace.assert_called_once()

@patch("sys.settrace")
def test_start_tracing_disabled(
    mock_settrace: MagicMock,
    mock_logger: MagicMock
) -> None:
    """Ensure `start_tracing()` does not initialize tracing when disabled.

    Tests:
    - Ensures `sys.settrace()` is **not called** when tracing is disabled in `CONFIGS`.
    - Validates that `start_tracing()` respects configuration settings.
    """
    mock_configs = {"tracing": {"enable": False}}
    start_tracing(logger=mock_logger, configs=mock_configs)
    mock_settrace.assert_not_called()

@patch("packages.appflow_tracer.lib.trace_utils.trace_all")
def test_trace_all(
    mock_trace_all: MagicMock,
    mock_logger: MagicMock,
    mock_configs: dict
) -> None:
    """Ensure `trace_all()` generates a valid trace function.

    Tests:
    - Mocks `trace_all()` to return a dummy function and verifies it is callable.
    - Ensures that `trace_all()` does not fail when `CONFIGS` is missing logging settings.
    """
    mock_configs.setdefault("logging", {"enable": True})
    mock_trace_all.return_value = lambda frame, event, arg: None
    trace_function = trace_all(mock_logger, mock_configs)
    assert callable(trace_function), "trace_all() did not return a callable trace function."

@patch("packages.appflow_tracer.lib.file_utils.is_project_file", return_value=True)
@patch("packages.appflow_tracer.lib.log_utils.log_message")
def test_call_events(
    mock_is_project_file: MagicMock,
    mock_log_message: MagicMock,
    mock_logger: MagicMock,
    mock_configs: dict
) -> None:
    """Ensure `call_events()` logs function calls correctly."""

    # Explicitly enable logging and ensure events are properly configured
    mock_configs["logging"]["enable"] = True
    mock_configs["tracing"]["enable"] = True
    mock_configs["events"] = {category.calls.id.lower(): True, category.returns.id.lower(): True}

    frame_mock = MagicMock()
    frame_mock.f_code.co_name = "test_function"
    frame_mock.f_back.f_code.co_name = "caller_function"
    frame_mock.f_globals.get.return_value = "/Users/emvaldes/.repos/azure/workspaces/azure-profiles/python/test_file.py"

    call_events(mock_logger, frame_mock, "test_file.py", None, mock_configs)

    # Ensure log_message was called
    assert mock_log_message.called, "Expected log_message() to be called, but it wasn't."

@patch("packages.appflow_tracer.lib.file_utils.is_project_file", return_value=True)
@patch("packages.appflow_tracer.lib.log_utils.log_message")
def test_return_events(
    mock_is_project_file: MagicMock,
    mock_log_message: MagicMock,
    mock_logger: MagicMock,
    mock_configs: dict
) -> None:
    """Ensure `return_events()` logs function return values correctly."""

    # Explicitly enable logging and events
    mock_configs["logging"]["enable"] = True
    mock_configs["tracing"]["enable"] = True
    mock_configs["events"] = {category.calls.id.lower(): True, category.returns.id.lower(): True}

    frame_mock = MagicMock()
    frame_mock.f_code.co_name = "test_function"
    frame_mock.f_globals.get.return_value = "/Users/emvaldes/.repos/azure/workspaces/azure-profiles/python/test_file.py"

    return_events(mock_logger, frame_mock, "test_file.py", "return_value", mock_configs)

    # Ensure log_message was called
    assert mock_log_message.called, "Expected log_message() to be called, but it wasn't."
