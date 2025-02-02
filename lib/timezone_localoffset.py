#!/usr/bin/env python3

import sys
import pytz

from datetime import datetime
from argument_parser import parse_arguments

# Global variables for time zone and offset
LocalTimeZone = None
LocalOffset = None

def get_local_offset( debug=False ):
    """Returns local timezone and time zone offset information."""
    global LocalTimeZone, LocalOffset
    try:
        # Get the current local timezone using pytz
        local_tz = pytz.timezone( "America/Creston" )  # Customize this for the user's region if needed
        # Get aware local time and UTC time
        local_time = datetime.now( local_tz )  # local_time is now aware
        utc_time = datetime.now( pytz.utc )    # utc_time is aware as well
        # Calculate offset (difference between UTC and local time)
        local_offset = local_tz.utcoffset( local_time ).total_seconds() / 3600  # in hours
        LocalTimeZone = local_tz
        LocalOffset = local_offset
        # Print output in the requested format
        print(
            f"Local Time Zone:\t{local_tz} ({local_tz.utcoffset(local_time)})"
        )
        print(
            f"Current Local Time:\t{local_time.strftime('%m/%d/%Y %H:%M:%S')}"
        )
        print(
            f"Current UTC Time:\t{utc_time.strftime('%m/%d/%Y %H:%M:%S')}"
        )
        print(
            f"Local Time Offset:\t{int(local_offset)} hours"
        )
        # Debugging output if enabled
        if debug:
            print(
                f"\nLocal Time Zone:\t{local_tz} ({local_tz.tzname(local_time)})",
                file=sys.stdout
            )
            print(
                f"Current Local Time:\t{local_time.strftime('%m/%d/%Y %H:%M:%S')}",
                file=sys.stdout
            )
            print(
                f"Current UTC Time:\t{utc_time.strftime('%m/%d/%Y %H:%M:%S')}",
                file=sys.stdout
            )
            print(
                f"Local Time Offset:\t{local_offset} hours",
                file=sys.stdout
            )
        return local_offset
    except Exception as e:
        print(f"Error retrieving time zone: {e}", file=sys.stderr)

def main( debug=False ):
    """Main entry point to process time zone offset."""
    try:
        get_local_offset( debug )
    except Exception as e:
        print(
            f"Error processing time zone: {e}",
            file=sys.stderr
        )
        sys.exit( 1 )

if __name__ == "__main__":
    # Command-line argument parsing for debug and verbose
    parser = argparse.ArgumentParser(
        description="Retrieve and print local time zone and offset."
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug mode"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose mode"
    )
    args = parser.parse_args()
    # Set global flags based on user input
    debug = args.debug
    verbose = args.verbose
    main( debug=debug )
