#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from lib.argument_parser import parse_arguments  ## Import the argument parser

def install_requirements(requirements_file):
    """Installs dependencies from a JSON requirements file."""
    requirements_path = Path(requirements_file).resolve()
    if not requirements_path.exists():
        raise FileNotFoundError(f"ERROR: Requirements file not found at {requirements_path}")
    try:
        with open(requirements_path, "r") as f:
            data = json.load(f)
            dependencies = [f"{pkg['package']}=={pkg['version']}" for pkg in data.get("dependencies", [])]
    except json.JSONDecodeError as e:
        raise ValueError(f"ERROR: Invalid JSON structure in '{requirements_path}'.\nDetails: {e}")
    ## Install dependencies using pip
    if dependencies:
        ## subprocess.run(["pip", "install"] + dependencies, check=True)
        ## Prevents silent failures when pip errors occur.
        try:
            subprocess.run(["pip", "install"] + dependencies, check=True)
            print("All dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install dependencies. Pip error: {e}")
            exit(1)
        except Exception as e:
            print(f"ERROR: Unexpected issue during installation. Details: {e}")
            exit(1)
    else:
        print("⚠ No dependencies found in requirements.json")

def main():
    """Main function to parse arguments and run the installer."""
    ## args = parse_arguments(context=["requirements_file"], description="Install dependencies from a JSON file")
    ## Clearly informs users they can pass a custom JSON file.
    args = parse_arguments(context=["requirements_file"], description="Install dependencies from a JSON file. Use -f to specify a custom JSON file.")
    ## Use provided requirements file path or default to configs/requirements.json
    requirements_file = args.requirements_file if args.requirements_file else "./configs/requirements.json"
    install_requirements(requirements_file)

if __name__ == "__main__":
    main()
