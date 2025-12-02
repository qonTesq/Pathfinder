"""
Utility functions and helpers for the Pathfinder application.

This package provides utility modules and functions used across the application:

Modules:
- logger: Logging setup and configuration utilities
- theme: Theme and styling utilities for the GUI
- paths: Path utilities for resource management in bundled executables

Exports:
- setup_logger: Function to configure loggers with console and file output
- apply_theme: Function to apply platform-specific theme styling
- get_resource_path: Function to get absolute paths to resources (dev and PyInstaller)
- get_writable_path: Function to get writable paths for saving data (dev and PyInstaller)
- initialize_user_data: Function to copy default data files to writable location on first run
"""

from .logger import setup_logger
from .paths import get_resource_path, get_writable_path, initialize_user_data
from .theme import apply_theme

__all__ = [
    "setup_logger",
    "apply_theme",
    "get_resource_path",
    "get_writable_path",
    "initialize_user_data",
]
