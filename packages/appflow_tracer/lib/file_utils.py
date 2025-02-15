#!/usr/bin/env python3

import re

from pathlib import Path

"""
File Utilities (file_utils.py)

is_project_file(): Checks if a file is in the project’s structure.
manage_logfiles(): Cleans up old log files.
relative_path(): Converts absolute paths to project-relative paths.
remove_ansi_escape_codes(): Strips ANSI codes from strings.
"""

# Import system_variables from lib.system_variables
from lib.system_variables import (
    project_root,
    project_logs,
    max_logfiles
)

def is_project_file(filename) -> bool:
    """
    Determines if a given file path belongs to the project directory structure.

    This function checks whether the provided `filename` is located within the
    project's root directory and is not part of any external libraries.

    Args:
        filename (str): The absolute or relative file path to be checked.
    Returns:
        bool: True if the file is within the project directory; False otherwise.

    Example:
        >>> is_project_file("appflow_tracer/tracing.py")
        True
        >>> is_project_file("appflow_tracer/external.py")
        False
    """

    if not filename:
        # print("is_project_file received None or empty filename.")
        return False
    try:
        filename_path = Path(filename).resolve()
        # print("Resolved filename_path:", filename_path)
        return project_root in filename_path.parents
    except (TypeError, ValueError):
        # Handle None or unexpected inputs gracefully
        return False

def manage_logfiles(configs=None) -> None:
    """
    Manages log file storage by removing the oldest logs if the number exceeds a configured limit.

    This function is responsible for ensuring that the log directory does not grow indefinitely.
    It checks the current number of log files and deletes the oldest ones if the total count
    exceeds the allowed limit specified in the global configuration.

    Args:
        None

    Returns:
        None

    Example:
        >>> manage_logfiles(configs=CONFIGS)
        # Deletes old logs if the count exceeds the configured limit.
    """

    logs_basedir = Path(project_logs)
    for log_subdir in logs_basedir.iterdir():
        if log_subdir.is_dir():  # Ensure it's a directory
            log_files = sorted(
                log_subdir.glob("*.log"),
                key=lambda f: f.stat().st_mtime
            )
            num_to_remove = len(log_files) - (configs["logging"].get("max_logfiles", max_logfiles))
            if num_to_remove > 0:
                logs_to_remove = log_files[:num_to_remove]
                for log_file in logs_to_remove:
                    try:
                        log_file.unlink()
                        print(f"🗑️ Deleted old log: {log_file}")
                    except Exception as e:
                        print(f"⚠️ Error deleting {log_file}: {e}")

def relative_path(filepath: str) -> str:
    """
    Converts an absolute file path into a project-relative path.

    This function tries to map the given absolute path into the project’s directory
    structure. If the file is outside the project, it returns the original path
    as a fallback. The returned path has the `.py` extension removed.

    Args:
        filepath (str): The absolute file path to convert.

    Returns:
        str: The relative path within the project, or the original path if it
        cannot be converted.

    Example:
        >>> relative_path("/path/to/project/module.py")
        "module"
    """

    try:
        return str(Path(filepath).resolve().relative_to(project_root)).replace(".py", "")
    except ValueError:
        return filepath.replace(".py", "")  # Return original if not within project

def remove_ansi_escape_codes(text: str) -> str:
    """
    Removes ANSI escape sequences from a string.

    This function is used to clean up log messages or terminal output by
    stripping out escape codes that produce colored or formatted text.
    The resulting string contains plain, unformatted text.

    Args:
        text (str): The input string that may contain ANSI escape codes.

    Returns:
        str: A new string with all ANSI escape codes removed.

    Example:
        >>> remove_ansi_escape_codes("\x1b[31mThis is red text\x1b[0m")
        "This is red text"
    """

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
