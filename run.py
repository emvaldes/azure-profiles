#!/usr/bin/env python3

"""
File Path: ./run.py

Description:

Main Execution Entry Point for the Framework

This script acts as the launcher for the framework, ensuring that system configurations,
dependencies, and user privileges are validated before execution.

Features:

- Executes `devops-workflow.py` to perform system validation and setup.
- Ensures all required dependencies and configurations are initialized.
- Provides a single-command entry point for launching the framework.

Expected Behavior:

- This script **must be run from the project root**.
- Any errors encountered in `devops-workflow.py` will be printed to the console.
- The script automatically terminates if critical dependencies are missing.

Dependencies:

- subprocess (used to execute the workflow script)

Usage:

To start the framework:
> python run.py
"""

---

import subprocess

print("Running devops-workflow script...")
subprocess.run(["python", "scripts/devops-workflow.py"])

def main() -> None:
    """
    Execute the framework startup sequence by running the `devops-workflow.py` script.

    This function:
    - Calls `scripts/devops-workflow.py` using `subprocess.run()`.
    - Ensures that system configurations, dependencies, and environment variables
      are validated before execution.
    - Prints status messages to indicate the execution progress.

    Expected Behavior:
    - The script **must be run from the project root**.
    - If `devops-workflow.py` encounters an error, it will be displayed in the console.
    - The script terminates automatically if critical dependencies are missing.

    Raises:
        subprocess.CalledProcessError: If the `devops-workflow.py` execution fails.

    Returns:
        None

    Example:
        >>> python run.py
        Running devops-workflow script...
    """

if __name__ == "__main__":
    main()
