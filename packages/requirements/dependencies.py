#!/usr/bin/env python3

"""
File Path: packages/requirements/dependencies.py

Description:

Dependency Management System

This module handles the installation and validation of project dependencies
based on a structured JSON requirements file.

Features:

- Loads dependencies from `requirements.json`.
- Verifies if required packages and versions are installed.
- Installs missing or outdated packages using `pip`.
- Updates an `installed.json` file to track package status.
- Logs installation and validation steps for debugging.

This module ensures the framework maintains all required dependencies for smooth execution.

Dependencies:

- sys
- json
- subprocess
- importlib.metadata
- argparse
- logging
- pathlib

Usage:

To install dependencies from the default `requirements.json`:
> python dependencies.py ;

To specify a custom requirements file:
> python dependencies.py -f /path/to/custom.json ;
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

def load_requirements(requirements_file):
    """Load dependencies from a JSON requirements file."""
    requirements_path = Path(requirements_file).resolve()
    if not requirements_path.exists():
        log_utils.log_message(f"ERROR: Requirements file not found at {requirements_path}", "error", configs=CONFIGS)
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
        log_utils.log_message(f"ERROR: Invalid JSON structure in '{requirements_path}'. Details: {e}", "error", configs=CONFIGS)
        raise ValueError(f"ERROR: Invalid JSON structure in '{requirements_path}'.\nDetails: {e}")

def install_package(package, version_info):
    """Install a specific package version using pip."""
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
        log_utils.log_message(f"❌ ERROR: Failed to install {package}=={version}. Pip error: {e}", "error", configs=CONFIGS)
        sys.exit(1)

def install_requirements(requirements_file):
    """Install missing dependencies from a JSON requirements file."""
    dependencies = load_requirements(requirements_file)

    if not dependencies:
        log_utils.log_message("⚠ No dependencies found in requirements.json", "warning", configs=CONFIGS)
        return

    for dep in dependencies:
        package = dep["package"]
        version = dep["version"]

        if is_package_installed(package, version):
            continue
        else:
            install_package(package, version)

def is_package_installed(package, version_info):
    """Check if a specific package version is installed."""
    version = version_info.get("target", None)
    if not version:
        log_utils.log_message(f"⚠️ Skipping {package}: Missing 'target' version.", "warning", configs=CONFIGS)
        return False
    try:
        installed_version = importlib.metadata.version(package)
        if installed_version == version:
            log_utils.log_message(f"{package}=={version} is already installed.", configs=CONFIGS)
            return True
        else:
            log_utils.log_message(f"⚠️ {package} installed, but version {installed_version} != {version} (expected).", "warning", configs=CONFIGS)
            return False
    except importlib.metadata.PackageNotFoundError:
        log_utils.log_message(f"❌ {package} is NOT installed.", "error", configs=CONFIGS)
        return False

def parse_arguments():
    """Parse command-line arguments for specifying the requirements file."""
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

def update_installed_packages(requirements_file, config_filepath):
    """Create or update the installed.json file with the local package setup."""
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

def main():
    """Main function to parse arguments and run the installer."""
    # Ensure the variable exists globally
    global CONFIGS

    CONFIGS = tracing.setup_logging()
    print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

    packages = environment.project_root / "packages" / CONFIGS["logging"].get("package_name")
    config_filepath = packages / "installed.json"

    args = parse_arguments()
    log_utils.log_message("🔍 Starting dependency installation process...", configs=CONFIGS)
    install_requirements(args.requirements_file)
    update_installed_packages(args.requirements_file, config_filepath)
    log_utils.log_message(f"📂 Logs are being saved in: {CONFIGS["logging"].get("log_filename")}", configs=CONFIGS)

if __name__ == "__main__":
    main()
