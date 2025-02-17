#!/usr/bin/env python3

import pytest
import json
import subprocess
import importlib.metadata

from unittest.mock import patch, mock_open
from pathlib import Path

from packages.requirements.dependencies import (
    load_requirements,
    is_package_installed,
    install_package,
    install_requirements,
    update_installed_packages,
    parse_arguments
)

def test_load_requirements_valid(tmp_path):
    req_file = tmp_path / "requirements.json"
    req_data = {"dependencies": [{"package": "requests", "version": {"target": "2.28.1"}}]}
    req_file.write_text(json.dumps(req_data))

    result = load_requirements(str(req_file))
    assert result == [{"package": "requests", "version": {"target": "2.28.1"}}]

def test_load_requirements_missing():
    with pytest.raises(FileNotFoundError):
        load_requirements("nonexistent.json")

def test_load_requirements_invalid_json(tmp_path):
    req_file = tmp_path / "requirements.json"
    req_file.write_text("{invalid_json}")
    with pytest.raises(ValueError):
        load_requirements(str(req_file))

@patch(
    "importlib.metadata.version",
    side_effect=lambda pkg: "2.28.1" if pkg == "requests" else None
)
def test_is_package_installed(mock_version):
    assert is_package_installed("requests", {"target": "2.28.1"}) is True
    assert is_package_installed("nonexistent", {"target": "1.0.0"}) is False
    assert is_package_installed("requests", {"target": "2.27.0"}) is False

@patch("subprocess.check_call")
def test_install_package(mock_subproc_call):
    with patch("packages.requirements.dependencies.log_utils.log_message") as mock_log:
        install_package("requests", {"target": "2.28.1"})
        mock_log.assert_any_call("Skipping installation: Managed environment (brew-controlled)")
        mock_subproc_call.assert_not_called()

@patch(
    "packages.requirements.dependencies.is_package_installed",
    side_effect=[False, True]
)
@patch("packages.requirements.dependencies.install_package")
def test_install_requirements(mock_install, mock_check, tmp_path):
    req_file = tmp_path / "requirements.json"
    req_data = {"dependencies": [{"package": "requests", "version": {"target": "2.28.1"}}]}
    req_file.write_text(json.dumps(req_data))

    install_requirements(str(req_file))
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
def test_update_installed_packages(mock_version, tmp_path):
    req_file = tmp_path / "requirements.json"
    installed_file = tmp_path / "installed.json"
    req_data = {"dependencies": [{"package": "requests", "version": {"target": "2.28.1"}}]}
    req_file.write_text(json.dumps(req_data))

    update_installed_packages(str(req_file), str(installed_file))
    installed_data = json.loads(installed_file.read_text())

    assert installed_data["dependencies"][0]["package"] == "requests"
    assert installed_data["dependencies"][0]["version"]["installed"] == "2.28.1"
