#!/usr/bin/env python3

"""
File Path: packages/appflow_tracer/lib/serialize_utils.py

Description:

Serialization and String Sanitization Utilities

This module provides helper functions for data serialization and
code sanitization, ensuring JSON compatibility and clean parsing.

Core Features:

- **Safe Serialization**: Converts Python objects to JSON-friendly formats.
- **String Sanitization**: Cleans and trims code strings while removing comments.

Primary Functions:

- `safe_serialize(data, verbose)`: Ensures serializable JSON output.
- `sanitize_token_string(line)`: Removes inline comments from a code string.

Expected Behavior:

- `safe_serialize()` should gracefully handle non-serializable objects.
- `sanitize_token_string()` should remove comments and preserve meaningful text.

Dependencies:

- `json`, `tokenize`, `StringIO` (for text processing)

Usage:

To safely serialize a Python object:
> safe_serialize(data={"key": "value"}, configs=CONFIGS)

To remove comments from a line of code:
> sanitize_token_string(data="some_code()  # this is a comment", configs=CONFIGS)
"""

import json
import tokenize

from io import StringIO

import json

# Import category from system_variables
from lib.system_variables import (
    default_indent,
    category
)

from . import (
    log_utils
)

def safe_serialize(
    data: any,
    configs: dict,
    verbose: bool = False
) -> dict:
    """
    Convert Python objects into a JSON-compatible serialized string with metadata.

    This function ensures that data is properly serialized into a JSON string format.
    If an object is not serializable, it attempts to extract its attributes or provide
    meaningful information instead of just a memory address.

    Args:
        data (any): The Python object to serialize.
        verbose (bool, optional): If True, the JSON output is formatted with indentation.

    Returns:
        dict: A structured response containing serialization results.

    Example:
        >>> safe_serialize({"key": "value"}, configs=configs)
        {"success": True, "serialized": '{"key": "value"}', "type": "dict"}

        >>> safe_serialize(object(), configs=configs)
        {"success": False, "serialized": "[Unserializable data]", "type": "object", "error": "TypeError"}
    """

    try:
        json_dumps = json.dumps(
            data,
            indent=default_indent if verbose else None,
            default=str,
            ensure_ascii=False
        )
        # Ensure that complex objects aren't falsely marked as serializable
        if isinstance(data, object) and not isinstance(data, (dict, list, tuple, str, int, float, bool, set, type(None))):
            raise TypeError("Object is not JSON serializable")
        serialized_data = {"success": True, "serialized": json_dumps, "type": type(data).__name__}
        # log_utils.log_message(
        #     f'\nSerialized Data: {serialized_data}',
        #     log_category=category.debug.id,
        #     configs=configs
        # )
        return serialized_data
    except (TypeError, ValueError) as e:
        # Handle objects with attributes (custom classes)
        if hasattr(data, "__dict__"):
            serialized_attrs = {k: str(v) for k, v in vars(data).items()}
            serialized_data = {
                "success": False,
                "serialized": json.dumps(
                    serialized_attrs,
                    indent=default_indent if verbose else None,
                    ensure_ascii=False
                ),
                "type": type(data).__name__,
                "error": str(e)
            }
        # Handle iterators (list, tuple, set)
        elif hasattr(data, "__iter__") and not isinstance(data, (str, bytes, dict)):
            try:
                serialized_data = {
                    "success": False,
                    "serialized": json.dumps(
                        list(data),
                        indent=default_indent if verbose else None,
                        ensure_ascii=False
                    ),
                    "type": "iterator",
                    "error": "Converted from iterator"
                }
            except Exception as iter_error:
                serialized_data = {
                    "success": False,
                    "serialized": "[Unserializable iterator]",
                    "type": "iterator",
                    "error": str(iter_error)
                }
        # Default fallback for completely non-serializable objects
        else:
            serialized_data = {
                "success": False,
                "serialized": "[Unserializable data]",
                "type": type(data).__name__,
                "error": str(e)
            }
        # log_utils.log_message(
        #     f'\nSerialized Data: {serialized_data}',
        #     log_category=category.debug.id,
        #     configs=configs
        # )
        return serialized_data

def sanitize_token_string(line: str) -> str:
    """
    Remove trailing comments and excess whitespace from a line of code.

    Args:
        line (str): A single line of text that may contain comments and extra spaces.

    Returns:
        str: The sanitized version of the input line, with comments and
        unnecessary whitespace removed.

    Example:
        >>> sanitize_token_string("some_code()  # this is a comment")
        "some_code()"

        >>> sanitize_token_string("   another_line   ")
        "another_line"
    """

    # Latest attempt to fix this issue:
    # try:
    #     tokens = tokenize.generate_tokens(StringIO(line).readline)
    #     new_line = []
    #     last_was_name_or_number = False
    #
    #     for token in tokens:
    #         if token.type == tokenize.COMMENT:
    #             break  # Stop at the first comment
    #         if last_was_name_or_number and token.type in (tokenize.NAME, tokenize.NUMBER):
    #             new_line.append(" ")  # Ensure spacing between identifiers/numbers
    #         new_line.append(token.string)
    #         last_was_name_or_number = token.type in (tokenize.NAME, tokenize.NUMBER)
    #
    #     return "".join(new_line).strip()  # Trim spaces/tabs/newlines
    # except Exception:
    #     return line.strip()  # Ensure fallback trims spaces

    # # PyTest compliant code but breaks readability:
    # try:
    #     tokens = tokenize.generate_tokens(StringIO(line).readline)
    #     new_line = []
    #     # last_token_was_name = False  # Track if the last token was an identifier or keyword
    #     for token in tokens:
    #         if token.type == tokenize.COMMENT:
    #             break  # Stop at the first comment
    #         # if last_token_was_name and token.type in (tokenize.NAME, tokenize.NUMBER):
    #         #     new_line.append(" ")  # Add space between concatenated names/numbers
    #         new_line.append(token.string)
    #     return "".join(new_line).strip()  # Trim spaces/tabs/newlines
    # except Exception:
    #     return line.strip()  # Ensure fallback trims spaces

    # Legacy code:
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
