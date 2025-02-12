#!/usr/bin/env python3

"""
File Path: ./lib/parsing_userinput.py

Description:

User Input Handling and Interactive Prompts

This module is responsible for collecting user input, ensuring required parameters are provided,
and setting environment variables dynamically. It supports both interactive and non-interactive
environments while handling missing values intelligently.

Features:

- Requests user input with optional default values.
- Handles missing required parameters by prompting users interactively.
- Loads and processes argument configuration from a JSON file.
- Dynamically sets environment variables based on user-provided values.

This module plays a crucial role in making the framework adaptable, allowing runtime configurations
to be validated and set at execution time.

Dependencies:
- json
- os
- logging

Usage:

If required parameters are missing, this module will prompt the user interactively:
> python parsing_userinput.py ;
"""

import sys
import json
import os
import logging

# Configure logging for debugging purposes
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def request_input(prompt: str, required: bool = True, default: str = None):
    """
    Persistent user input request with an optional default value.
    """
    if not sys.stdin.isatty():
        logging.error(f"ERROR: Required parameter '{prompt}' is missing and cannot be requested in a non-interactive environment.")
        print(f"ERROR: Required parameter '{prompt}' is missing and cannot be requested in a non-interactive environment.")
        exit(1)
    try:
        while True:
            user_input = input(f"{prompt} [{default}]: " if default else f"{prompt}: ").strip()
            if user_input:
                logging.debug(f"User input received for {prompt}: {user_input}")
                return user_input
            if not required:
                return default
            print("This field is required. Please enter a value.", end="\r")
    except KeyboardInterrupt:
        logging.critical("Input interrupted by user. Exiting cleanly.")
        print("\nERROR: Input interrupted by user. Exiting cleanly.")
        exit(1)

def user_interview(arguments_config, missing_vars):
    """
    Prompt the user for missing required variables and return a dictionary of responses.
    """
    user_inputs = {}
    for var in missing_vars:
        for param, details in arguments_config.items():
            if details.get("target_env") == var:
                prompt_message = details.get("prompt", f"Enter value for {var}")
                default_value = details.get("default", "")
                logging.debug(f"Prompting user for: {var} - Default: {default_value}")
                user_inputs[var] = request_input(prompt_message, required=True, default=default_value)
    return user_inputs

def parse_and_collect_user_inputs(arguments_config_path, required_runtime_vars):
    """
    Handles user input collection by loading the argument configuration,
    identifying missing variables, and prompting the user for required ones.
    """
    if not os.path.exists(arguments_config_path):
        logging.critical(f"ERROR: Arguments configuration file not found at {arguments_config_path}")
        raise FileNotFoundError(f"ERROR: Arguments configuration file not found at {arguments_config_path}")
    logging.debug(f"Loading arguments configuration from: {arguments_config_path}")
    with open(arguments_config_path, "r") as file:
        arguments_config = json.load(file)
    logging.debug(f"Arguments configuration loaded: {json.dumps(arguments_config, indent=4)}")
    missing_vars = [var for var in required_runtime_vars if not os.getenv(var)]
    logging.info(f"Missing required environment variables: {missing_vars}")
    if missing_vars:
        logging.info("Some required parameters are missing. Initiating user-interview process.")
        user_inputs = user_interview(arguments_config, missing_vars)
        for key, value in user_inputs.items():
            os.environ[key] = str(value)
            logging.debug(f"Environment variable set: {key} = {value}")
        return user_inputs
    logging.info("No missing required environment variables. Proceeding without user interaction.")
    return {}
