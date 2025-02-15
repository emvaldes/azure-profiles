#!/usr/bin/env python3

import json
import tokenize

from io import StringIO

"""
Serialization Utilities (serialization_utils.py)

safe_serialize(): Converts data into JSON-friendly formats.
sanitize_token_string(): Cleans and normalizes code strings.
"""

def safe_serialize(
    data: any,
    verbose: bool = False
) -> str:
    """
    Serializes data into JSON format, ensuring that it is human-readable and
    handles non-serializable data gracefully.

    This function attempts to serialize the input data to a JSON string. If
    serialization fails, it falls back to converting the data into a string
    representation. It also provides optional pretty-printing for better
    readability.

    Args:
        data (any): The data to be serialized.
        verbose (bool, optional): If True, the JSON will be formatted with
            indentation for readability. Defaults to False.

    Returns:
        str: The serialized JSON string, or a string representation of the
        data if serialization fails.

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
    Removes trailing comments from a code line and trims whitespace.

    This function is useful when parsing source code or configuration files.
    It ensures that only the essential code or text remains, excluding comments
    and extra spaces.

    Args:
        line (str): A line of text that may include comments and extra spaces.

    Returns:
        str: A sanitized version of the input line, with comments and
        whitespace removed.

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
