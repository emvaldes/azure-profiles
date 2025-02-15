#!/usr/bin/env python3

import sys
import json
import logging

from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from packages.appflow_tracer import tracing

def main():
    global LOGGING, CONFIGS, logger  # Ensure CONFIGS is globally accessible

    CONFIGS = tracing.setup_logging()
    print(f'CONFIGS: {json.dumps(CONFIGS, indent=2)}')

    print("I am a stand-alone script minding my own business")

if __name__ == "__main__":
    main()
