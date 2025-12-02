"""
UI Module for Pathfinder Visualizer.

This module provides the complete user interface system for visualizing
pathfinding algorithms on hospital floorplans. It includes components for:
- Rendering the floorplan grid
- Handling user interactions (clicks, mode changes)
- Animating pathfinding algorithms
- Editing edge walls
- Displaying statistics and controls

The module is organized into separate components for maintainability:
- visualizer: Main UI coordinator
- renderer: Handles all canvas drawing operations
- animator: Manages path animation sequences
- editor: Handles edge wall editing functionality
- builder: Constructs UI components and layout
- controller: Manages pathfinding operations
- handler: Processes user input events
- updater: Updates information display panel
"""

from .animator import PathAnimator
from .builder import UIBuilder
from .controller import PathController
from .editor import EdgeWallEditor
from .handler import InteractionHandler
from .renderer import FloorplanRenderer
from .updater import InformationUpdater
from .visualizer import FloorplanVisualizer

# Export all UI components for external use
__all__ = [
    "FloorplanVisualizer",  # Main UI coordinator
    "FloorplanRenderer",  # Canvas rendering operations
    "PathAnimator",  # Path animation controller
    "EdgeWallEditor",  # Edge wall editing functionality
    "UIBuilder",  # UI component construction
    "PathController",  # Pathfinding operations manager
    "InteractionHandler",  # User input processor
    "InformationUpdater",  # Information panel updater
]
