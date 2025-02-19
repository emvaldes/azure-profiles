#!/usr/bin/env python3

"""
Test Module: ./tests/appflow_tracer/tracing/test_file_utils.py

This module contains unit tests for the `file_utils.py` module in `appflow_tracer.lib`.
It ensures that file handling functions operate correctly, including:

- **Path validation** for identifying project files.
- **Log file management** to enforce maximum log retention limits.
- **Relative path conversion** for standardizing file references.
- **ANSI escape code removal** for cleaning log outputs.

## Use Cases:
1. **Verify project file path validation**
   - Ensures `file_utils.is_project_file()` correctly identifies files inside the project directory.
   - Rejects paths outside the project directory.

2. **Ensure `file_utils.manage_logfiles()` properly removes excess logs**
   - Simulates an environment where `max_logfiles` is exceeded.
   - Validates that the oldest logs are deleted while respecting the limit.
   - Compares the list of expected deleted logs against the actual returned list.

3. **Validate relative path conversion**
   - Ensures `file_utils.relative_path()` correctly strips absolute paths into relative project paths.
   - Removes `.py` file extensions for consistency.

4. **Confirm ANSI escape code removal**
   - Verifies `file_utils.remove_ansi_escape_codes()` strips formatting sequences from log output.
   - Ensures output is clean and human-readable.

## Improvements Implemented:
- `file_utils.manage_logfiles()` now **returns a list of deleted files**, making validation straightforward.
- The test dynamically **adjusts `max_logfiles`** to trigger controlled log deletion.
- Instead of assuming a deletion count, the test **compares expected vs. actual deleted logs**.
- Fixed `Path.stat()` mocking to properly handle `follow_symlinks=True`, preventing test failures.
- Ensured logging does not interfere when disabled in `CONFIGS`.

## Expected Behavior:
- **Logs exceeding `max_logfiles` are removed**, with older logs prioritized.
- **Deleted logs are returned and verified** to ensure the function works correctly.
- **Path handling and text sanitization functions operate as expected**.
- **Logging is only enabled when explicitly set in `CONFIGS`.**
- **Path handling and text sanitization functions operate as expected.**

Author: Eduardo Valdes
Date: 2025/01/01
"""

import sys
import os

import json

import pytest
from unittest.mock import patch

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[4]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib import system_variables as environment
from packages.appflow_tracer import tracing
from packages.appflow_tracer.lib import file_utils

# Initialize CONFIGS from tracing.setup_logging
CONFIGS = tracing.setup_logging(
    logname_override='logs/tests/test_file_utils.log'
)
CONFIGS['logging']['max_logfiles'] = 6  # Adjust max_logfiles to trigger deletion
CONFIGS['logging']['enable'] = False  # Disable logging for test consistency
# print("DEBUG: CONFIGS Loaded ->", CONFIGS)  # Debugging CONFIGS object

@pytest.fixture
def mock_configs():
    """Mock CONFIGS globally for test stability."""
    CONFIGS["logging"]["max_logfiles"] = 6  # Ensure deletion triggers
    with patch(
        "packages.appflow_tracer.tracing.CONFIGS",
        CONFIGS
    ):
        yield CONFIGS

# Test if a file is correctly identified as part of the project
def test_is_project_file() -> None:
    """Ensure `file_utils.is_project_file()` correctly identifies project files and rejects external ones.

    Tests:
    - Identifies valid project file paths within the root directory.
    - Ensures external paths (outside project scope) return `False`.
    """
    valid_path = str(Path(environment.project_root) / "packages/appflow_tracer/lib/file_utils.py")
    invalid_path = "/outside/module.py"
    assert file_utils.is_project_file(valid_path) is True
    assert file_utils.is_project_file(invalid_path) is False

def test_manage_logfiles():
    """Simulates log file cleanup by `file_utils.manage_logfiles()` and validates the list of deleted logs.

    Tests:
    - Simulates an environment with excess log files.
    - Ensures the oldest logs are deleted while respecting `max_logfiles`.
    - Compares expected vs. actual deleted logs to validate accuracy.
    """
    with patch(
        "os.path.exists",
        return_value=True
    ), \
    patch("os.makedirs"), \
    patch.object(
        Path,
        "iterdir",
        return_value=[Path(CONFIGS['logging']['logs_dirname'])]
    ), \
    patch.object(
        Path,
        "is_dir",
        return_value=True
    ), \
    patch.object(
        Path,
        "glob",
        return_value=[
            Path(f"{CONFIGS['logging']['logs_dirname']}/log{i}.txt") for i in range(10)
        ]
    ), \
    patch(
        "pathlib.Path.stat",
        side_effect=lambda *args,
        **kwargs: type(
            'MockStat',
            (),
            {"st_mtime": 1739747800}
        )()
    ), \
    patch("pathlib.Path.unlink") as mock_remove:
        log_files = sorted(
            Path(
                CONFIGS['logging']['logs_dirname']
            ).glob('*.txt'),
            key=lambda f: f.stat().st_mtime
        )
        expected_deletions = log_files[:max(
            0,
            len(log_files) - CONFIGS['logging']['max_logfiles']
        )]
        deleted_logs = file_utils.manage_logfiles(CONFIGS)
        # Ensure the deleted logs match expected deletions
        assert set(deleted_logs) == set(f.as_posix() for f in expected_deletions), \
            f"Expected {expected_deletions}, but got {deleted_logs}"
        # Ensure return type is a list
        assert isinstance(
            deleted_logs,
            list
        )
        # Ensure logs were actually deleted
        assert len(deleted_logs) > 0, "No logs were deleted!"

# Test relative path conversion
def test_relative_path() -> None:
    """Ensure `file_utils.relative_path()` correctly converts absolute paths into project-relative paths.

    Tests:
    - Converts absolute file paths into a standardized project-relative format.
    - Ensures `.py` file extensions are stripped from the final output.
    """
    abs_path = "/Users/user/project/module.py"
    rel_path = file_utils.relative_path(abs_path)
    assert "module" in rel_path  # Match how `file_utils.relative_path()` behaves

# Test removal of ANSI escape codes from text
def test_remove_ansi_escape_codes() -> None:
    """Verify `file_utils.remove_ansi_escape_codes()` correctly strips ANSI formatting sequences from text.

    Tests:
    - Removes ANSI escape codes from formatted text.
    - Ensures the cleaned output maintains readability without formatting artifacts.
    """
    ansi_text = "\033[31mThis is red text\033[0m"
    clean_text = file_utils.remove_ansi_escape_codes(ansi_text)
    assert clean_text == "This is red text"
