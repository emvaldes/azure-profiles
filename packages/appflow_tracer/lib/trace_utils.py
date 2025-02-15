#!/usr/bin/env python3

import sys
import json

import inspect
import logging

from typing import Callable
from types import FrameType

from . import (
    log_utils,
    file_utils,
    serialize_utils
)

"""
Tracing Utilities (tracing_utils.py)

start_tracing(): Begins the tracing system.
trace_all(): Provides the main tracing logic.
trace_events(): A helper sub-function that handles individual trace events.
"""

def start_tracing(configs: dict = None) -> None:
    """
    Starts the tracing system to monitor function calls and events.

    This function initializes the tracing mechanism, enabling detailed tracking
    of function calls, returns, and other events within the codebase. If a
    tracing configuration is not provided, it uses the default global
    configuration.

    Args:
        configs (dict, optional): A dictionary containing tracing configurations.
        If None, the global configurations will be used.

    Returns:
        None

    Example:
        >>> start_tracing()
        # Tracing begins using the global configuration.
    """

    configs = configs or CONFIGS  # Default to global CONFIGS if not provided
    if not configs or "logging" not in configs:
        print("⚠️ Warning: configs is not properly initialized in trace_all.")
        # return None  # This leads to the error
        return lambda frame, event, arg: None  # A no-op trace function
    # print(f'Configs: {configs}')

    # print(f'Trace All result: {trace_all(configs)}')
    # print(f'Trace All type: {type(trace_all(configs))}')

    if configs["tracing"].get("enable", True) and sys.gettrace() is None:  # Prevent multiple traces
        trace_func = trace_all(configs)
        if trace_func is None:
            print("Trace function is None, skipping tracing.")
            return
        # sys.settrace(lambda frame, event, arg: trace_all(configs)(frame, event, arg))
        sys.settrace(lambda frame, event, arg: trace_func(frame, event, arg))
    # message = f'Start Tracing invoked!'
    # log_utils.log_message(message, "CALL", configs=configs)

def trace_all(configs: dict) -> Callable:
    """
    Generates a tracing function based on the provided configuration.

    The returned function, when used as a trace function, logs information
    about calls, returns, and events within the codebase. It ensures that
    only files and modules within the project scope are traced.

    Args:
        configs (dict): The configuration dictionary that controls tracing behavior.

    Returns:
        function: A trace function that can be used with `sys.settrace()`.

    Example:
        >>> sys.settrace(trace_all(configs))
        # Starts tracing using the given configuration.
    """

    # Ensure configs is valid before using it
    if not configs or "logging" not in configs:
        print("⚠️ Warning: configs is not properly initialized in trace_all.")
        return None  # Stop tracing if configs is not ready
    # print( f'Configs: {configs}' )

    # Ensure the logger is properly initialized
    global logger

    def trace_events(
        frame: FrameType,
        event: str,
        arg: object
    ) -> None:
        """
        Core function to handle events during tracing.

        This function is triggered on every Python event (e.g., function call, return) when tracing
        is enabled. It inspects the current frame, determines the event type, and logs the appropriate
        details. The goal is to capture function calls, their arguments, return values, and ensure that
        all traced information belongs to files within the project.

        Args:
            frame (inspect.FrameType): The current frame at the point of the event.
            event (str): The type of event (e.g., "call", "return").
            arg (object): The argument associated with the event (e.g., the return value).

        Returns:
            None

        Example:
            >>> trace_events(frame, "call", None)
            # Logs function call details if the file is within the project.
        """

        # print(f"\nTracing activated in {__name__}\n")

        # Define functions to be ignored
        excluded_functions = {"emit", "log_utils.log_message"}
        if frame.f_code.co_name in excluded_functions:
            return  # Skip tracing these functions

        # # Excluding non-project specific sources
        # filename = frame.f_globals.get("__file__", "")
        # if not file_utils.is_project_file(filename):
        #     # print(f'Excluding: {filename}')
        #     return None  # Stop tracing for non-project files

        try:
            # Excluding non-project specific sources
            filename = frame.f_globals.get("__file__", "")
            if not filename:
                # If filename is None or an empty string, skip further processing
                return None
            if not file_utils.is_project_file(filename):
                # print(f'Excluding: {filename}')
                return None  # Stop tracing for non-project files
            # Additional logic can follow here, like calling file_utils.is_project_file(filename)
        except (TypeError, ValueError):
            # Handle None or unexpected inputs gracefully
            return None

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
                    caller_filename = file_utils.relative_path(caller_info.filename)  # Convert absolute path to relative
                    invoking_line = caller_info.code_context[0] if caller_info.code_context else "Unknown"
                    invoking_line = serialize_utils.sanitize_token_string(invoking_line)
                    # {file_utils.relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]"

                    message = f"\n[{category}] {caller_filename} ( {invoking_line} )"
                    if message.strip():
                        log_utils.log_message(message, category, configs=configs)

                    if caller_frame.f_code.co_name == "<module>":
                        caller_lineno = caller_info.lineno
                        caller_module = caller_filename if "/" not in caller_filename else caller_filename.split("/")[-1]
                        message  = f"[{category}] {caller_module}[{caller_lineno}] ( {invoking_line} ) "
                        message += f"-> {file_utils.relative_path(filename)} ({frame.f_code.co_name})[{frame.f_code.co_firstlineno}]"
                        if message.strip():
                            log_utils.log_message(message, category, configs=configs)

                    else:
                        caller_co_name = caller_frame.f_code.co_name
                        callee_info = inspect.getframeinfo(frame)
                        arg_values = inspect.getargvalues(frame)
                        arg_list = {arg: arg_values.locals[arg] for arg in arg_values.args}
                        message  = f"[{category}] {caller_filename} ({caller_co_name})[{caller_info.lineno}] "
                        message += f"-> {file_utils.relative_path(callee_info.filename)} ({frame.f_code.co_name})[{callee_info.lineno}]"
                        # Fix: Ensure JSON serialization before passing data
                        try:
                            arg_list = json.loads(json.dumps({arg: arg_values.locals[arg] for arg in arg_values.args}, default=str))
                        except (TypeError, ValueError):
                            arg_list = "[Unserializable data]"
                        if message.strip():
                            log_utils.log_message(message, category, json_data=arg_list, configs=configs)

            except Exception as e:
                logger.error(f"Error in trace_all: {e}")

        elif event == "return":

            try:

                category = "RETURN"
                message = ""  # Initialize message early

                return_filename = file_utils.relative_path(filename)
                return_lineno = frame.f_lineno
                return_type = type(arg).__name__
                return_value = serialize_utils.safe_serialize(arg)  # Ensure JSON serializability
                # message  = f"\n[RETURN] {return_filename}[{return_lineno}] "
                # message += f"-> RETURN VALUE (Type: {return_type}): {return_value}"
                # , "RETURN", configs=configs)

                # Get the returning module/function name
                if frame.f_code.co_name == "<module>":
                    return_filename = file_utils.relative_path(frame.f_globals.get("__file__", ""))
                    return_co_name = return_filename  # Use filename instead of <module>
                else:
                    return_co_name = frame.f_code.co_name

                # Capture the exact line of code causing the return
                return_info = inspect.getframeinfo(frame)
                return_lineno = return_info.lineno
                # Extract the actual return statement (if available)
                return_line = return_info.code_context[0] if return_info.code_context else "Unknown"
                return_line = serialize_utils.sanitize_token_string(return_line)  # Clean up comments and spaces

                # Print the type of the return value and inspect its structure
                arg_type = type(arg).__name__
                # If it's an argparse.Namespace or other complex object, print its full structure
                if hasattr(arg, "__dict__"):
                    return_value = vars(arg)  # Convert Namespace or similar object to a dictionary

                message  = f"[{category}] {return_filename}[{return_lineno}] ( {return_line} ) "
                message += f"-> {category} VALUE (Type: {arg_type}):"
                # Log the return with more scope
                # message = f"\n[RETURN] {return_filename}[{return_lineno}] ( {return_line} ) -> RETURN VALUE:",
                #           "RETURN", json_data=serialize_utils.safe_serialize(arg), configs=CONFIGS)

                # if return_value not in [None, "null", ""]:
                if message.strip():
                    log_utils.log_message(message, category, json_data=return_value, configs=configs)

            # except Exception:
            #     pass  # Ignore frames that cannot be inspected
            except Exception as e:
                logger.error(f"Error in trace_all return handling: {e}")

        return trace_events  # Continue tracing

    return trace_events
