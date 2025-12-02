"""
Pathfinder Application Package.

This package provides a graphical interface for visualizing and interacting
with hospital floorplans, including pathfinding algorithms, interactive editing,
and hospital ward information.

Main Entry Point:
    main: Initialize and run the Pathfinder application

Usage:
    from pathfinder import main
    main()

Modules:
    - config: Application configuration (colors, grid size, wards)
    - core: Core pathfinding algorithms and logic
    - data: Floorplan data management
    - ui: User interface components
    - utils: Logging, theming, and utility functions
"""

from .main import main

__all__ = ["main"]
