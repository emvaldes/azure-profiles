#!/usr/bin/env python3

"""
File Path: packages/appflow_tracer/enable_tracing.py

Description:

AppFlow Tracing System

This module implements structured and advanced tracing system for monitoring function calls,
imported modules, and return values within the framework. It logs execution details
for debugging and performance analysis.
It logs execution details to `./logs/appflow_tracer/enable_tracing.log` for self-inspection.

Features:

- Traces function calls and captures their arguments.
- Logs return values of functions and their types.
- Supports logging to both console and file with structured JSON output.
- Limits the number of log files to avoid excessive storage usage.

Enhancements:

- Works within `packages/appflow_tracer` properly.
- Self-inspection enabled when executed directly.
- Structured logging ensured.
- Provides a `start_tracing()` function for external usage.

This module provides deep insights into the application's execution, making it an
essential tool for debugging and performance monitoring.

Dependencies:

- import sys
- import inspect
- import datetime
- import logging
- import builtins
- import json
- import re

- lib.system_variables

Usage:

To enable function call tracing and log execution details:
> python enable_tracing.py ;
"""

import sys
import inspect
import datetime
import logging
import builtins
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
    setup_configs
)

# ---------- Module functions:

def is_project_file(filename):
    """Check if a file belongs to the project and isn't from external libraries."""
    if not filename:
        return False
    filename_path = Path(filename).resolve()
    return project_root in filename_path.parents  # Ensure it's within the project directory

def log_message(message, category="INFO", json_data=None, serialize_json=False, configs=None):
    """Logs messages using the correct logger while keeping console output."""
    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    logger = logging.getLogger(f"{configs['logging']['package_name']}.{configs['logging']['module_name']}")  # Use full module logger name

    # Determine the correct logging level
    log_levels = {
        "CALL": logging.INFO,     # Map CALL to INFO for clarity
        "RETURN": logging.DEBUG,  # Map RETURN to DEBUG
        "IMPORT": logging.WARNING,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    log_level = log_levels.get(category.upper(), logging.INFO)

    # If json_data exists, append it to the message
    if json_data:
        if serialize_json:
            # json_data = safe_serialize(json_data, verbose=serialize_json)
            json_data = json.dumps(json_data, separators=(",", ":"), ensure_ascii=False)

    if configs["logging"].get("enable", False) and not configs["tracing"].get("enable", False):
        if message.strip():
            output_logfile(logger, message, json_data or False)  # ✅ Write ONLY to log file if tracing is disabled

    if configs["tracing"].get("enable", False):
        if message.strip():
            output_console(message, category, json_data or False, configs)  # ✅ Write to console

def manage_logfiles():
    """Remove the oldest log files if they exceed the max_logfiles limit, ensuring logs are managed per package."""
    logs_basedir = Path(project_logs)
    for log_subdir in logs_basedir.iterdir():
        if log_subdir.is_dir():  # Ensure it's a directory
            log_files = sorted(
                log_subdir.glob("*.log"),
                key=lambda f: f.stat().st_mtime
            )
            num_to_remove = len(log_files) - (CONFIGS["logging"].get("max_logfiles", 10))
            if num_to_remove > 0:
                logs_to_remove = log_files[:num_to_remove]
                for log_file in logs_to_remove:
                    try:
                        log_file.unlink()
                        print(f"🗑️ Deleted old log: {log_file}")
                    except Exception as e:
                        print(f"⚠️ Error deleting {log_file}: {e}")

def output_logfile(logger, message, json_data=None):
    """Writes log messages to the log file."""
    # logfile_message = remove_ansi_escape_codes(message)
    logfile_message = message
    if json_data:
        logfile_message += f"\n{json_data}"
    message = remove_ansi_escape_codes(message)
    logger.info(logfile_message)  # ✅ Write to log file

def output_console(message, category, json_data=None, configs=None):
    """Writes log messages to the console with colors."""
    color = configs["colors"].get(category.upper(), configs["colors"]["RESET"])
    if not color.startswith("\033"):  # ✅ Ensure it's an ANSI color code
        color = configs["colors"]["RESET"]
    console_message = f"{color}{message}{configs['colors']['RESET']}"
    print(console_message)  # ✅ Print colored message
    if json_data:
        if isinstance(json_data, str):
            # ✅ Print strings as-is (no JSON formatting)
            print(json_data)
        else:
            # ✅ Pretty-print JSON while keeping Unicode characters
            print(json.dumps(json_data, indent=2, ensure_ascii=False))

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
    """Safely serialize data to JSON without escaping new lines."""
    try:
        return data if isinstance(data, str) else json.dumps(data, indent=2 if verbose else None, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(data) if verbose else "[Unserializable data]"

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

def setup_logging(configs=None):
    """Initialize logging globally and ensure all logs go to the correct file."""
    # ✅ Ensure the variable exists globally
    global LOGGING, CONFIGS, logger

    try:
        if not LOGGING:  # ✅ Check if logging has already been initialized
            LOGGING = True  # ✅ Mark logging as initialized
            # print(f'\n----------> Initializing Setup Logging ... \n')
    except NameError:
        return False

    if configs:
        print(f'Inheriting log-configs')
        CONFIGS = configs
    else:
        print(f'Initializing log-configs')
        CONFIGS = setup_configs()
    # print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

    logfile = CONFIGS["logging"].get("log_filename", False)
    logger = logging.getLogger(f"{CONFIGS['logging']['package_name']}.{CONFIGS['logging']['module_name']}")
    logger.propagate = False  # Prevent handler duplication
    logger.setLevel(logging.DEBUG)

    # Ensure the log file directory exists
    Path(logfile).parent.mkdir(parents=True, exist_ok=True)

    # Remove existing handlers before adding new ones (Prevents duplicate logging)
    if logger.hasHandlers():
        logger.handlers.clear()  # ✅ Ensure handlers are properly cleared before adding new ones
    else:
        # Use ANSIFileHandler as logfile handler
        file_handler = ANSIFileHandler(logfile, mode='a')
        logger.addHandler(file_handler)
        # formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # file_handler.setFormatter(formatter)
        # file_handler.setLevel(logging.DEBUG)
        # Console handler (keeps ANSI color but ensures immediate output)
        console_handler = PrintCapture()
        logger.addHandler(console_handler)
        # console_handler.setFormatter(formatter)
        # console_handler.setLevel(logging.DEBUG)

    # Redirect print() statements to logger
    builtins.print = lambda *args, **kwargs: logger.info(" ".join(str(arg) for arg in args))
    # if CONFIGS["logging"].get("enable", False):
    #     builtins.print = lambda *args, **kwargs: sys.__stdout__.write(" ".join(str(arg) for arg in args) + "\n")

    # Ensure all logs are flushed immediately
    sys.stdout.flush()
    sys.stderr.flush()

    # if not LOGGING:  # ✅ Check if logging has already been initialized
    if CONFIGS["tracing"].get("enable", True):
        try:
            start_tracing(CONFIGS)
            print("🔍 \nTracing system initialized.\n")
        except NameError:
            return False

    return CONFIGS

def start_tracing(configs=None):
    """Public function to enable tracing for external modules with a given config."""
    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    # print(f'\n----------> Start Tracing invoked!\n')
    if configs["tracing"].get("enable", True) and sys.gettrace() is None:  # Prevent multiple traces
        sys.settrace(lambda frame, event, arg: trace_all(configs)(frame, event, arg))

def trace_all(configs):
    """Returns a trace_all function that uses the given configs."""

    # Ensure configs is valid before using it
    if not configs or "logging" not in configs:
        print("⚠️ Warning: configs is not properly initialized in trace_all.")
        return None  # Stop tracing if configs is not ready
    # print( f'Configs: {configs}' )

    # if not configs["logging"].get("enable") and not configs["tracing"].get("enable"):
    #     sys.exit(1)  # Stop tracing if both logging & console tracing are disabled

    # Ensure the logger is properly initialized
    global logger

    def trace_events(frame, event, arg):
        """Trace imports, function calls, function parameters, and return values within the project only."""
        # print(f"\nTracing activated in {__name__}\n")

        # Define functions to be ignored
        excluded_functions = {"emit", "log_message"}
        if frame.f_code.co_name in excluded_functions:
            return  # Skip tracing these functions

        # Excluding non-project specific sources
        filename = frame.f_globals.get("__file__", "")
        if not is_project_file(filename):
            # print(f'Excluding: {filename}')
            return None  # Stop tracing for non-project files

        # print( f'\nFrame: {frame}' )
        # print( f'Event: {event}' )
        # print( f'Arg: {arg}' )

        if event == "call":
            try:
                caller_frame = frame.f_back  # Get caller frame
                if caller_frame:

                    category = "CALL"

                    message = ""  # Initialize message early
                    caller_info = inspect.getframeinfo(caller_frame)
                    caller_filename = relative_path(caller_info.filename)  # Convert absolute path to relative
                    invoking_line = caller_info.code_context[0] if caller_info.code_context else "Unknown"
                    invoking_line = sanitize_token_string(invoking_line)
                    # {relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]"

                    message = f"\n[{category}] {caller_filename} ( {invoking_line} )"
                    if message.strip():
                        log_message(message, category, configs=configs)

                    if caller_frame.f_code.co_name == "<module>":
                        caller_lineno = caller_info.lineno
                        caller_module = caller_filename if "/" not in caller_filename else caller_filename.split("/")[-1]
                        message  = f"[{category}] {caller_module}[{caller_lineno}] ( {invoking_line} ) "
                        message += f"-> {relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]"
                        if message.strip():
                            log_message(message, category, configs=configs)

                    else:
                        caller_co_name = caller_frame.f_code.co_name
                        callee_info = inspect.getframeinfo(frame)
                        arg_values = inspect.getargvalues(frame)
                        arg_list = {arg: arg_values.locals[arg] for arg in arg_values.args}
                        message  = f"[{category}] {caller_filename} ({caller_co_name})[{caller_info.lineno}] "
                        message += f"-> {relative_path(callee_info.filename)} ({frame.f_code.co_name})[{callee_info.lineno}]"
                        # ✅ Fix: Ensure JSON serialization before passing data
                        try:
                            arg_list = json.loads(json.dumps({arg: arg_values.locals[arg] for arg in arg_values.args}, default=str))
                        except (TypeError, ValueError):
                            arg_list = "[Unserializable data]"
                        if message.strip():
                            log_message(message, category, json_data=arg_list, configs=configs)

            except Exception as e:
                logger.error(f"Error in trace_all: {e}")

        elif event == "return":

            try:

                category = "RETURN"
                message = ""  # Initialize message early

                return_filename = relative_path(filename)
                return_lineno = frame.f_lineno
                return_type = type(arg).__name__
                return_value = safe_serialize(arg)  # Ensure JSON serializability
                # message  = f"\n[RETURN] {return_filename}[{return_lineno}] "
                # message += f"-> RETURN VALUE (Type: {return_type}): {return_value}"
                # , "RETURN", configs=configs)

                # Get the returning module/function name
                if frame.f_code.co_name == "<module>":
                    return_filename = relative_path(frame.f_globals.get("__file__", ""))
                    return_co_name = return_filename  # Use filename instead of <module>
                else:
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

                message  = f"[{category}] {return_filename}[{return_lineno}] ( {return_line} ) "
                message += f"-> {category} VALUE (Type: {arg_type}):"
                # Log the return with more scope
                # message = f"\n[RETURN] {return_filename}[{return_lineno}] ( {return_line} ) -> RETURN VALUE:",
                #           "RETURN", json_data=safe_serialize(arg), configs=CONFIGS)

                # if return_value not in [None, "null", ""]:
                if message.strip():
                    log_message(message, category, json_data=return_value, configs=configs)

            # except Exception:
            #     pass  # Ignore frames that cannot be inspected
            except Exception as e:
                logger.error(f"Error in trace_all return handling: {e}")

        return trace_events  # Continue tracing

    return trace_events

class PrintCapture(logging.StreamHandler):
    """ Custom logging handler that captures print() and logs it while displaying in the console. """
    def emit(self, record):
        log_entry = self.format(record)
        sys.__stdout__.write(log_entry + "\n")  # Write to actual stdout
        sys.__stdout__.flush()  # Ensure immediate flushing

class ANSIFileHandler(logging.FileHandler):
    """Custom FileHandler that removes ANSI codes and filters out logging system entries."""
    def emit(self, record):
        # ✅ Ensure only Python's internal logging system is ignored
        if "logging/__init__.py" in record.pathname:
            return  # ✅ Skip internal Python logging module logs
        super().emit(record)  # ✅ Proceed with normal logging

# ---------- Module Global variables:

LOGGING = None
CONFIGS = None
logger = None  # Global logger instance

# ---------- Module operations:

def main():
    """Entry point for running tracing as a standalone module with self-inspection."""
    global LOGGING, CONFIGS, logger  # ✅ Ensure CONFIGS is globally accessible

    # Ensure logging is set up globally before anything else
    setup_logging()
    print( f'CONFIGS: {json.dumps(CONFIGS, indent=2)}' )

    # Manage log files before starting new tracing session
    manage_logfiles()

    # # Debug: Read and display log content to verify logging works
    # try:
    #     log_file = CONFIGS["logging"].get("log_filename", False)
    #     print( f'\nReading Log-file: {log_file}' )
    #     with open(log_file, "r") as file:
    #         # print("\n📄 Log file content:")
    #         print(file.read())
    # except Exception as e:
    #     print(f"⚠️ Unable to read log file: {e}")

# Automatically start tracing when executed directly
if __name__ == "__main__":
    main()
