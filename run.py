#!/usr/bin/env python3
"""
PyInstaller Entry Point for Pathfinder Application.

This script serves as the entry point for the PyInstaller executable.
It avoids relative import issues by using absolute imports.
"""

from pathfinder import main

if __name__ == "__main__":
    main()
