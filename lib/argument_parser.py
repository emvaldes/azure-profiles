#!/usr/bin/env python3

"""
File Path: ./lib/argument_parser.py

Description:

Command-Line Argument Parser

This module provides dynamic parsing of command-line arguments based on a JSON configuration file.
It supports structured parameter definitions, automatic type conversion, and flexible flag handling.

Core Features:

- **JSON-Based Argument Loading**: Reads structured argument definitions dynamically.
- **Automatic Type Conversion**: Converts CLI argument values to expected Python types.
- **Structured Validation**: Ensures required and optional arguments are handled correctly.
- **Debugging Support**: Displays parsed arguments in JSON format when `--debug` is used.

Primary Functions:

- `load_argument_config()`: Reads and validates argument definitions from a JSON file.
- `convert_types(kwargs)`: Converts JSON type definitions into Python-compatible types.
- `parse_arguments(context, description)`: Dynamically parses CLI arguments.
- `parse_arguments(args)`: Processes structured CLI arguments from system parameters.

Expected Behavior:

- If the argument configuration file is missing, an error is logged.
- JSON parsing errors are handled gracefully to prevent execution failures.
- Debug mode (`--debug`) prints parsed arguments in JSON format.

Dependencies:

- `argparse`, `json`, `logging`
- `system_variables` (for directory paths and settings)

Usage:

To run argument parsing with debug output:
> python argument_parser.py --debug
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

def load_argument_config() -> dict:
    """
    Load argument definitions from a JSON configuration file and validate them.

    Reads a structured JSON file that defines command-line arguments, ensuring the file exists,
    is correctly formatted, and contains valid content.

    Raises:
        FileNotFoundError: If the JSON configuration file does not exist.
        ValueError: If the JSON file is empty or contains invalid JSON.
        RuntimeError: If an unexpected error occurs while reading the file.

    Returns:
        dict: A dictionary containing the parsed argument definitions.
    """
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

def convert_types(kwargs: dict) -> dict:
    """
    Convert JSON type definitions into actual Python types.

    This function modifies the argument properties dictionary by converting
    type definitions from string format (e.g., "str", "int") into their corresponding
    Python types.

    Args:
        kwargs (dict): Dictionary of argument properties, potentially including a `type` field.

    Returns:
        dict: Updated dictionary with the `type` field converted to a Python type if applicable.
    """
    type_mapping = {"str": str, "int": int, "bool": bool}
    ## Remove "type" if "store_true" action is set
    if "action" in kwargs and kwargs["action"] == "store_true":
        kwargs.pop("type", None)  ## Safely remove "type" if it exists
    elif "type" in kwargs and kwargs["type"] in type_mapping:
        kwargs["type"] = type_mapping[kwargs["type"]]
    return kwargs

def parse_arguments__prototype(
    context: dict = None,
    description: str = "Azure CLI utility"
) -> argparse.Namespace:
    """
    Parse command-line arguments dynamically based on a JSON configuration file.

    This function loads structured argument definitions from a JSON file and dynamically
    adds them to an argparse parser. It supports automatic type conversion and structured validation.

    Args:
        context (dict, optional): A dictionary specifying which arguments should be included. Defaults to None.
        description (str, optional): A description for the command-line utility. Defaults to "Azure CLI utility".

    Returns:
        argparse.Namespace: A namespace containing the parsed arguments as attributes.
    """

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

def parse_arguments(args: dict) -> argparse.Namespace:
    """
    Process structured CLI arguments using argparse.

    This function manually processes each argument defined in a structured dictionary,
    ensuring correct type conversions and handling unknown arguments gracefully.

    Args:
        args (dict): A dictionary containing structured argument definitions.

    Returns:
        argparse.Namespace: A namespace containing the parsed arguments as attributes.
    """

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
    """
    Main function for executing argument parsing when the script is run as a standalone module.

    This function loads the argument configuration, parses command-line arguments, and
    prints the parsed values in a structured JSON format.
    """
    args = parse_arguments()
    print("\nArgument parsing completed successfully.")
    print(json.dumps(vars(args), indent=4))

if __name__ == "__main__":
    main()
