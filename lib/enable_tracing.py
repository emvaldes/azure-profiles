#!/usr/bin/env python3

import sys
import inspect
import json

import tokenize
from io import StringIO

from pathlib import Path
import datetime

from system_variables import (
    project_root,
    max_logfiles
)

# Define the base directory of your project (automatically detected)
BASE_DIR = Path(__file__).resolve().parent

# LOGS_DIR = BASE_DIR / ".logs"
LOGS_DIR = project_root / ".logs"

# Ensure the logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Default settings
TRACE = True  # Enable tracing output to console
LOGS = True  # Enable logging to file

# LOG_FILE = LOGS_DIR / f"{Path(sys.argv[0]).stem}.log"
# LOG_FILE = LOGS_DIR / f"{Path(sys.argv[0]).stem}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log"
log_filename = Path(sys.argv[0]).stem
log_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
LOG_FILE = LOGS_DIR / f"{log_filename}_{log_timestamp}.log"

# ANSI color codes for console output
COLORS = {
    "IMPORT": "\033[94m",  # Blue
    "CALL": "\033[92m",    # Green
    "RETURN": "\033[93m",  # Yellow
    "RESET": "\033[0m"      # Reset to default
}

def is_project_file(filename):
    """Check if a filename is inside the project directory and not in site-packages or standard lib."""
    if filename is None:
        return False
    filename_path = Path(filename).resolve()
    return BASE_DIR in filename_path.parents  # Only include files in the project directory

def relative_path(filepath):
    """Convert absolute paths to relative paths based on the project root."""
    try:
        return str(Path(filepath).resolve().relative_to(BASE_DIR)).replace(".py", "")
    except ValueError:
        return filepath.replace(".py", "")  # Return original if not within project

def safe_serialize(obj):
    """Ensure all objects are JSON serializable, converting non-serializable objects to strings."""
    try:
        return json.loads(json.dumps(obj, default=str))  # Ensure valid JSON without double encoding
    except (TypeError, OverflowError):
        return str(obj)  # Convert non-serializable objects to strings

def log_message(message, category="", json_data=None):
    """Log to a file if LOGS is enabled, print to console if TRACE is enabled with color formatting."""
    if LOGS:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(message + "\n")
            if json_data:
                log_file.write(json.dumps(json_data, indent=2) + "\n")
    if TRACE:
        color = COLORS.get(category, COLORS["RESET"])
        print(f"{color}{message}{COLORS['RESET']}")
        if json_data:
            print(json.dumps(json_data, indent=2))

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

def trace_all(frame, event, arg):
    """Trace imports, function calls, function parameters, and return values within the project only."""
    ## print(f"Tracing activated in {__name__}")
    if not LOGS and not TRACE:
        return None  # Disable tracing if both logging and console output are disabled
    filename = frame.f_globals.get("__file__", "")
    if not is_project_file(filename):
        return None  # Stop tracing for this module
    if event == "call":
        caller_frame = frame.f_back  # Get caller frame
        if caller_frame:
            try:
                caller_info = inspect.getframeinfo(caller_frame)
                if caller_frame.f_code.co_name == "<module>":
                    caller_filename = relative_path(caller_info.filename)  # Convert absolute path to relative
                    caller_lineno = caller_info.lineno
                    # Extract the actual line invoking the function
                    invoking_line = caller_info.code_context[0] if caller_info.code_context else "Unknown"
                    invoking_line = sanitize_token_string(invoking_line)
                    # Fix: Ensure we only show the module name, not the full path
                    caller_module = caller_filename if "/" not in caller_filename else caller_filename.split("/")[-1]
                    log_message(f"\n[CALL] {caller_module}[{caller_lineno}] ( {invoking_line} ) "
                                f"-> {relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]", "CALL")
                else:
                    caller_filename = relative_path(caller_info.filename)
                    caller_co_name = caller_frame.f_code.co_name
                    callee_info = inspect.getframeinfo(frame)
                    arg_values = inspect.getargvalues(frame)
                    arg_list = {arg: arg_values.locals[arg] for arg in arg_values.args}
                    if is_project_file(caller_info.filename):
                        log_message(f"\n[CALL] {caller_filename} ({caller_co_name})[{caller_info.lineno}] "
                                    f"-> {relative_path(callee_info.filename)} ({frame.f_code.co_name})[{callee_info.lineno}]",
                                    "CALL", json_data=arg_list)
            except Exception:
                pass  # Ignore frames that cannot be inspected
    elif event == "return":
        try:
            caller_frame = frame.f_back
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
                        "RETURN", json_data=return_value)
            # # Log the return with more scope
            # log_message(f"\n[RETURN] {return_filename}[{return_lineno}] ( {return_line} ) -> RETURN VALUE:",
            #             "RETURN", json_data=safe_serialize(arg))
        except Exception:
            pass  # Ignore frames that cannot be inspected
    return trace_all  # Keep tracing

# Enable tracing for only the project's modules if either LOGS or TRACE is enabled
if LOGS or TRACE and is_project_file(__file__):
    sys.settrace(trace_all)

# Remove the oldest log file if more than 10 logs exist
# print(max_logfiles)
existing_logs = sorted(LOGS_DIR.glob("*.log"), key=lambda f: f.stat().st_mtime)
print("Number of log files found:", len(existing_logs))
num_to_remove = len(existing_logs) - ( max_logfiles - 1 )
if num_to_remove > 0:
    logs_to_remove = existing_logs[:num_to_remove]
    for log_file in logs_to_remove:
        try:
            log_file.unlink()
        except Exception as e:
            print(f"Error deleting {log_file}: {e}")
