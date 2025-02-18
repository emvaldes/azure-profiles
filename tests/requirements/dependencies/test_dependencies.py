#!/usr/bin/env python3

import sys
import json
import subprocess
import importlib.metadata

import pytest
from unittest.mock import patch, mock_open

from pathlib import Path

# Ensure the root project directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]  # Adjust the number based on folder depth
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Add root directory to sys.path

from lib.system_variables import category
from packages.appflow_tracer import tracing

from packages.requirements.dependencies import (
    load_requirements,
    is_package_installed,
    install_package,
    install_requirements,
    update_installed_packages,
    parse_arguments
)

try:
  CONFIGS = tracing.setup_logging(logname_override='logs/tests/test_dependencies.log')
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

def test_load_requirements_valid(tmp_path, mock_configs):
    req_file = tmp_path / "requirements.json"
    req_data = {"dependencies": [{"package": "requests", "version": {"target": "2.28.1"}}]}
    req_file.write_text(json.dumps(req_data))

    result = load_requirements(str(req_file), configs=mock_configs)
    assert result == [{"package": "requests", "version": {"target": "2.28.1"}}]

def test_load_requirements_missing(mock_configs):
    with pytest.raises(FileNotFoundError):
        load_requirements("nonexistent.json", configs=mock_configs)

def test_load_requirements_invalid_json(tmp_path, mock_configs):
    req_file = tmp_path / "requirements.json"
    req_file.write_text("{invalid_json}")
    with pytest.raises(ValueError):
        load_requirements(str(req_file), configs=mock_configs)

@patch("subprocess.check_call")  # Prevents actual package installations
@patch("importlib.metadata.version", return_value="2.28.1")  # Ensures installed version is controlled
def test_is_package_installed(mock_version, mock_subproc_call, mock_configs):
    assert is_package_installed("requests", {"target": "2.28.1"}, configs=mock_configs) is True
    assert is_package_installed("nonexistent", {"target": "1.0.0"}, configs=mock_configs) is False
    assert is_package_installed("requests", {"target": "2.27.0"}, configs=mock_configs) is False

# @patch("subprocess.check_call")
# def test_install_package(mock_subproc_call, mock_configs):
#     with patch("packages.requirements.dependencies.log_utils.log_message") as mock_log:
#         install_package("requests", {"target": "2.28.1"}, configs=mock_configs)
#         mock_log.assert_any_call("Skipping installation: Managed environment (brew-controlled)")
#         mock_subproc_call.assert_not_called()

@patch("packages.requirements.dependencies.install_package")  # Prevents real installations
@patch("packages.requirements.dependencies.is_package_installed", return_value=True)  # Mock package check
def test_install_requirements(mock_check, mock_install, tmp_path, mock_configs):
    req_file = tmp_path / "requirements.json"
    req_data = {"dependencies": [{"package": "requests", "version": {"target": "2.28.1"}}]}
    req_file.write_text(json.dumps(req_data))

    install_requirements(str(req_file), configs=mock_configs)
    mock_install.assert_not_called()

def test_parse_arguments_default():
    with patch("sys.argv", ["dependencies.py"]):
        args = parse_arguments()
        assert args.requirements_file == "./packages/requirements/requirements.json"

def test_parse_arguments_custom():
    with patch("sys.argv", ["dependencies.py", "-f", "custom.json"]):
        args = parse_arguments()
        assert args.requirements_file == "custom.json"

@patch(
    "importlib.metadata.version",
    side_effect=lambda pkg: "2.28.1" if pkg == "requests" else None
)
def test_update_installed_packages(mock_version, tmp_path, mock_configs):
    req_file = tmp_path / "requirements.json"
    installed_file = tmp_path / "installed.json"
    req_data = {"dependencies": [{"package": "requests", "version": {"target": "2.28.1"}}]}
    req_file.write_text(json.dumps(req_data))

    update_installed_packages(str(req_file), str(installed_file), configs=mock_configs)
    installed_data = json.loads(installed_file.read_text())

    assert installed_data["dependencies"][0]["package"] == "requests"
    assert installed_data["dependencies"][0]["version"]["installed"] == "2.28.1"
