#!/usr/bin/env python3

"""
File Path: ./lib/manage_accesstoken.py

Description:

Azure Access Token Manager

This module handles Azure authentication and manages access token expiration.
It ensures that tokens remain valid for API requests and integrates with timezone
handling for better session tracking.

Features:

- Retrieves and checks Azure access token expiration.
- Integrates with local timezone offset detection.
- Provides a command-line interface for session and token management.

This module ensures that the framework maintains valid authentication tokens
and properly handles session expiration.

Dependencies:

- accesstoken_expiration
- timezone_localoffset
- argument_parser

Usage:

To manage Azure session and token expiration:
> python manage_accesstoken.py --debug ;
"""

import sys

from timezone_localoffset import get_local_offset
from lib import system_params
from argument_parser import parse_arguments

def manage_accesstoken():
    """Manages Azure authentication and session expiration handling."""
    from accesstoken_expiration import print_token_expiration
    try:
        print_token_expiration( globals.DEBUG_MODE )
        get_local_offset( globals.DEBUG_MODE )
    except Exception as e:
        print(
            f"An error occurred during token or timezone processing: {e}",
            file=sys.stderr
        )
        sys.exit(1)

if __name__ == "__main__":
    args = parse_arguments(
        context=["debug", "verbose"],
        description="Azure session and token expiration management."
    )
    # Update global flags
    globals.DEBUG_MODE = args.debug
    globals.VERBOSE_MODE = args.verbose
    manage_accesstoken()
