#!/usr/bin/env python3

"""
File Path: ./lib/argument_parser.py

Description:

Command-Line Argument Parser
This module provides dynamic parsing of command-line arguments based on a JSON configuration file.
It supports structured parameter definitions, automatic type conversion, and flexible flag handling.

Features:

- Loads argument definitions from a JSON configuration file.
- Ensures type conversion (e.g., str, int, bool) for CLI arguments.
- Supports optional and required parameters with structured validation.
- Provides debug mode to display parsed arguments in JSON format.

This module is used to standardize and centralize argument parsing across the framework, ensuring consistency
in handling user-provided parameters.

Dependencies:

- argparse
- json
- logging

Usage:

To run argument parsing with debug output:
> python argument_parser.py --debug ;
"""

import sys
import os

import argparse
import json
import logging

from pathlib import Path
from system_variables import (
    system_params_filepath
)

def load_argument_config():
    """Load argument definitions from a JSON configuration file with better error handling."""
    if not system_params_filepath.exists():
        raise FileNotFoundError(f"ERROR: Argument configuration file not found at {system_params_filepath}")
    ## Handles empty files, permission issues, and invalid JSON.
    try:
        with open(system_params_filepath, "r") as file:
            data = json.load(file)
            if not data:
                raise ValueError(f"ERROR: Empty JSON file '{system_params_filepath}'. Please check the contents.")
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"ERROR: Invalid JSON structure in '{system_params_filepath}'.\nDetails: {e}")
    except Exception as e:
        raise RuntimeError(f"ERROR: Unable to read '{system_params_filepath}'. Details: {e}")

def convert_types(kwargs):
    """Convert string representations from JSON into actual Python types."""
    type_mapping = {"str": str, "int": int, "bool": bool}
    ## Remove "type" if "store_true" action is set
    if "action" in kwargs and kwargs["action"] == "store_true":
        kwargs.pop("type", None)  ## Safely remove "type" if it exists
    elif "type" in kwargs and kwargs["type"] in type_mapping:
        kwargs["type"] = type_mapping[kwargs["type"]]
    return kwargs

def parse_arguments__prototype(context=None, description="Azure CLI utility"):
    """Parse command-line arguments dynamically from JSON configuration."""
    parser = argparse.ArgumentParser(description=description)
    argument_definitions = load_argument_config()
    for section_name, parameters in argument_definitions.items():
        for arg_name, arg_data in parameters.items():
            if context and arg_name not in context:
                continue
            flags = arg_data.get("flags", [])
            kwargs = convert_types(arg_data.get("kwargs", {}))
            ## Override 'required' for manual enforcement in `main()`
            if "required" in kwargs:
                kwargs.pop("required")
            parser.add_argument(*flags, **kwargs)
    args = parser.parse_args()
    ## Improves readability of CLI arguments.
    ## Debug mode: Show parsed arguments
    if getattr(args, "debug", False):
        print("\nParsed CLI Arguments (JSON):")
        ## for key, value in vars(args).items():
        ##     print(f"{key}: {value}")
        print(json.dumps(vars(args), indent=4))
    return args

def parse_arguments( args ):
    parser = argparse.ArgumentParser(description="System Globals Parameter Parser")
    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool
    }

    # print(f"System Parameters (loaded): {json.dumps(args, indent=4)}")

    parsed_args = {}  # Store parsed arguments manually
    for section, section_data in args.items():
        if "options" in section_data:
            for param, details in section_data["options"].items():
                print()
                logging.debug(f'Processing: {section}["{param}"]')
                print(json.dumps(details, indent=4))
                # Ensure type conversion
                kwargs = details.get("kwargs", {}).copy()
                # Remove `required=True` to allow missing values to be handled manually
                kwargs.pop("required", None)
                # If action is store_true or store_false, remove type to avoid conflict
                if "action" in kwargs and kwargs["action"] in ["store_true", "store_false"]:
                    kwargs.pop("type", None)
                # Convert type from string to callable
                if "type" in kwargs and isinstance(kwargs["type"], str):
                    kwargs["type"] = type_mapping.get(kwargs["type"], str)
                # Check if flags exist before calling parser.add_argument
                flags = details.get("flags")
                if not flags:
                    logging.error(f"Missing 'flags' in argument: {param}")
                    continue
                try:
                    parser.add_argument(*flags, **kwargs)
                except Exception as e:
                    logging.error(f"Failed to add argument {param} in section {section} with details {kwargs}: {e}")
                    raise
    args, unknown = parser.parse_known_args()
    args_dict = vars(args)
    # Log any unknown arguments that were ignored
    if unknown:
        logging.warning(f"Unknown CLI arguments ignored: {unknown}")

    return args

def main():
    """Main function for executing argument parsing when the script is run as a module."""
    args = parse_arguments()
    print("\nArgument parsing completed successfully.")
    print(json.dumps(vars(args), indent=4))

if __name__ == "__main__":
    main()
