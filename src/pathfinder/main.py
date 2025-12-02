"""
Pathfinder application - Main Entry Point.

This module serves as the main entry point for the Pathfinder application.
It initializes the application, loads floorplan data, sets up the GUI, and starts
the main event loop.

The application provides a graphical interface for visualizing and interacting
with hospital floorplans, including features for:
- Floorplan visualization and navigation
- Pathfinding using A* and Dijkstra algorithms
- Interactive editing of walls and paths
- Hospital ward information and routing
- Dark mode support across platforms

Functions:
    main: Initialize and run the Pathfinder application
"""

import logging
import tkinter as tk

from .data import FLOORPLAN, FloorplanManager
from .ui import FloorplanVisualizer
from .utils import apply_theme, get_resource_path, initialize_user_data, setup_logger

# Initialize logger for this module
logger: logging.Logger = setup_logger(__name__)


def main() -> None:
    """
    Initialize and run the Pathfinder application.

    This is the main entry point for the application. It:
    1. Loads the floorplan data
    2. Creates the floorplan manager for pathfinding operations
    3. Initializes the Tkinter root window
    4. Applies appropriate theming
    5. Creates the main GUI visualizer
    6. Starts the event loop

    The function includes comprehensive error handling to catch and log
    any issues during startup. Critical errors are logged and re-raised
    to prevent silent failures.

    Returns:
        None: The function blocks until the user closes the application.

    Raises:
        Exception: Any unexpected errors during application initialization
                  are logged and re-raised for debugging purposes.

    Workflow:
        1. Load FLOORPLAN data from the data module
        2. Initialize FloorplanManager with edge walls from JSON
        3. Create Tkinter root window
        4. Apply platform-specific theming
        5. Initialize FloorplanVisualizer with the root window
        6. Log successful startup
        7. Enter Tkinter event loop (blocks until window closes)

    Example:
        >>> main()  # Starts the application and blocks until window closes
    """

    try:
        # Log the start of the initialization process
        logger.info("Loading floorplan data from Python module")

        # Initialize edge_walls.json by copying bundled default to writable location
        # Dev: src/pathfinder/data/edge_walls.json
        # Prod: data/edge_walls.json (next to .exe)
        edge_walls_path = initialize_user_data(
            "src/pathfinder/data/edge_walls.json",  # Bundled default file
            "edge_walls.json",  # User file in data/ folder
        )

        # Initialize floor plan manager with floor plan data
        manager = FloorplanManager(FLOORPLAN, edge_walls_path=edge_walls_path)

        # Create the root Tkinter window for the application
        root = tk.Tk()

        # Set window icon (title bar and taskbar)
        try:
            icon_path = get_resource_path("src/pathfinder/assets/icon.ico")
            if icon_path.exists():
                root.iconbitmap(str(icon_path))
                logger.info(f"Loaded application icon from {icon_path}")
            else:
                logger.warning(
                    f"Icon file not found at {icon_path} - using default icon"
                )
        except Exception as e:
            logger.warning(f"Could not load application icon: {e} - using default icon")

        # Apply platform-specific theming (dark mode, OS styling, etc.)
        apply_theme(root)

        # Initialize the main UI visualizer with the window and manager
        # This creates all UI elements and sets up event handlers
        FloorplanVisualizer(root, manager)

        # Log successful application startup
        logger.info("Application started successfully")

        # Start the Tkinter event loop
        # This call blocks until the user closes the window
        root.mainloop()

    except Exception as e:
        # Log critical errors that occur during startup
        # Include the exception for debugging purposes
        logger.critical(f"Unexpected error during application startup: {e}")
        # Re-raise the exception to make the failure obvious
        raise


# Entry point for running the module directly
if __name__ == "__main__":
    main()
