"""
Configuration module for the Pathfinder application.

This package centralizes all application-wide configuration settings including:
- Grid dimensions and display properties
- UI colors and themes (with dark mode support)
- Ward definitions and metadata
- Application metadata

All configuration values are imported and re-exported here for convenient access
throughout the application.

Exports:
    GRID_WIDTH: Width of the pathfinding grid in cells
    GRID_HEIGHT: Height of the pathfinding grid in cells
    GRID_CELL_SIZE: Display size of each grid cell in pixels
    UIColours: Enum of all UI color definitions
    WARDS: Dictionary of all ward definitions
    APP_TITLE: Application window title
    DARK_MODE: Boolean indicating system dark mode preference
    LOG_LEVEL: Logging verbosity level
"""

from .settings import (
    APP_TITLE,
    DARK_MODE,
    GRID_CELL_SIZE,
    GRID_HEIGHT,
    GRID_WIDTH,
    LOG_LEVEL,
    WARDS,
    UIColours,
)

__all__ = [
    "GRID_WIDTH",
    "GRID_HEIGHT",
    "GRID_CELL_SIZE",
    "UIColours",
    "WARDS",
    "APP_TITLE",
    "DARK_MODE",
    "LOG_LEVEL",
]
