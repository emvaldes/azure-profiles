# Project Documentation

## Project Structure

```console
./
├── .env
├── .gitignore
├── .outputs/
│   ├── output-console.log
│   └── output-logfile.log
├── .project/
│   ├── chatgpt-requests.log
│   ├── project-instructions.log
│   └── project-objectives.log
├── LICENSE
├── README.md
├── configs/
│   ├── .env.header
│   ├── default-params.json
│   ├── project-params.json
│   └── runtime-params.json
├── lib/
│   ├── __init__.py
│   ├── accesstoken_expiration.py
│   ├── argument_parser.py
│   ├── configure_params.py
│   ├── manage_accesstoken.py
│   ├── parsing_userinput.py
│   ├── pkgconfig_loader.py
│   ├── system_params.py
│   ├── system_variables.py
│   └── timezone_localoffset.py
├── packages/
│   ├── __init__.py
│   ├── appflow_tracer/
│   │   ├── LICENSE
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── lib/
│   │   │   ├── __init__.py
│   │   │   ├── file_utils.py
│   │   │   ├── log_utils.py
│   │   │   ├── serialize_utils.py
│   │   │   └── trace_utils.py
│   │   ├── pyproject.toml
│   │   ├── setup.py
│   │   ├── tracing.json
│   │   ├── tracing.log
│   │   └── tracing.py
│   └── requirements/
│       ├── __init__.py
│       ├── __main__.py
│       ├── dependencies.json
│       ├── dependencies.log
│       ├── dependencies.py
│       ├── installed.json
│       └── requirements.json
├── run.py
└── scripts/
    ├── devops-workflow.log
    ├── devops-workflow.py*
    ├── testing.json
    └── testing.py

10 directories, 50 files
```

## Overview

This project is structured around a logging system, configuration management, and execution scripts, with core functionality implemented in `packages` and `lib`. Below is a breakdown of each file and directory.

## Root Directory

- **`run.py`**: The main entry point for executing the application. Likely orchestrates different modules.
- **`LICENSE`**: Contains licensing information for the project.
- **`README.md`**: Provides an overview of the project, setup instructions, and usage details.
- **`.gitignore`**: Specifies files and directories to be ignored by Git.
- **`.env`**: Stores environment variables for runtime configuration. This file is dynamically generated at runtime and contains user-specific settings that should not be committed to version control.

---

## Configuration Files (`configs/`)

- **`runtime-params.json`**: Stores the merged runtime parameters derived from `default-params.json` and `project-params.json`.
  - This file acts as the JSON equivalent of `.env`, containing structured environment variables.
  - It is created if it does not exist and is wiped if invalid.
  - It merges the `target_env` properties from `default-params.json` and `project-params.json`.
  - It categorizes parameters into:
    - **Required**: Must be specified by the user (`environment`, `project_domain`, `resource_group`).
    - **Optional**: Project-specific configurations (`database_name`, `functionapp_name`, `postgres_server`, `vault_name`).
    - **Defaults**: Standardized framework parameters (`auto`, `debug`, `verbose`, etc.).
  - If no user input is provided, the system prompts the user to input required parameters.
  - User-provided parameters override merged configurations and are stored in `.env` (local file, excluded from Git) while updating `runtime-params.json` **in memory only** (not written to file).

- **`project-params.json`**: Contains project-specific configurations that the end-user is expected to customize.
  - This file is designed for project-specific configurations and is meant to be customized by the user. The parameters listed here serve only as examples for this prototype and are not required by the framework.
  - Defines required and optional parameters specific to the project.
  - Example of what could be considered as required parameters:
    - `--environment`: Specifies the target environment.
    - `--project-domain`: Defines the project domain.
    - `--resource-group`: Identifies the resource group name.
  - Example of optional parameters the application might include:
    - `--database-name`: Defines the PostgreSQL database name.
    - `--function-app-name`: Specifies the Function App name.
    - `--postgres-server`: Names the PostgreSQL server.
    - `--vault-name`: Specifies the secrets vault.
  - These parameters are flexible and should be adapted based on the project's specific requirements.

- **`default-params.json`**: Contains default configurations for script execution parameters.
  - Defines standardized input parameters for the application.
  - Supports command-line flags such as `--auto`, `--debug`, `--examples`, `--help`, and more.
  - Specifies behavior for unattended execution, debugging, logging levels, parameter listings, and tracing.
  - Each parameter includes:
    - Flags: Command-line arguments (e.g., `--debug`, `--json`).
    - Kwargs: Properties like type, requirement status, and action behavior.
    - Target Environment: Context for execution.
    - Prompt Messages: User messages for each action.
    - Default Values: Predefined settings for execution.
  - Example parameters include:
    - `--debug`: Enables debug mode.
    - `--json`: Displays script/project configurations.
    - `--verbose`: Enables verbose output.
    - `--trace`: Enables tracing mode.
    - `--version`: Displays the application version.

---

## Library (`lib/`)

- **`__init__.py`**: Initializes the `lib` package.
This file marks the `lib` directory as a Python package.
It may be used to:
- Initialize package-wide variables.
- Import commonly used modules within `lib`.
- Define shared utilities that may be reused across the package.

---

#### `lib/accesstoken_expiration.py`
**`accesstoken_expiration.py`**: Handles expiration policies for access tokens.

This module manages Azure access tokens by:
- Fetching a token using `InteractiveBrowserCredential`.
- Extracting and storing expiration details.
- Printing token expiration and remaining validity time.

**Key Functions:**
- `get_access_token()`: Retrieves an Azure access token.
- `print_token_expiration(debug=False)`: Prints the token expiration time.
- `print_remaining_time()`: Displays the remaining validity of the token.
- `main(debug=False)`: Handles command-line execution.

**Usage:**
To retrieve the token and check expiration details:

```python
  python lib/accesstoken_expiration.py --debug ;
```

This ensures the system has a valid authentication token for interacting with Azure services.

---

#### `lib/argument_parser.py`
This module handles dynamic parsing of command-line arguments based on a JSON configuration file.
It ensures consistency in how user-provided parameters are interpreted and validated across the framework.

**Key Functions:**
- `load_argument_config()`: Loads argument definitions from a JSON configuration file.
- `convert_types(kwargs)`: Converts JSON string types into actual Python types.
- `parse_arguments__prototype(context, description)`: Dynamically parses CLI arguments based on JSON configurations.
- `parse_arguments(args)`: Parses arguments while handling type conversion, missing values, and validation.
- `main()`: Runs the argument parser when executed as a standalone script.

**Usage:**
To execute argument parsing with debug output:

```python
> python lib/argument_parser.py --debug
```

This module ensures a consistent and structured approach to handling CLI arguments across the framework.

---

#### `lib/configure_params.py`
This module is responsible for managing and validating configuration parameters by merging default
settings with user-defined input.

**Key Responsibilities:**
- Loads and parses JSON configuration files (`default-params.json` and `project-params.json`).
- Ensures all required parameters are provided by the user or set with defaults.
- Validates optional parameters and applies fallback values when necessary.
- Updates in-memory runtime parameters dynamically based on provided inputs.

**Key Functions:**
- `load_parameters()`: Reads and processes JSON configuration files.
- `validate_parameters()`: Ensures all required parameters are present and valid.
- `merge_configurations()`: Merges user-defined and default parameters.
- `apply_runtime_settings()`: Updates runtime parameters dynamically.

**Usage:**
To process and validate configuration parameters:

```python
> python lib/configure_params.py ;
```

This module ensures a structured and dynamic configuration system for the framework.

---

#### `lib/manage_accesstoken.py`
This module ensures proper authentication handling by managing Azure access tokens and their expiration.
It integrates with timezone utilities to synchronize session validity across different time zones.

**Key Responsibilities:**
- Retrieves the Azure access token expiration time.
- Integrates with the `timezone_localoffset` module to adjust session tracking.
- Provides a CLI for debugging session and token expiration.

**Key Functions:**
- `manage_accesstoken()`: Checks access token validity and adjusts session expiration handling.
- `print_token_expiration(debug)`: Displays access token expiration details.
- `get_local_offset(debug)`: Retrieves the local timezone offset.
- `parse_arguments(context, description)`: Parses command-line arguments.

**Usage:**
To manage Azure session authentication and expiration:

```python
> python lib/manage_accesstoken.py --debug ;
```

This ensures a stable and authenticated session for the framework's operations.

---

#### `lib/parsing_userinput.py`
This module handles interactive user input collection and ensures that required parameters are provided
at runtime. It is used to validate and request missing values when necessary.

**Key Responsibilities:**
- Checks for missing required environment variables.
- Requests user input interactively with optional default values.
- Loads argument configuration from a JSON file.
- Dynamically sets environment variables based on user input.

**Key Functions:**
- `request_input(prompt, required, default)`: Prompts the user for input and applies validation.
- `user_interview(arguments_config, missing_vars)`: Iterates through missing variables and requests input.
- `parse_and_collect_user_inputs(arguments_config_path, required_runtime_vars)`: Handles input collection
  and updates environment variables dynamically.

**Usage:**
If required parameters are missing, this module will prompt the user interactively:

```python
> python lib/parsing_userinput.py ;
```

This ensures all necessary parameters are set before execution.

---

#### `lib/system_params.py`
This module is responsible for managing system-wide parameters by merging default and project-specific
configurations, ensuring all necessary runtime parameters are available.

**Key Responsibilities:**
- Loads and validates system parameters from `runtime-params.json`, `project-params.json`, and `default-params.json`.
- Dynamically sets environment variables based on merged configurations.
- Ensures that required parameters are present before the system executes.

**Key Functions:**
- `load_json_config(runtime_params_filepath)`: Loads runtime parameters from a JSON configuration file.
- `get_runtime_variable(name, required)`: Retrieves and validates environment variables.
- `configure_params()`: Merges system and runtime parameters dynamically.

**Usage:**
To load and validate system parameters before execution:

```python
> python lib/system_params.py ;
```

This module ensures that the framework operates with a properly initialized environment.

---

#### `lib/system_variables.py`
This module defines system-wide variables and paths for configuration management.
It centralizes all critical file paths for streamlined access throughout the framework.

**Key Responsibilities:**
- Establishes the project root directory for consistent path resolution.
- Defines paths for runtime, system, project, and default configurations.
- Aggregates configuration sources to facilitate parameter merging.
- Limits the number of log files to maintain efficient storage.

**Defined Variables:**
- `project_root`: Root directory of the project.
- `env_filepath`: Path to the `.env` file for environment variables.
- `runtime_params_filepath`: Path to `runtime-params.json` (runtime configurations).
- `system_params_filepath`: Path to `system-params.json` (global configurations).
- `project_params_filepath`: Path to `project-params.json` (project-specific configurations).
- `default_params_filepath`: Path to `default-params.json` (framework default configurations).
- `system_params_listing`: List of configuration files used for aggregation.
- `max_logfiles`: Restricts the number of log files in `./logs/`.

**Usage:**
This module is imported wherever global paths and configuration file locations are required.

---

#### `lib/timezone_localoffset.py`
This module retrieves and calculates the local time zone and offset from UTC.
It ensures proper time synchronization for logging, scheduling, and authentication processes.

**Key Responsibilities:**
- Determines the local time zone using the `pytz` library.
- Calculates the offset between local time and UTC.
- Provides a command-line interface for debugging time zone information.

**Key Functions:**
- `get_local_offset(debug)`: Retrieves and displays the local time zone and UTC offset.
- `main(debug)`: Handles command-line execution and processes time zone retrieval.

**Usage:**
To retrieve and display the local time zone and offset:

```python
> python lib/timezone_localoffset.py --debug ;
```

This module ensures that the framework operates with accurate time zone awareness.

---

## Packages (`packages/`)

#### `packages/__init__.py`
This file initializes the `packages/` directory as a valid Python package.

**Key Responsibilities:**
- Marks `packages/` as a Python package.
- Ensures submodules within `packages/` can be explicitly imported.
- Prevents automatic submodule execution to avoid unintended behaviors.

**Usage:**
Submodules within `packages/` should be imported explicitly:

```python
from packages.appflow_tracer import tracing
from packages.requirements import dependencies
```

This structure ensures controlled imports while maintaining modularity.

---

### Package: appflow_tracer

#### `packages/appflow_tracer/__init__.py`
This file initializes the `appflow_tracer` package and provides access to its main tracing functionality.

**Key Responsibilities:**
- Marks the `appflow_tracer` directory as a Python package.
- Imports and exposes the `main()` function from `tracing.py`.

**Usage:**
To run the tracing function from within another module:

```python
  from packages.appflow_tracer import main
  main()
```

This allows seamless execution of the tracing functionality from the package level.

---

#### `packages/appflow_tracer/__main__.py`
This file allows the `appflow_tracer` package to be executed as a standalone module.
It initializes the tracing system and displays tracing/logging status.

**Key Responsibilities:**
- Initializes full self-tracing with logging enabled.
- Prints tracing and logging system status.
- Provides an entry point for running the package directly.

**Key Functions:**
- `main()`: Initializes the tracing system and displays relevant status messages.

**Usage:**
To execute the tracing system in standalone mode:

```python
> python -m packages.appflow_tracer ;
```

This ensures tracing and logging are active and ready for capturing system events.

---

#### `packages/appflow_tracer/tracing.py`
This module provides a detailed tracing system for monitoring function calls, imports,
and return values within the framework. It is primarily used for debugging and logging
execution details.

**Key Responsibilities:**
- Tracks function calls, parameters, and return values.
- Logs execution details to console and file.
- Limits excessive log file storage by removing old logs.

**Key Functions:**
- `trace_all(frame, event, arg)`: Traces function calls and return values within the project.
- `log_message(message, category, json_data)`: Logs tracing details to file and console.
- `sanitize_token_string(line)`: Cleans and formats tokenized function calls.
- `is_project_file(filename)`: Ensures tracing is only applied to project files.

**Usage:**
To enable tracing and logging for debugging:

```python
> python lib/tracing.py ;
```

This module provides detailed execution tracking for in-depth debugging and performance analysis.

---

### Package: requirements

#### `packages/requirements/__init__.py`
This file initializes the `requirements` package and provides access to its dependency management functionality.

**Key Responsibilities:**
- Marks the `requirements` directory as a Python package.
- Imports and exposes the `main()` function from `dependencies.py`.

**Usage:**
To run the dependency management function from within another module:

```python
  from packages.requirements import main
  main()
```

This allows seamless execution of the dependency management functionality from the package level.

---

#### `packages/requirements/__main__.py`
This file allows the `requirements` package to be executed as a standalone module.
It initializes the dependency management system.

**Key Responsibilities:**
- Calls the `main()` function from `dependencies.py` to handle dependency resolution.
- Provides an entry point for executing the package directly.

**Usage:**
To execute the dependency management system in standalone mode:

```python
> python -m packages.requirements ;
```

This ensures that dependency management functions can run independently when required.

---

#### `packages/requirements/dependencies.py`
This module manages project dependencies, ensuring required packages are installed
and up to date.

**Key Responsibilities:**
- Loads and parses dependency requirements from `requirements.json`.
- Checks if packages are installed and verifies their versions.
- Installs missing or outdated dependencies via `pip`.
- Updates an `installed.json` file to track package installation status.
- Logs all dependency checks and installations.

**Key Functions:**
- `load_requirements(requirements_file)`: Loads dependencies from a JSON file.
- `is_package_installed(package, version_info)`: Checks if a package is installed with the correct version.
- `install_package(package, version_info)`: Installs a specified package version.
- `install_requirements(requirements_file)`: Installs all required dependencies.
- `update_installed_packages(requirements_file)`: Updates `installed.json` with package installation status.
- `main()`: Parses command-line arguments and runs the dependency installation process.

**Usage:**
To install dependencies from the default `requirements.json`:

```python
> python lib/dependencies.py ;
```

To specify a custom requirements file:

python lib/dependencies.py -f /path/to/custom.json
This module ensures the framework has all necessary dependencies installed.

---

## Scripts (`scripts/`)

#### `scripts/devops-workflow.py`
This script ensures user privileges, dependencies, and environment configurations
are validated before execution.

**Key Responsibilities:**
- Installs required dependencies dynamically.
- Loads and validates system parameters.
- Interactively prompts users for missing input values.
- Cleans up temporary files (`__pycache__`) before execution.

**Key Functions:**
- `remove_pycache()`: Removes the `lib/__pycache__` directory to prevent stale bytecode execution.
- `request_input(var_name)`: Prompts users for missing environment variables interactively.
- `main()`: Manages runtime parameters and executes system checks.

**Usage:**
To verify system privileges and environment configurations:

```python
> python scripts/devops-workflow.py ;
```

This script ensures a clean and well-configured runtime environment.

---

#### `.env`
This file defines environment variables dynamically at runtime. It is used to store
user-provided configurations and standardized execution parameters.

**Key Responsibilities:**
- Stores required input parameters such as `environment`, `project_domain`, and `resource_group`.
- Holds optional project-specific configurations.
- Contains standardized parameters for execution settings.
- **Excluded from version control** (`.gitignore`) to prevent storing sensitive data.

**Structure:**
- **Required Parameters:** Must be set by the user before execution.
- **Optional Parameters:** Project-specific configurations that can be adjusted.
- **Standardized Parameters:** Default execution behaviors managed by the framework.

**Regeneration & Updates:**
- If deleted or found invalid, this file is **automatically regenerated**.
- During execution, missing values prompt interactive user input.
- Any provided CLI arguments override values in `.env`.
- **Header Preservation:**
  - The `.env` file includes a structured header that explains its purpose and usage.
  - This header is **stored separately** in `./configs/.env.header`.
  - During regeneration or updates, the content of `./configs/.env.header` is **appended** to `.env` to ensure documentation is retained.

**Example Usage:**
To manually define environment variables:

```ini
environment=production
project_domain=my_project
resource_group=my_resource_group
```

If values are missing, the framework will prompt the user interactively.

---

#### `run.py`
This script serves as the main execution entry point for the framework.
It automatically runs the `devops-workflow.py` script to validate user privileges
and ensure system configurations and dependencies are properly set up.

**Key Responsibilities:**
- Launches the `devops-workflow.py` script to set up the runtime environment.
- Ensures required parameters and dependencies are validated before execution.
- Provides a single-command startup mechanism.

**Key Functions:**
- Uses `subprocess.run()` to execute `devops-workflow.py`.

**Usage:**
To start the framework:

```python
> python run.py ;
```

This script ensures a structured and validated execution environment before launching the main workflow.

---

This document serves as a reference for understanding the project's structure and components.<br />
Keep it updated as the project evolves.
