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
> safe_serialize({"key": "value"})

To remove comments from a line of code:
> sanitize_token_string("some_code()  # this is a comment")
"""

import json
import tokenize

from io import StringIO

def safe_serialize(
    data: any,
    verbose: bool = False
) -> str:
    """
    Convert Python objects into a JSON-compatible serialized string.

    This function ensures that data is properly serialized into a JSON string format.
    If an object is not serializable, it gracefully converts it into a string.
    Optionally supports pretty-printing for improved readability.

    Args:
        data (any): The Python object to serialize.
        verbose (bool, optional): If True, the JSON output is formatted with indentation.
            Defaults to False.

    Returns:
        str: A JSON-formatted string if serialization is successful, or a string representation
        of the object if serialization fails.

    Example:
        >>> safe_serialize({"key": "value"})
        '{"key": "value"}'

        >>> safe_serialize({"key": "value"}, verbose=True)
        '{
            "key": "value"
        }'

        >>> safe_serialize(object())
        "[Unserializable data]"
    """

    try:
        return data if isinstance(data, str) else json.dumps(data, indent=2 if verbose else None, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(data) if verbose else "[Unserializable data]"

def sanitize_token_string(line: str) -> str:
    """
    Remove trailing comments and excess whitespace from a line of code.

    This function processes a given line of code and removes any inline comments,
    ensuring only the essential code remains. Useful for parsing source code or
    configuration files.

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
