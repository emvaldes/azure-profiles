#!/usr/bin/env python3

"""
File Path: packages/appflow_tracing/enable_tracing.py

Description:

AppFlow Tracing System

This module implements structured and advanced tracing system for monitoring function calls,
imported modules, and return values within the framework. It logs execution details
for debugging and performance analysis.
It logs execution details to `./logs/appflow_tracing/enable_tracing.log` for self-inspection.

Features:

- Traces function calls and captures their arguments.
- Logs return values of functions and their types.
- Supports logging to both console and file with structured JSON output.
- Limits the number of log files to avoid excessive storage usage.

Enhancements:

- Works within `packages/appflow_tracing` properly.
- Self-inspection enabled when executed directly.
- Structured logging ensured.
- Provides a `start_tracing()` function for external usage.

This module provides deep insights into the application's execution, making it an
essential tool for debugging and performance monitoring.

Dependencies:

- sys
- inspect
- json
- pathlib
- datetime
- re

- lib.system_variables

Usage:

To enable function call tracing and log execution details:
> python enable_tracing.py ;
"""

import sys
import inspect
import datetime
import logging
import json
import re

# import tokenize
# from io import StringIO

from pathlib import Path

# Define base directories
LIB_DIR = Path(__file__).resolve().parent.parent.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))  # Dynamically add `lib/` to sys.path only if not present

# Debugging: Print sys.path to verify import paths
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

# ---------- Module functions:

def is_project_file(filename):
    """Check if a file belongs to the project and isn't from external libraries."""
    if not filename:
        return False
    filename_path = Path(filename).resolve()
    return project_root in filename_path.parents  # Ensure it's within the project directory

# def log_message__legacy(message, category="", json_data=None, serialize_json=False):
#     """Logs messages to console and file if enabled, ensuring no ANSI escape sequences in logs."""
#     clean_message = remove_ansi_escape_codes(message)
#     if CONFIGS["logging"]["enable_logging"]:
#         with open(LOG_FILE, "a") as log_file:
#             log_file.write(clean_message + "\n")
#             if json_data:
#                 log_file.write(safe_serialize(json_data, verbose=serialize_json) + "\n")
#
#     if CONFIGS["logging"]["enable_tracing"]:
#         color = CONFIGS["colors"].get(category, CONFIGS["colors"]["RESET"])
#         print(f"{color}{message}{CONFIGS['colors']['RESET']}")
#         if json_data:
#             print(json.dumps(json_data, indent=2))


def log_message(message, category="", json_data=None, serialize_json=False, configs=None):
    """Logs messages using the correct logger while keeping console output."""
    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    logger = logging.getLogger(configs["logging"]["package_name"])  # ✅ Use the correct logger

    # Ensure message is cleaned before logging
    clean_message = remove_ansi_escape_codes(message)

    if configs["logging"]["enable_logging"]:
        if json_data:
            message += f" {safe_serialize(json_data, verbose=serialize_json)}"
        logger.info(clean_message)  # ✅ Uses logging instead of manual file writing

    if configs["logging"]["enable_tracing"]:
        color = configs["colors"].get(category, configs["colors"]["RESET"])
        print(f"{color}{message}{configs['colors']['RESET']}")
        if json_data:
            print(json.dumps(json_data, indent=2))

    # print( f'\nLogging Message ...' )
    # print( f'Message: {message}' )
    # print( f'Category: {category}' )
    # print( f'JSON Data: {json_data}' )
    # print( f'Serialize JSON: {serialize_json}' )

def manage_logfiles():
    """Remove the oldest log files if they exceed the max_logfiles limit, ensuring logs are managed per package."""
    logs_basedir = Path(project_logs)
    for log_subdir in logs_basedir.iterdir():
        if log_subdir.is_dir():  # Ensure it's a directory
            log_files = sorted(
                log_subdir.glob("*.log"),
                key=lambda f: f.stat().st_mtime
            )
            num_to_remove = len(log_files) - (CONFIGS["logging"]["max_logfiles"])
            if num_to_remove > 0:
                logs_to_remove = log_files[:num_to_remove]
                for log_file in logs_to_remove:
                    try:
                        log_file.unlink()
                        print(f"🗑️ Deleted old log: {log_file}")
                    except Exception as e:
                        print(f"⚠️ Error deleting {log_file}: {e}")

def relative_path(filepath):
    """Convert absolute path to a relative path within the project while ensuring safe fallback."""
    try:
        return str(Path(filepath).resolve().relative_to(project_root)).replace(".py", "")
    except ValueError:
        return filepath.replace(".py", "")  # Return original if not within project

def remove_ansi_escape_codes(text):
    """Remove ANSI escape codes from text to keep logs clean."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def safe_serialize(data, verbose=False):
    """Safely serialize data to JSON, choosing compact or pretty format based on verbosity."""
    try:
        return json.dumps(data, indent=2 if verbose else None, default=str)
    except (TypeError, ValueError):
        return str(data) if verbose else "[Unserializable data]"

def sanitize_token_string__prototype(line):
    """Sanitize sensitive tokens from log messages while preparing for inline encryption."""
    return line.replace("SECRET_TOKEN", "[REDACTED]")

def sanitize_token_string(line):
    """Remove trailing comments while preserving formatting and trim spaces."""
    try:
        tokens = tokenize.generate_tokens(StringIO(line).readline)
        new_line = []
        last_token_was_name = False  # Track if the last token was an identifier or keyword
        for token in tokens:
            if token.type == tokenize.COMMENT:
                break  # Stop at the first comment outside of strings
            if last_token_was_name and token.type in (tokenize.NAME, tokenize.NUMBER):
                new_line.append(" ")  # Add space between concatenated names/numbers
            new_line.append(token.string)
            last_token_was_name = token.type in (tokenize.NAME, tokenize.NUMBER)
            new_line = "".join(new_line).strip()  # Trim spaces/tabs/newlines
        return new_line
        # return "".join(new_line).strip()  # Trim spaces/tabs/newlines
    except Exception:
        return line.strip()  # Ensure fallback trims spaces

def setup_logging(configs=None, logfile=None):
    """Initialize logging globally to ensure all logs go to the correct file."""
    global logger  # Ensure logger is available everywhere
    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    logfile = logfile or LOG_FILE  # Default to global LOG_FILE if not provided

    # logger = logging.getLogger(CONFIGS["logging"]["package_name"])
    logger = logging.getLogger(f"{configs['logging']['package_name']}.{configs['logging']['module_name']}")
    logger.setLevel(logging.DEBUG)

    # Ensure the log file directory exists
    Path(logfile).parent.mkdir(parents=True, exist_ok=True)

    # ✅ Remove existing handlers before adding new ones (Prevents duplicate logging)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Configure logging
    logging.basicConfig(
        filename=logfile,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Add a file handler
    file_handler = logging.FileHandler(logfile)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # # ✅ Also log to console
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(formatter)
    # logger.addHandler(console_handler)

    logger.info("🔍 Logging system initialized.")

    return logger  # ✅ Now returns the logger instance

def start_tracing(configs=None):
    """Public function to enable tracing for external modules with a given config."""
    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    sys.settrace(lambda frame, event, arg: trace_all(configs)(frame, event, arg))  # ✅ Pass a function reference

def trace_all(configs):
    # """Returns a trace_all function that uses the given configs."""

    def trace_events(frame, event, arg):
        """Trace imports, function calls, function parameters, and return values within the project only."""
        # print(f"\nTracing activated in {__name__}\n")

        # print( f'\nTracing All ...' )
        # print( f'frame: {frame}' )
        # print( f'event: {event}' )
        # print( f'arg: {arg}' )
        #
        # print( f'Configs: {configs}' )
        #
        # log_message(f"🔍 Tracing Activated: {event} in {frame.f_code.co_name}", "DEBUG", configs=configs)

        if not configs["logging"]["enable_logging"] and not configs["logging"]["enable_tracing"]:
            print( f'Warning: it is broken' )
            sys.exit(1)
            # return None  # Disable tracing if both logging and console output are disabled

        filename = frame.f_globals.get("__file__", "")
        if not is_project_file(filename):
            return None  # Stop tracing for this module

        if event == "call":
            caller_frame = frame.f_back  # Get caller frame
            if caller_frame:
                try:

                    caller_info = inspect.getframeinfo(caller_frame)
                    caller_filename = relative_path(caller_info.filename)
                    caller_lineno = caller_info.lineno
                    callee_info = inspect.getframeinfo(frame)
                    invoking_line = caller_info.code_context[0] if caller_info.code_context else "Unknown"
                    invoking_line = sanitize_token_string(invoking_line)
                    # log_message(f"\n[CALL] {caller_filename}[{caller_lineno}] ( {invoking_line} ) -> {relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]", "CALL", configs=configs)
                    log_message(f"\n[CALL] {caller_filename} ( {invoking_line} )", "CALL", configs=configs)

                    if caller_frame.f_code.co_name == "<module>":
                        caller_filename = relative_path(caller_info.filename)  # Convert absolute path to relative
                        caller_lineno = caller_info.lineno
                        # Extract the actual line invoking the function
                        invoking_line = caller_info.code_context[0] if caller_info.code_context else "Unknown"
                        invoking_line = sanitize_token_string(invoking_line)
                        # Fix: Ensure we only show the module name, not the full path
                        caller_module = caller_filename if "/" not in caller_filename else caller_filename.split("/")[-1]
                        log_message(f"[CALL] {caller_module}[{caller_lineno}] ( {invoking_line} ) "
                                    f"-> {relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]", "CALL", configs=configs)
                    else:
                        caller_filename = relative_path(caller_info.filename)
                        caller_co_name = caller_frame.f_code.co_name
                        callee_info = inspect.getframeinfo(frame)
                        arg_values = inspect.getargvalues(frame)
                        arg_list = {arg: arg_values.locals[arg] for arg in arg_values.args}
                        if is_project_file(caller_info.filename):
                            log_message(f"[CALL] {caller_filename} ({caller_co_name})[{caller_info.lineno}] "
                                        f"-> {relative_path(callee_info.filename)} ({frame.f_code.co_name})[{callee_info.lineno}]",
                                        "CALL", json_data=arg_list, configs=configs)

                except Exception:
                    pass  # Ignore frames that cannot be inspected
        elif event == "return":
            try:

                caller_frame = frame.f_back
                return_filename = relative_path(filename)
                return_lineno = frame.f_lineno
                return_line = "Unknown"
                return_type = type(arg).__name__
                return_value = safe_serialize(arg)
                # log_message(f"\n[RETURN] {return_filename}[{return_lineno}] -> RETURN VALUE (Type: {return_type}): {return_value}", "RETURN", configs=configs)

                # Get the returning module/function name
                if frame.f_code.co_name == "<module>":
                    return_filename = relative_path(frame.f_globals.get("__file__", ""))
                    return_co_name = return_filename  # Use filename instead of <module>
                else:
                    return_filename = relative_path(filename)
                    return_co_name = frame.f_code.co_name

                # Capture the exact line of code causing the return
                return_info = inspect.getframeinfo(frame)
                return_lineno = return_info.lineno
                # Extract the actual return statement (if available)
                return_line = return_info.code_context[0] if return_info.code_context else "Unknown"
                return_line = sanitize_token_string(return_line)  # Clean up comments and spaces

                # Print the type of the return value and inspect its structure
                arg_type = type(arg).__name__
                # If it's an argparse.Namespace or other complex object, print its full structure
                if hasattr(arg, "__dict__"):
                    return_value = vars(arg)  # Convert Namespace or similar object to a dictionary
                else:
                    return_value = safe_serialize(arg)  # Ensure JSON serializability
                log_message(f"\n[RETURN] {return_filename}[{return_lineno}] ( {return_line} ) -> RETURN VALUE (Type: {arg_type}):",
                            "RETURN", json_data=return_value, configs=configs)
                # # Log the return with more scope
                # log_message(f"\n[RETURN] {return_filename}[{return_lineno}] ( {return_line} ) -> RETURN VALUE:",
                #             "RETURN", json_data=safe_serialize(arg), configs=CONFIGS)

            except Exception:
                pass  # Ignore frames that cannot be inspected
        return trace_events  # Keep tracing

    return trace_events

# ---------- Module Global variables:

# ---------- Module operations:

def main():
    """Entry point for running tracing as a standalone module with self-inspection."""
    global CONFIGS, LOG_FILE  # Ensure they are updated within the function

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

    # Manage log files before starting new tracing session
    manage_logfiles()

    # Start tracing
    if CONFIGS["logging"]["enable_tracing"]:
        # print("🔍 Tracing system initialized.")
        start_tracing(configs=CONFIGS)

    # ✅ Ensure logging is set up globally before anything else
    setup_logging(CONFIGS)

    # Log the standalone execution
    # logger.info("🔍 Logging system initialized.")
    log_message("Executing appflow_tracing in standalone mode.", "IMPORT", configs=CONFIGS)

    # ✅ Debug: Read and display log content to verify logging works
    try:
        print( f'\nReading Log-file: {LOG_FILE}' )
        with open(LOG_FILE, "r") as file:
            print("\n📄 Log file content:")
            print(file.read())
    except Exception as e:
        print(f"⚠️ Unable to read log file: {e}")

# Automatically start tracing when executed directly
if __name__ == "__main__":
    main()
