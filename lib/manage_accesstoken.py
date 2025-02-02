#!/usr/bin/env python3

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
