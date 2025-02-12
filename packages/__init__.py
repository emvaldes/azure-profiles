#!/usr/bin/env python3

"""
File Path: packages/__init__.py

Description:

Packages Directory Initialization

This file marks the `packages/` directory as a valid Python package.
It ensures that modules within `packages/` can be imported properly.

Important:

- This file **does not** automatically import submodules to prevent unintended executions.
- Individual submodules must be explicitly imported as needed.

Usage:

Modules within `packages/` should be imported manually:
```python
    from packages.appflow_tracing import enable_tracing
    from packages.requirements import dependencies
```
"""
