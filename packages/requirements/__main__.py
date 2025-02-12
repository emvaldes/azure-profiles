#!/usr/bin/env python3

"""
File Path: packages/requirements/__main__.py

Description:

Requirements Package Entry Point

This file serves as the entry point for executing the `requirements` package in standalone mode.
It initializes and runs the dependency management system.

Features:

- Calls the `main()` function from `dependencies.py` to manage dependencies.
- Allows the package to be executed as a standalone script.

This module enables the execution of the package using:
```python
python -m packages.requirements ;
```
"""

from .dependencies import main
if __name__ == "__main__":
    main()
