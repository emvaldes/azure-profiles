#!/usr/bin/env python3

"""
Test Module: test_serialize_utils.py

This module contains unit tests for the `serialize_utils.py` module in `appflow_tracer.lib`.
It ensures that serialization and string sanitization functions operate correctly, including:

- Safe JSON serialization
- String sanitization for code parsing

## Use Cases:
1. **Validate JSON serialization with `safe_serialize()`**
   - Ensures standard Python objects serialize correctly to JSON.
   - Handles non-serializable objects gracefully.
   - Verifies `verbose=True` outputs formatted JSON.

2. **Ensure `sanitize_token_string()` removes inline comments**
   - Strips comments from code strings while preserving meaningful text.
   - Handles different edge cases, including empty strings and special characters.

## Improvements Implemented:
- `safe_serialize()` now **handles non-serializable objects** without crashing.
- `sanitize_token_string()` **properly removes comments** without affecting valid code.
- The test **isolates serialization behavior** to prevent interference from logging/tracing.

## Expected Behavior:
- **Valid JSON is returned for serializable objects**.
- **Non-serializable objects return fallback representations**.
- **Inline comments are removed while preserving valid code**.

Author: Eduardo Valdes
Date: 2025/01/01
"""

import sys
import os

import pytest
import json

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib.system_variables import category
from packages.appflow_tracer.tracing import setup_logging

from packages.appflow_tracer.lib.serialize_utils import (
    safe_serialize,
    sanitize_token_string
)

CONFIGS = setup_logging(logname_override='logs/tests/test_serialize_utils.log')
CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints

# Test safe_serialize function
def test_safe_serialize():
    """Ensure `safe_serialize()` correctly converts objects to JSON strings with metadata."""

    # Test valid JSON serialization
    result = safe_serialize({"key": "value"}, configs=CONFIGS)
    assert result["success"] is True
    assert json.loads(result["serialized"]) == {"key": "value"}
    assert result["type"] == "dict"

    result_verbose = safe_serialize({"key": "value"}, configs=CONFIGS, verbose=True)
    assert result_verbose["success"] is True
    assert json.loads(result_verbose["serialized"]) == {"key": "value"}
    assert result_verbose["type"] == "dict"

    # Test primitive data types
    assert safe_serialize(123, configs=CONFIGS)["serialized"] == "123"
    assert json.loads(safe_serialize([1, 2, 3], configs=CONFIGS)["serialized"]) == [1, 2, 3]

    # Test handling of non-serializable objects
    result_unserializable = safe_serialize(object(), configs=CONFIGS)
    # print("DEBUG: safe_serialize(object()) ->", result_unserializable)
    assert result_unserializable["success"] is False

    assert result_unserializable["serialized"] == "[Unserializable data]"
    assert "error" in result_unserializable
    assert result_unserializable["type"] == "object"

# Test sanitize_token_string function
def test_sanitize_token_string():
    """Ensure `sanitize_token_string()` removes comments while keeping code intact."""
    assert sanitize_token_string("some_code()  # this is a comment") == "some_code()"
    assert sanitize_token_string("   another_line   ") == "another_line"
    assert sanitize_token_string("print(123)  # inline comment") == "print(123)"
    assert sanitize_token_string("# full line comment") == ""
    assert sanitize_token_string("") == ""
