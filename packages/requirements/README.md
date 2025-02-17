# requirements.dependencies - README

## Overview
The `requirements.dependencies` module manages package dependencies for the framework. It ensures that all required Python packages are installed and up-to-date, preventing runtime errors due to missing dependencies.

## Features
- **Dependency Loading**: Reads dependencies from `requirements.json`.
- **Installation Checking**: Verifies whether a package is installed with the correct version.
- **Automatic Installation**: Installs missing or outdated dependencies using `pip`.
- **Logging & Tracking**: Logs all dependency management actions.
- **JSON-Based Configuration**: Uses structured JSON files for managing dependencies.

## Module Functions

### `load_requirements(requirements_file: str) -> dict`
Loads dependency information from a JSON file.

**Parameters:**
- `requirements_file (str)`: Path to the JSON file containing dependencies.

**Returns:**
- `dict`: Parsed dependencies.

**Example:**
```python
dependencies = load_requirements("requirements.json")
print(dependencies)
```

---
### `is_package_installed(package: str, version_info: str = None) -> bool`
Checks if a package is installed and optionally verifies its version.

**Parameters:**
- `package (str)`: The package name.
- `version_info (str, optional)`: The required package version.

**Returns:**
- `bool`: `True` if the package is installed, otherwise `False`.

**Example:**
```python
if is_package_installed("requests", "2.28.0"):
    print("Requests package is installed")
```

---
### `install_package(package: str, version_info: str = None) -> bool`
Installs a specified package and version using `pip`.

**Parameters:**
- `package (str)`: The package name.
- `version_info (str, optional)`: The required package version.

**Returns:**
- `bool`: `True` if installation is successful, otherwise `False`.

**Example:**
```python
install_package("requests", "2.28.0")
```

---
### `install_requirements(requirements_file: str) -> None`
Installs all required dependencies from a JSON file.

**Parameters:**
- `requirements_file (str)`: Path to the JSON file containing dependencies.

**Example:**
```python
install_requirements("requirements.json")
```

---
### `update_installed_packages(requirements_file: str) -> None`
Updates `installed.json` with the current state of installed packages.

**Parameters:**
- `requirements_file (str)`: Path to the JSON file containing dependencies.

**Example:**
```python
update_installed_packages("requirements.json")
```

## JSON Configuration Format
### `requirements.json`
Example:
```json
{
    "dependencies": {
        "requests": "2.28.0",
        "pytest": "7.2.0"
    }
}
```

### `installed.json`
Tracks installed packages:
```json
{
    "requests": "2.28.0",
    "pytest": "7.2.0"
}
```

## Logging
All dependency actions are logged in:
```
./logs/requirements/dependencies-<timestamp>.log
```
Example Log Entry:
```
[2025-02-16 12:30:00] [INFO] Installed requests 2.28.0
```

## Usage Examples
### Check Installed Packages
```python
from requirements.dependencies import is_package_installed

if is_package_installed("numpy"):
    print("Numpy is installed")
```

### Install Dependencies
```python
from requirements.dependencies import install_requirements

install_requirements("requirements.json")
```

## Future Enhancements
- Implement dependency version conflict resolution.
- Optimize installation for large-scale package management.
- Provide automatic rollback in case of failed installations.

## Contributors
- **Project Owner**: [Your Name]
- **Maintainer**: [Your Team]

## License
This module is licensed under the [MIT License](../LICENSE).
