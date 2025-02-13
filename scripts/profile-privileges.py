#!/usr/bin/env python3

"""
File Path: scripts/profile-privileges.py


Description:

User Privileges and Environment Setup

This script validates user privileges and system configurations, ensuring all required
environment variables are properly set. It dynamically manages runtime parameters
and interacts with dependency and tracing modules.

Features:

- Ensures required dependencies are installed before execution.
- Loads and validates system parameters dynamically.
- Prompts users interactively for missing environment variables.
- Removes `__pycache__` directories to prevent stale bytecode issues.
- Logs execution details for debugging.

This script is essential for ensuring a properly configured execution environment.

Dependencies:

- argparse
- logging
- json
- shutil

Usage:

To execute privilege validation and environment setup:
> python scripts/profile-privileges.py ;
"""

import sys
import os

import json
import logging

import shutil
import atexit

from pathlib import Path

# Determine project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Ensure `lib/` and `packages/` are in sys.path
LIB_PATH = str(PROJECT_ROOT / "lib")
PACKAGES_PATH = str(PROJECT_ROOT / "packages")

if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

if PACKAGES_PATH not in sys.path:
    sys.path.insert(0, PACKAGES_PATH)

# Import dependency management package
try:
    from packages.requirements import dependencies
    dependencies.main()  # Ensure dependencies are installed
except ImportError as e:
    print(f"ERROR: Failed to import dependency management: {e}")
    sys.exit(1)

# Import tracing module (no need to pass arguments)
from packages.appflow_tracer import enable_tracing

# Import other necessary modules from `lib/`
from lib import system_params
from lib.system_params import *
from lib.argument_parser import parse_arguments
from lib.system_variables import project_root

# Configure logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.DEBUG)  # Force debug logging

# # Optionally override default tracing settings
# enable_tracing.TRACE = True  # Disable console output if needed
# enable_tracing.LOGS = True    # Ensure logging is enabled

# Function to remove the specific lib/__pycache__ folder
def remove_pycache():
    """Remove the lib/__pycache__ directory."""
    pycache_dir = project_root / "lib" / "__pycache__"
    if pycache_dir.exists():
        shutil.rmtree(pycache_dir)
        print()
        logging.info(f"{pycache_dir} removed.\n")

def request_input(var_name):
    """Prompt user for input interactively, handling empty inputs and interruptions."""
    if not sys.stdin.isatty():
        print(f"ERROR: Required parameter '{var_name}' is missing and cannot be requested in a non-interactive environment.")
        exit(1)
    try:
        while True:
            user_input = input(f"⚠ '{var_name}' is missing. Please enter a value: ").strip()
            if user_input:
                return user_input
            print("\033[F\033[K", end="", flush=True)  ## Move cursor up and clear line
    except KeyboardInterrupt:
        print("\nERROR: Input interrupted by user. Exiting cleanly.")
        exit(1)

def main():
    """
    Main execution function, dynamically updating RUNTIME VARS from CLI arguments.
    """

    # Register cleanup function at exit
    atexit.register(remove_pycache)

    # ## Debugging Info
    # # print(f"Logging Level: {logging.getLogger().getEffectiveLevel()} (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)")
    # # print(f"\nApplication CLI Arguments (Before Processing): {sys.argv}")
    #
    # # print("RunTime Variables type", type(RUNTIME_PARAMS))
    # args = parse_arguments( SYSTEM_PARAMS )
    # # print("ARGS Variables type", type(args))
    #
    # # print( args )
    #
    # RUNTIME_REQUIRED = RUNTIME_PARAMS["required"]["options"]
    # # print( RUNTIME_REQUIRED )
    # RUNTIME_OPTIONAL = RUNTIME_PARAMS["optional"]["options"]
    # # print( RUNTIME_OPTIONAL )
    # RUNTIME_DEFAULTS = RUNTIME_PARAMS["defaults"]["options"]
    # # print( RUNTIME_DEFAULTS )
    #
    # ## Ensure DEBUG mode is a boolean
    # ## Associate CLI debug flag (-d) with DEBUG mode
    # RUNTIME_PARAMS["defaults"]["options"]["debug"] = args.debug if hasattr(args, "debug") else RUNTIME_PARAMS["defaults"]["options"].get("debug", False)
    # RUNTIME_PARAMS["defaults"]["options"]["verbose"] = args.verbose if hasattr(args, "verbose") else RUNTIME_PARAMS["defaults"]["options"].get("verbose", False)
    #
    # sys.exit(1)
    #
    # allowed_RUNTIME_PARAMS = set(RUNTIME_PARAMS.keys()).union(set(args.keys()))

    args = parse_arguments(system_params.SYSTEM_PARAMS)

    RUNTIME_REQUIRED = system_params.RUNTIME_PARAMS["required"]["options"]
    RUNTIME_OPTIONAL = system_params.RUNTIME_PARAMS["optional"]["options"]
    RUNTIME_DEFAULTS = system_params.RUNTIME_PARAMS["defaults"]["options"]

    RUNTIME_DEFAULTS["debug"] = args.debug if hasattr(args, "debug") else RUNTIME_DEFAULTS.get("debug", False)
    RUNTIME_DEFAULTS["verbose"] = args.verbose if hasattr(args, "verbose") else RUNTIME_DEFAULTS.get("verbose", False)

    allowed_RUNTIME_PARAMS = set(system_params.RUNTIME_PARAMS.keys()).union(set(args.keys()))

    for key, value in args.items():
        key_upper = key.upper()
        if key_upper in allowed_RUNTIME_PARAMS and value is not None:

    #         RUNTIME_PARAMS[key_upper] = value
    #         ## logging.debug(f"Environment Variable [ {key_upper} = '{value}' ]")
    # for key, value in RUNTIME_PARAMS.items():
    #     os.environ[key] = str(value)
    #
    # # ## Identify missing required environment variables
    # # missing_vars = [var for var in REQUIRED_RUNTIME_PARAMS if not os.environ.get(var) or os.environ.get(var).strip() == ""]
    # #
    # # if missing_vars:
    # #     logging.info("Some required parameters are missing. Initiating user-interview process.")
    # #     user_inputs = parse_and_collect_user_inputs("configs/system-params.json", REQUIRED_RUNTIME_PARAMS)
    # #     for key, value in user_inputs.items():
    # #         os.environ[key] = str(value)
    # #         RUNTIME_PARAMS[key] = value
    #
    # ## Validate and sanitize required variables from .env
    # for var in REQUIRED_RUNTIME_PARAMS:
    #     ## Load from .env if available
    #     if var in RUNTIME_PARAMS:
    #         raw_value = RUNTIME_PARAMS[var]
    #         if RUNTIME_PARAMS.get("DEBUG"):
    #             logging.debug(f"\nInspecting Environment Variable: '{var}'")

    for var in system_params.REQUIRED_RUNTIME_PARAMS:
        if var in system_params.RUNTIME_PARAMS:
            raw_value = system_params.RUNTIME_PARAMS[var]
            if system_params.RUNTIME_PARAMS.get("DEBUG"):
                logging.debug(f"Inspecting Environment Variable: '{var}'")

                logging.debug(f"- Raw Value: {raw_value}")
                logging.debug(f"- Type: {type(raw_value)}")
                logging.debug(f"- Length (if applicable): {len(raw_value) if isinstance(raw_value, str) else 'N/A'}")
                logging.debug(f"- Stripped Value: '{raw_value.strip()}'" if isinstance(raw_value, str) else "N/A")
                logging.debug(f"- Is None? {'YES' if raw_value is None else 'NO'}")
                logging.debug(f"- Is Empty String? {'YES' if str(raw_value).strip() == '' else 'NO'}")

            ## Convert string "None" to actual NoneType
            if isinstance(raw_value, str) and raw_value.strip().lower() == "none":
                RUNTIME_PARAMS[var] = None

        # if RUNTIME_PARAMS[var] in [None, ""]:
        #     logging.critical(f"CRITICAL ERROR: Required parameter '{var}' is missing or invalid ('None' detected).")
        #     print(f"CRITICAL ERROR: Required parameter '{var}' is missing or invalid ('None' detected).")
        #     logging.debug(f"sys.stdin.isatty() = {sys.stdin.isatty()}")

                system_params.RUNTIME_PARAMS[var] = None
        if system_params.RUNTIME_PARAMS[var] in [None, ""]:
            logging.critical(f"CRITICAL ERROR: Required parameter '{var}' is missing or invalid.")

            if sys.stdin.isatty():
                logging.info(f"Interactive Mode Detected. Prompting user for '{var}'...")
                try:

                    # while not RUNTIME_PARAMS[var]:  ## Ensures empty string or None triggers the prompt
                    #     RUNTIME_PARAMS[var] = request_input(var)
                    #     # RUNTIME_PARAMS[var] = parse_and_collect_user_inputs("configs/system-params.json", REQUIRED_RUNTIME_PARAMS)[var]
                    #     logging.debug(f"User Input for '{var}': {RUNTIME_PARAMS[var]}")

                    while not system_params.RUNTIME_PARAMS[var]:
                        system_params.RUNTIME_PARAMS[var] = request_input(var)
                        logging.debug(f"User Input for '{var}': {system_params.RUNTIME_PARAMS[var]}")

                except KeyboardInterrupt:
                    logging.error("\nERROR: User interrupted input. Exiting.")
                    exit(1)
            else:
                logging.critical(f"ERROR: Required parameter '{var}' is missing and cannot be requested in a non-interactive environment.")
                exit(1)
    ## logging.debug(f"DEBUG Final Value Before Check: {RUNTIME_PARAMS.get('DEBUG')}")
    ## if RUNTIME_PARAMS.get("DEBUG"):

    print("\nEnd-User's Input parameters (override):")

    # print(json.dumps(RUNTIME_PARAMS, indent=4))
    # manage_accesstoken

    print(json.dumps(system_params.RUNTIME_PARAMS, indent=4))

if __name__ == "__main__":
    main()
