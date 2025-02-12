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

from packages.appflow_tracing.enable_tracing import (
    log_message,
    setup_logging,
    start_tracing
)

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# # Debugging: Print sys.path to verify import paths
# print("\n[DEBUG] sys.path contains:")
# for path in sys.path:
#     print(f"  - {path}")

# Import system_variables from lib.system_variables
from lib.system_variables import (
    project_root,
    project_logs,
    max_logfiles
)

from lib.pkgconfig_loader import (
    load_configs,
    get_logfile
)

def load_requirements(requirements_file):
    """Load dependencies from a JSON requirements file."""
    requirements_path = Path(requirements_file).resolve()
    if not requirements_path.exists():
        log_message(f"ERROR: Requirements file not found at {requirements_path}", "error", configs=CONFIGS)
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
        log_message(f"ERROR: Invalid JSON structure in '{requirements_path}'. Details: {e}", "error", configs=CONFIGS)
        raise ValueError(f"ERROR: Invalid JSON structure in '{requirements_path}'.\nDetails: {e}")

def install_package(package, version_info):
    """Install a specific package version using pip."""
    version = version_info["target"]
    log_message(f"Installing {package}=={version}...", configs=CONFIGS)
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
        log_message(f"✅ Successfully installed {package}=={version}", configs=CONFIGS)
    except subprocess.CalledProcessError as e:
        log_message(f"❌ ERROR: Failed to install {package}=={version}. Pip error: {e}", "error", configs=CONFIGS)
        sys.exit(1)

def install_requirements(requirements_file):
    """Install missing dependencies from a JSON requirements file."""
    dependencies = load_requirements(requirements_file)

    if not dependencies:
        log_message("⚠ No dependencies found in requirements.json", "warning", configs=CONFIGS)
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
        log_message(f"⚠️ Skipping {package}: Missing 'target' version.", "warning", configs=CONFIGS)
        return False
    try:
        installed_version = importlib.metadata.version(package)
        if installed_version == version:
            log_message(f"✅ {package}=={version} is already installed.", configs=CONFIGS)
            return True
        else:
            log_message(f"⚠️ {package} installed, but version {installed_version} != {version} (expected).", "warning", configs=CONFIGS)
            return False
    except importlib.metadata.PackageNotFoundError:
        log_message(f"❌ {package} is NOT installed.", "error", configs=CONFIGS)
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

def update_installed_packages(requirements_file):
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
    with open(INSTALLED_JSON_PATH, "w") as f:
        json.dump({"dependencies": installed_data}, f, indent=4)
    log_message(f"📄 Installed package status updated in {INSTALLED_JSON_PATH}", configs=CONFIGS)

# Module's configurations
package_name = Path(__file__).resolve().parent.name
module_name = Path(__file__).stem
CONFIGS, LOG_FILE = load_configs({
    "logging": {
        "module_name": module_name,
        "package_name": package_name,
        "package_logs": str( project_logs / package_name ),
        "log_filename": module_name
    }
})
# print( f'LOG_FILE: {LOG_FILE}' )
# print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

# ✅ Ensure logging is set up globally before anything else
# ✅ Assign the logger explicitly
logger = setup_logging(configs=CONFIGS, logfile=LOG_FILE)

# Start tracing
if CONFIGS["logging"]["enable_tracing"]:
    # print("🔍 Tracing system initialized.")
    start_tracing(configs=CONFIGS)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger.info("🔍 Logging system initialized.")

packages = project_root / "packages" / package_name
INSTALLED_JSON_PATH = packages / "installed.json"

def main():
    """Main function to parse arguments and run the installer."""
    args = parse_arguments()
    log_message("🔍 Starting dependency installation process...", configs=CONFIGS)
    install_requirements(args.requirements_file)
    update_installed_packages(args.requirements_file)
    log_message(f"📂 Logs are being saved in: {LOG_FILE}", configs=CONFIGS)

if __name__ == "__main__":
    main()
