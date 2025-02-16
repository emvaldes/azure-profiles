#!/usr/bin/env python3

"""
File Path: packages/requirements/dependencies.py

Description:

Dependency Management System

This module manages project dependencies by loading a structured `requirements.json` file,
validating installed packages, and installing any missing dependencies.

It ensures the framework maintains all required dependencies for smooth execution.

Features:

- **Loads Dependencies**: Reads dependencies from `requirements.json`.
- **Version Validation**: Verifies if required packages and versions are installed.
- **Installation Handling**: Installs missing or outdated packages using `pip`.
- **Tracking & Logging**: Updates `installed.json` to track package status.
- **Logging Support**: Logs installation and validation steps for debugging.

Expected Behavior:

- If a package is missing, it is installed automatically.
- If a package version is incorrect, an installation attempt is made.
- Logs all dependency checks and installations for traceability.

Dependencies:

- `sys`, `json`, `subprocess`, `importlib.metadata`, `argparse`, `logging`, `pathlib`
- `packages.appflow_tracer.tracing` (for logging support)
- `lib.pkgconfig_loader`, `lib.system_variables` (for configuration management)

Usage:

To install dependencies from the default `requirements.json`:
> python dependencies.py

To specify a custom requirements file:
> python dependencies.py -f /path/to/custom.json
"""

import sys
import subprocess
import datetime
import logging
import argparse
import json

import importlib.metadata

from pathlib import Path

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f"  - {path}")

# Import modules & variables from lib.*
from lib import (
    pkgconfig_loader as pkgconfig,
    system_variables as environment
)

from packages.appflow_tracer import (
    tracing
)

# Import trace_utils from lib.*_utils
from packages.appflow_tracer.lib import (
    file_utils,
    log_utils,
    trace_utils
)

# Import category from system_variables
from lib.system_variables import (
    category
)

def load_requirements(requirements_file: str) -> list:
    """
    Load dependencies from a JSON requirements file.

    Reads a structured JSON file that defines required dependencies, extracting
    package names and version requirements.

    Args:
        requirements_file (str): The path to the JSON requirements file.

    Raises:
        FileNotFoundError: If the requirements file does not exist.
        ValueError: If the JSON file is invalid or improperly structured.

    Returns:
        list: A list of dictionaries, each containing a package name and version details.

    Example:
        >>> load_requirements("requirements.json")
        [{"package": "requests", "version": {"target": "2.28.1"}}]
    """

    requirements_path = Path(requirements_file).resolve()
    if not requirements_path.exists():
        log_utils.log_message(f"Requirements file not found at {requirements_path}", category.error.id, configs=CONFIGS)
        raise FileNotFoundError(f"ERROR: Requirements file not found at {requirements_path}")

    try:
        with open(requirements_path, "r") as f:
            data = json.load(f)
            dependencies = [
                {"package": pkg["package"], "version": pkg["version"]}
                for pkg in data.get("dependencies", [])
            ]
            return dependencies
    except json.JSONDecodeError as e:
        log_utils.log_message(f"Invalid JSON structure in '{requirements_path}'. Details: {e}", category.error.id, configs=CONFIGS)
        raise ValueError(f"ERROR: Invalid JSON structure in '{requirements_path}'.\nDetails: {e}")

def install_package(
    package: str,
    version_info: dict
) -> None:
    """
    Install a specific package version using pip.

    This function attempts to install the specified package version using pip.
    It ensures that missing or outdated packages are properly updated.

    Args:
        package (str): The name of the package to install.
        version_info (dict): A dictionary containing the target version of the package.

    Raises:
        SystemExit: If the package installation fails.

    Returns:
        None

    Example:
        >>> install_package("requests", {"target": "2.28.1"})
        Installing requests==2.28.1...
    """

    version = version_info["target"]
    log_utils.log_message(f"Installing {package}=={version}...", configs=CONFIGS)
    try:
        # subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}=={version}"])
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--user",
            f"{package}=={version}"
        ])
        log_utils.log_message(f"Successfully installed {package}=={version}", configs=CONFIGS)
    except subprocess.CalledProcessError as e:
        log_utils.log_message(f"Failed to install {package}=={version}. Pip error: {e}", category.error.id, configs=CONFIGS)
        sys.exit(1)

def install_requirements(requirements_file: str) -> None:
    """
    Install missing dependencies from a JSON requirements file.

    This function iterates through the dependencies listed in the requirements file,
    checking if they are installed and installing missing or outdated packages.

    Args:
        requirements_file (str): The path to the JSON requirements file.

    Returns:
        None

    Example:
        >>> install_requirements("requirements.json")
        Installing missing dependencies...
    """

    dependencies = load_requirements(requirements_file)

    if not dependencies:
        log_utils.log_message("⚠ No dependencies found in requirements.json", category.warning.id, configs=CONFIGS)
        return

    for dep in dependencies:
        package = dep["package"]
        version = dep["version"]

        if is_package_installed(package, version):
            continue
        else:
            install_package(package, version)

def is_package_installed(
    package: str,
    version_info: dict
) -> bool:
    """
    Check if a specific package version is installed.

    This function verifies whether the installed version of a package matches
    the required target version.

    Args:
        package (str): The name of the package.
        version_info (dict): A dictionary containing the target version.

    Returns:
        bool: True if the package is installed with the correct version, False otherwise.

    Example:
        >>> is_package_installed("requests", {"target": "2.28.1"})
        True
    """

    version = version_info.get("target", None)
    if not version:
        log_utils.log_message(f"⚠️ Skipping {package}: Missing 'target' version.", category.warning.id, configs=CONFIGS)
        return False
    try:
        installed_version = importlib.metadata.version(package)
        if installed_version == version:
            log_utils.log_message(f"{package}=={version} is already installed.", configs=CONFIGS)
            return True
        else:
            log_utils.log_message(f"⚠️ {package} installed, but version {installed_version} != {version} (expected).", category.warning.id, configs=CONFIGS)
            return False
    except importlib.metadata.PackageNotFoundError:
        log_utils.log_message(f"{package} is NOT installed.", category.error.id, configs=CONFIGS)
        return False

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for specifying the requirements file.

    This function enables the user to specify a custom requirements JSON file
    using the `-f` or `--file` argument.

    Returns:
        argparse.Namespace: The parsed arguments object containing the selected requirements file.

    Example:
        >>> parse_arguments()
        Namespace(requirements_file='requirements.json')
    """

    parser = argparse.ArgumentParser(
        description="Install dependencies from a JSON file. Use -f to specify a custom JSON file."
    )
    parser.add_argument(
        "-f", "--file",
        dest="requirements_file",
        default="./packages/requirements/requirements.json",
        help="Path to the requirements JSON file (default: ./packages/requirements/requirements.json)"
    )
    return parser.parse_args()

def update_installed_packages(
    requirements_file: str,
    config_filepath: str
) -> None:
    """
    Create or update the `installed.json` file with details of the currently installed packages.

    This function compares installed package versions with required versions and
    updates the `installed.json` file to track their status.

    Args:
        requirements_file (str): The path to the JSON requirements file.
        config_filepath (str): The path where `installed.json` will be saved.

    Returns:
        None

    Example:
        >>> update_installed_packages("requirements.json", "installed.json")
        Updating installed packages...
    """

    dependencies = load_requirements(requirements_file)
    installed_data = []

    for dep in dependencies:
        package = dep["package"]
        target_version = dep["version"]["target"]

        try:
            installed_version = importlib.metadata.version(package)
            if installed_version == target_version:
                status = "installed"
            elif installed_version > target_version:
                status = "newer"
            else:
                status = "outdated"
        except importlib.metadata.PackageNotFoundError:
            installed_version = None
            status = False  # Package is not installed

        installed_data.append({
            "package": package,
            "version": {
                "target": target_version,
                "installed": installed_version,
                "status": status
            }
        })

    # Write to installed.json
    print(f'Installed JSON file: {config_filepath}')
    with open(config_filepath, "w") as f:
        json.dump({"dependencies": installed_data}, f, indent=4)
    log_utils.log_message(f"📄 Installed package status updated in {config_filepath}", configs=CONFIGS)

# ---------- Module Global variables:

# ---------- Module operations:

def main() -> None:
    """
    Main function to parse arguments and run the dependency installation process.

    This function:
    - Parses command-line arguments.
    - Loads the required dependencies.
    - Installs missing dependencies.
    - Updates the installed package tracking file.

    Returns:
        None

    Example:
        >>> python dependencies.py
        Installing dependencies...
    """

    # Ensure the variable exists globally
    global CONFIGS

    CONFIGS = tracing.setup_logging()
    # print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

    packages = environment.project_root / "packages" / CONFIGS["logging"].get("package_name")
    config_filepath = packages / "installed.json"

    args = parse_arguments()
    log_utils.log_message("🔍 Starting dependency installation process...", configs=CONFIGS)
    install_requirements(args.requirements_file)
    update_installed_packages(args.requirements_file, config_filepath)
    log_utils.log_message(f"📂 Logs are being saved in: {CONFIGS["logging"].get("log_filename")}", configs=CONFIGS)

if __name__ == "__main__":
    main()
