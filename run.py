#!/usr/bin/env python3

"""
File Path: ./run.py

Description:

Framework Execution Entry Point

This script serves as the main execution entry point for the framework.
It ensures that system configurations, dependencies, and user privileges
are properly validated before launching the main workflow.

Features:

- Automatically runs the `devops-workflow.py` script to set up the environment.
- Ensures required dependencies and runtime configurations are properly initialized.
- Provides a simple way to start the framework with a single command.

This script simplifies execution by automating the validation and setup process.

Dependencies:

- subprocess

Usage:

To start the framework:
> python run.py ;
"""

---

import subprocess

print("Running devops-workflow script...")
subprocess.run(["python", "scripts/devops-workflow.py"])
