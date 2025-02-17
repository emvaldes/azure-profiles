#!/usr/bin/env python3

"""
File Path: ./lib/accesstoken_expiration.py

Description:

Azure Access Token Expiration Manager
This module handles retrieving and managing Azure access tokens.
It utilizes the `azure.identity` package to fetch tokens and determines expiration details.

Features:

- Fetches an Azure access token using `InteractiveBrowserCredential`
- Extracts and prints token expiration details
- Calculates remaining time before token expiration
- Provides a command-line interface for debugging token validity

This script is primarily used within the framework for handling authentication and ensuring
Azure API requests have valid credentials.

Dependencies:

- azure-identity
- azure-core

Usage:

Run this script to retrieve the token and check its expiration details:
> python accesstoken_expiration.py --debug ;
"""

import sys

from datetime import datetime
from azure.identity import InteractiveBrowserCredential
from azure.core.exceptions import AzureError

# Global variables
TokenScope = "https://management.azure.com/"
AccessToken = None
TokenExpiration = None

def get_access_token():
    """Fetches the Azure access token using Python SDK."""
    global AccessToken
    try:
        credential = InteractiveBrowserCredential()
        token = credential.get_token( "https://management.azure.com/.default" )
        AccessToken = token.token  # Storing the access token globally
        return datetime.datetime.utcfromtimestamp( token.expires_on )  # Expiration time
    except AzureError as e:
        print(
            f"Azure SDK error while fetching token: {e}",
            file=sys.stderr
        )
        return None
    except Exception as e:
        print(
            f"Error fetching access token: {e}",
            file=sys.stderr
        )
        return None

def print_token_expiration( debug=False ):
    """Prints the expiration time and handles errors gracefully."""
    global TokenExpiration
    try:
        # Fetch the token and its expiration
        token_expiration = get_access_token()
        if not token_expiration:
            print(
                "Failed to retrieve or parse the access token.",
                file=sys.stderr
            )
            return
        # Set the expiration globally
        TokenExpiration = token_expiration
        # Debugging output if enabled
        if debug:
            print(
                f"Access Token (JSON) -> {{'accessToken': '{AccessToken}', 'expiresOn': '{TokenExpiration}'}}",
                file=sys.stdout
            )
        # Handle the expiration
        if not TokenExpiration:
            print(
                "Token expiration not found.",
                file=sys.stderr
            )
            return
        # Convert to time string
        expiration_string = TokenExpiration.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if not expiration_string:
            print(
                "Token expiration string is empty.",
                file=sys.stderr
            )
            return
        print(
            f"Token expiration date: {expiration_string}",
            file=sys.stdout
        )
        return TokenExpiration
    except Exception as e:
        print(
            f"Error processing token expiration: {e}",
            file=sys.stderr
        )

def print_remaining_time():
    """Print the remaining time until token expiration."""
    try:
        if TokenExpiration:
            current_time = datetime.datetime.now()
            time_remaining = TokenExpiration - current_time
            hours_remaining = time_remaining.total_seconds() // 3600
            minutes_remaining = (time_remaining.total_seconds() % 3600) // 60
            seconds_remaining = time_remaining.total_seconds() % 60
            print(
                f"Available Remaining Time: {int(hours_remaining)} hours, {int(minutes_remaining)} minutes, {int(seconds_remaining)} seconds",
                file=sys.stdout
            )
        else:
            print(
                "Token expiration is not set, unable to calculate remaining time.",
                file=sys.stderr
            )
    except Exception as e:
        print(
            f"Error calculating remaining time: {e}",
            file=sys.stderr
        )

def main(debug=False):
    """Main entry point to process token expiration."""
    try:
        print_token_expiration( debug=debug )
        print_remaining_time()
    except Exception as e:
        print(
            f"Critical error: {e}",
            file=sys.stderr
        )
        sys.exit(1)

if __name__ == "__main__":
    from argument_parser import parse_arguments
    args = parse_arguments(
        context=["debug", "verbose"],
        description="Manage Azure access token expiration."
    )
    main( debug=args.debug )
