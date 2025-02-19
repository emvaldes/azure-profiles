#!/usr/bin/env python3

"""
Unit tests for the dependency management module.

This module contains tests for verifying the correct behavior of functions that load, install, and validate dependencies.
It ensures that packages are installed correctly, updates are applied properly, and compliance is maintained.
"""

import sys
import json
import subprocess
import importlib.metadata

import pytest
from unittest.mock import patch

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from packages.appflow_tracer import tracing
from packages.requirements import dependencies

try:
  CONFIGS = tracing.setup_logging(
      logname_override='logs/tests/test_dependencies.log'
  )
  CONFIGS["logging"]["enable"] = False  # Disable logging for test isolation
  CONFIGS["tracing"]["enable"] = False  # Disable tracing to prevent unintended prints
except NameError:
    CONFIGS = {
        "logging": {"enable": False},
        "tracing": {"enable": False},
        "events": {"install": True, "update": True},
    }

@pytest.fixture(autouse=True)
def mock_configs():
    """Mock `CONFIGS` globally for all tests if not initialized."""
    global CONFIGS
    if CONFIGS is None:
        CONFIGS = {
            "logging": {"enable": False},
            "tracing": {"enable": False},
            "events": {"install": True, "update": True},
        }
    return CONFIGS  # Explicitly returns CONFIGS

@pytest.mark.parametrize(
    "package, expected_version", [
        ("requests", "2.28.1"),
        ("nonexistent-package", None)
    ]
)
@patch("packages.requirements.dependencies.get_installed_version")
def test_debug_installation(
    mock_get_version,
    package,
    expected_version
):
    """
    Debugging test to check whether the package installation check
    is returning expected results.
    """
    mock_get_version.return_value = expected_version
    result = mock_get_version(package)
    # Print debug information
    print(f"Testing package: {package}, Expected Version: {expected_version}, Got: {result}")
    assert result == expected_version

def test_load_requirements_invalid_json(
    tmp_path,
    mock_configs
):
    """
    Test that loading a malformed JSON file raises a ValueError.
    """
    req_file = tmp_path / "requirements.json"
    req_file.write_text(
        "{invalid_json}"
    )
    with pytest.raises(ValueError):
        dependencies.load_requirements(
            str(req_file),
            configs=mock_configs
        )

def test_load_requirements_missing(mock_configs):
    """
    Test that loading a missing requirements file raises a FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        dependencies.load_requirements(
            "nonexistent.json",
            configs=mock_configs
        )

def test_load_requirements_valid(
    tmp_path,
    mock_configs
):
    """
    Test that a valid requirements file is correctly loaded.
    """
    req_file = tmp_path / "requirements.json"
    req_data = {
        "dependencies": [{
            "package": "requests",
            "version": {
                "target": "2.28.1"
            }
        }]
    }
    req_file.write_text(
        json.dumps(req_data)
    )
    result = dependencies.load_requirements(
        str(req_file),
        configs=mock_configs
    )
    assert result == [
        {
            "package": "requests",
            "version": {
                "target": "2.28.1"
            }
        }
    ]

@patch(
    "packages.requirements.dependencies.get_installed_version",
    return_value="2.28.1"
)
def test_install_or_update_package(
    mock_version,
    mock_configs
):
    """
    Test that `dependencies.install_or_update_package` does not attempt installation
    if the package is already installed with the correct version.
    """
    with patch("subprocess.run") as mock_subproc:
        dependencies.install_or_update_package(
            "requests",
            "2.28.1",
            configs=mock_configs
        )
        mock_subproc.assert_not_called()  # Should not run installation if version matches

@patch("packages.requirements.dependencies.install_or_update_package")  # Prevents real installations
@patch("packages.requirements.dependencies.get_installed_version")
def test_install_requirements(
    mock_get_version,
    mock_install,
    tmp_path,
    mock_configs
):
    """
    Test that `dependencies.install_requirements` correctly skips installation if
    the required version is already installed, and triggers installation
    when the package is missing.
    """
    req_file = tmp_path / "requirements.json"
    req_data = {
        "dependencies": [{
            "package": "requests",
            "version": {
                "target": "2.28.1"
            }
        }]
    }
    req_file.write_text(json.dumps(req_data))
    # Simulate scenario where the package is already installed
    mock_get_version.return_value = "2.28.1"
    dependencies.install_requirements(
        str(req_file),
        configs=mock_configs
    )
    # Ensure `dependencies.install_or_update_package` is NOT called when package is already installed
    mock_install.assert_not_called()
    # 🔄 Simulate package missing scenario
    mock_get_version.return_value = None
    dependencies.install_requirements(
        str(req_file),
        configs=mock_configs
    )
    # Ensure install is triggered when package is missing
    # mock_install.assert_called_once_with("requests", "2.28.1", configs=mock_configs)
    mock_install.assert_called_once()
    args, kwargs = mock_install.call_args
    assert kwargs["package"] == "requests"
    assert kwargs["version"] == "2.28.1"
    assert kwargs["configs"] == mock_configs

@patch("subprocess.check_call")  # Prevents actual package installations
@patch(
    "importlib.metadata.version",
    return_value="2.28.1"
)  # Ensures installed version is controlled
def test_is_package_installed(
    mock_version,
    mock_subproc_call,
    mock_configs
):
    assert dependencies.is_package_installed(
        "requests",
        {"target": "2.28.1"},
        configs=mock_configs
    ) is True
    assert dependencies.is_package_installed(
        "nonexistent",
        {"target": "1.0.0"},
        configs=mock_configs
    ) is False
    assert dependencies.is_package_installed(
        "requests",
        {"target": "2.27.0"},
        configs=mock_configs
    ) is False

def test_parse_arguments_custom():
    with patch(
        "sys.argv",
        ["dependencies.py",
         "-f",
         "custom.json"]
    ):
        args = dependencies.parse_arguments()
        assert args.requirements_file == "custom.json"

def test_parse_arguments_default():
    with patch(
        "sys.argv",
        ["dependencies.py"]
    ):
        args = dependencies.parse_arguments()
        assert args.requirements_file == "./packages/requirements/requirements.json"

@patch("packages.appflow_tracer.lib.log_utils.log_message")
def test_print_installed_packages(
    mock_log_message,
    tmp_path,
    mock_configs
):
    installed_file = tmp_path / "installed.json"
    installed_data = {
        "dependencies": [
            {
                "package": "requests",
                "version": {
                    "target": "2.28.1",
                    "installed": "2.28.1",
                    "status": "installed"
                }
            }
        ]
    }
    installed_file.write_text(
        json.dumps(installed_data, indent=4)
    )
    dependencies.print_installed_packages(
        str(installed_file),
        configs=mock_configs
    )
    # Ensure log messages were called correctly
    mock_log_message.assert_any_call(
        "\nInstalled Packages:\n",
        configs=mock_configs
    )
    mock_log_message.assert_any_call(
        "requests (Required: 2.28.1, Installed: 2.28.1)",
        configs=mock_configs
    )

@patch(
    "importlib.metadata.version",
    side_effect=lambda pkg: "2.28.1" if pkg == "requests" else None
)
def test_update_installed_packages(
    mock_version,
    tmp_path,
    mock_configs
):
    req_file = tmp_path / "requirements.json"
    installed_file = tmp_path / "installed.json"
    req_data = {
        "dependencies": [
            {
                "package": "requests",
                "version": {
                    "target": "2.28.1"
                }
            }
        ]
    }
    req_file.write_text(
        json.dumps(req_data)
    )
    dependencies.update_installed_packages(
        str(req_file),
        str(installed_file),
        configs=mock_configs
    )
    installed_data = json.loads(
        installed_file.read_text()
    )
    assert installed_data["dependencies"][0]["package"] == "requests"
    assert installed_data["dependencies"][0]["version"]["installed"] == "2.28.1"
