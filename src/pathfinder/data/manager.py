"""
Floor plan data manager for Pathfinder application.

This module provides the FloorplanManager class which handles loading,
accessing, and analyzing hospital floor plan data. It serves as the
central data access layer for the pathfinding visualizer.

The manager is responsible for:
- Loading floor plan data from various sources
- Validating floor plan structure and integrity
- Providing access to floor plan cells and dimensions
- Computing statistics about wards, corridors, and walls
- Handling errors during data loading
"""

import json
import logging
from pathlib import Path
from typing import FrozenSet, Tuple

import numpy as np

from ..utils import initialize_user_data

logger = logging.getLogger(__name__)


class FloorplanManager:
    """
    Manages hospital floor plan data and provides data access methods.

    This class encapsulates floor plan data and provides a clean interface
    for other components to access and analyze the floor plan. It handles
    data validation, dimension queries, and statistical analysis.

    The floor plan is a 2D grid where each cell contains:
    - 1: Wall (impassable)
    - 0: Open corridor (passable)
    - str: Ward code (representing different hospital wards)

    Attributes:
        floorplan: NumPy array representing the hospital floor plan
    """

    def __init__(self, floorplan_data, edge_walls_path=None) -> None:
        """
        Initialize the FloorplanManager with floor plan data.

        Loads and validates the provided floor plan data during initialization.

        Args:
            floorplan_data: 2D list of lists representing the floor plan

        Raises:
            ValueError: If floorplan_data is invalid (not a list, not 2D, etc.)
            Any exception from load_floorplan()
        """
        self.floorplan = None
        self.edge_walls_path: Path = (
            Path(edge_walls_path)
            if edge_walls_path
            else initialize_user_data("src/app/data/edge_walls.json", "edge_walls.json")
        )
        # Each edge is stored as frozenset({(r1,c1), (r2,c2)})
        self.edge_walls = set()
        self.load_floorplan(floorplan_data)
        self.load_edge_walls()

    def load_floorplan(self, data) -> None:
        """
        Load and validate floor plan data.

        Converts the input data to a NumPy array and performs validation
        to ensure the data structure is valid.

        Args:
            data: 2D list of lists representing the floor plan

        Raises:
            ValueError: If data is not a valid 2D list or is empty
            Any exception from NumPy array conversion

        Logs:
            Info on successful load, error on failure
        """
        try:
            # Validate input is a list of lists
            if not isinstance(data, list):
                raise ValueError("Floorplan data must be a list of lists")
            if not all(isinstance(row, list) for row in data):
                raise ValueError("Floorplan data must be a 2D list")
            if not data:
                raise ValueError("Floorplan data cannot be empty")

            # Convert to NumPy array with object dtype to support mixed types
            # (walls as 1, corridors as 0, wards as strings)
            self.floorplan = np.array(data, dtype=object)
            logger.info(f"Loaded floorplan: shape={self.floorplan.shape}")

        except ValueError as e:
            logger.error(f"Invalid floorplan data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading floorplan: {e}")
            raise

    def get_floorplan(self) -> np.ndarray:
        """
        Get the floor plan array.

        Returns:
            NumPy array representing the floor plan

        Raises:
            RuntimeError: If floor plan has not been loaded
        """
        if self.floorplan is None:
            raise RuntimeError("Floorplan not loaded")
        return self.floorplan

    # ---------------------------
    # Edge-wall Utilities
    # ---------------------------
    @staticmethod
    def normalize_edge(a, b) -> FrozenSet[Tuple[int, int]]:
        """
        Normalize an edge between two cells into a canonical frozenset representation.

        This ensures that edges are stored consistently regardless of the order
        in which the two endpoints are provided. For example, edge (A,B) and
        edge (B,A) will produce the same frozenset, preventing duplicates.

        Args:
            a: Tuple (row, col) of first cell position
            b: Tuple (row, col) of second cell position

        Returns:
            FrozenSet containing both cell positions (order-independent)
        """
        return frozenset((a, b))

    @staticmethod
    def are_adjacent(a, b) -> bool:
        """
        Check if two cell positions are adjacent (horizontally or vertically).

        Two cells are considered adjacent if they differ by exactly 1 in either
        row or column (but not both), meaning they share an edge. Diagonal
        positions are not considered adjacent.

        Args:
            a: Tuple (row, col) of first cell position
            b: Tuple (row, col) of second cell position

        Returns:
            bool: True if cells are adjacent, False otherwise

        Examples:
            >>> are_adjacent((5, 5), (5, 6))  # Horizontally adjacent
            True
            >>> are_adjacent((5, 5), (6, 5))  # Vertically adjacent
            True
            >>> are_adjacent((5, 5), (6, 6))  # Diagonally positioned
            False
        """
        return (abs(a[0] - b[0]) == 1 and a[1] == b[1]) or (
            abs(a[1] - b[1]) == 1 and a[0] == b[0]
        )

    # ---------------------------
    # Edge Wall Persistence
    # ---------------------------
    def load_edge_walls(self) -> None:
        """
        Load edge wall data from JSON file.

        Edge walls are user-defined barriers between adjacent cells that
        restrict robot movement during pathfinding. This method loads
        previously saved edge walls from the JSON file at initialization.

        The JSON file format is a list of edge pairs:
            [ [[row1, col1], [row2, col2]], ... ]

        If the file doesn't exist, initializes with an empty set of edge walls.
        On error, logs the issue and initializes with an empty set.

        Raises:
            No exceptions are raised; errors are caught and logged

        Logs:
            Info: Number of edge walls loaded successfully
            Warning: If edge_walls.json file is not found
            Error: If loading fails due to other exceptions
        """
        try:
            if self.edge_walls_path.exists():
                # Load edge wall data from JSON file
                data = json.load(self.edge_walls_path.open("r", encoding="utf-8"))

                # Convert list format [ [[r1,c1],[r2,c2]], ... ] to set of frozensets
                # Each edge is normalized to ensure consistent representation
                self.edge_walls = {
                    self.normalize_edge(tuple(a), tuple(b))  # type: ignore[arg-type]
                    for (a, b) in data
                }
                logger.info(
                    f"Loaded {len(self.edge_walls)} edge walls from {self.edge_walls_path}"
                )
            else:
                # No saved edge walls file; start fresh
                self.edge_walls = set()
                logger.warning("No edge_walls.json found - starting with 0 edge walls")
        except Exception as e:
            # On any error, log and start with empty edge walls
            logger.error(f"Failed to load edge walls: {e}")
            self.edge_walls = set()

    def save_edge_walls(self) -> None:
        """
        Save current edge wall data to JSON file.

        Persists the current set of edge walls to the JSON file for future
        sessions. Edge walls are converted from the internal frozenset
        representation to a JSON-serializable list format.

        The saved format is a list of edge pairs:
            [ [[row1, col1], [row2, col2]], ... ]

        This method is typically called when the user exits Edit mode or
        explicitly saves their changes.

        Raises:
            No exceptions are raised; errors are caught and logged

        Logs:
            Info: Number of edge walls saved successfully
            Error: If saving fails due to file I/O or other exceptions
        """
        try:
            # Convert internal frozenset representation to JSON-serializable format
            serializable = []
            for edge in self.edge_walls:
                # Extract the two cell positions from the frozenset
                a, b = tuple(edge)
                # Convert to nested list format: [[row, col], [row, col]]
                serializable.append([[a[0], a[1]], [b[0], b[1]]])

            # Write to file with pretty formatting (indent=2)
            self.edge_walls_path.write_text(
                json.dumps(serializable, indent=2), encoding="utf-8"
            )

            logger.info(
                f"Saved {len(self.edge_walls)} edge walls to {self.edge_walls_path}"
            )
        except Exception as e:
            # Log any file I/O or serialization errors
            logger.error(f"Failed to save edge walls: {e}")

    def get_dimensions(self) -> tuple:
        """
        Get the dimensions of the floor plan.

        Returns:
            Tuple of (rows, cols) representing floor plan dimensions

        Raises:
            RuntimeError: If floor plan has not been loaded
        """
        if self.floorplan is None:
            raise RuntimeError("Floorplan not loaded")
        return self.floorplan.shape
