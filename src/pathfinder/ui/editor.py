"""
Edge Wall Editor Module for Pathfinder Visualizer.

This module contains the EdgeWallEditor class responsible for managing
edge wall editing functionality. Edge walls are barriers placed between
adjacent cells that block pathfinding without being full wall cells.

Users can toggle edge walls by:
1. Clicking a cell to select it
2. Clicking an adjacent cell to add/remove a wall between them
"""

import logging

from ..config import GRID_CELL_SIZE, UIColours

logger = logging.getLogger(__name__)


class EdgeWallEditor:
    """
    Manages edge wall editing operations in the floorplan visualizer.

    Edge walls are dynamic barriers between adjacent cells that can be
    added or removed by users. This class handles:
    - Click processing for cell selection
    - Visual markers for selected and adjacent cells
    - Edge wall creation and removal
    - Edge wall rendering
    - Persistence operations (save/load)

    Attributes:
        vis: Reference to the parent FloorplanVisualizer instance
    """

    def __init__(self, visualizer) -> None:
        """
        Initialize the EdgeWallEditor with a reference to the visualizer.

        Args:
            visualizer: The parent FloorplanVisualizer instance
        """
        self.vis = visualizer

    def handle_edit_click(self, row, col) -> None:
        """
        Handle a click event in edit mode to toggle edge walls.

        The first click selects a cell and shows adjacent options.
        The second click on an adjacent cell toggles an edge wall.
        Non-adjacent clicks are ignored.

        Args:
            row: The row index of the clicked cell
            col: The column index of the clicked cell
        """
        if self.vis.edit_first is None:
            # First click: Select the initial cell
            self.vis.edit_first = (row, col)
            self.draw_edit_selection_marker(row, col)
            self.draw_adjacent_markers(row, col)
            self.vis.update_path_stats()
            logger.info(f"Edit mode: First cell selected at {(row, col)}")
        else:
            # Second click: Attempt to toggle edge wall
            first_row, first_col = self.vis.edit_first

            if self.are_adjacent((first_row, first_col), (row, col)):
                # Create edge identifier as frozenset for bidirectional lookup
                edge = frozenset([(first_row, first_col), (row, col)])

                if edge in self.vis.manager.edge_walls:
                    # Remove existing edge wall
                    self.vis.manager.edge_walls.discard(edge)
                    logger.info(
                        f"Removed edge wall between {self.vis.edit_first} and {(row, col)}"
                    )
                else:
                    # Add new edge wall
                    self.vis.manager.edge_walls.add(edge)
                    logger.info(
                        f"Added edge wall between {self.vis.edit_first} and {(row, col)}"
                    )

                # Update pathfinder with new edge walls
                self.vis.pathfinder.edge_walls = self.vis.manager.edge_walls

                # Redraw to show changes
                self.redraw_edge_walls()
            else:
                # Cells are not adjacent, log warning
                logger.warning(
                    f"Cells {self.vis.edit_first} and {(row, col)} are not adjacent"
                )

            # Clear selection markers and reset state
            self.clear_edit_marker()
            self.clear_adjacent_markers()
            self.vis.edit_first = None
            self.vis.update_path_stats()

    def are_adjacent(self, pos1, pos2) -> bool:
        """
        Check if two cells are adjacent (horizontally or vertically).

        Args:
            pos1: Tuple (row, col) of first cell
            pos2: Tuple (row, col) of second cell

        Returns:
            bool: True if cells are adjacent, False otherwise
        """
        r1, c1 = pos1
        r2, c2 = pos2

        # Check horizontal adjacency (same row, columns differ by 1)
        if r1 == r2 and abs(c1 - c2) == 1:
            return True

        # Check vertical adjacency (same column, rows differ by 1)
        if c1 == c2 and abs(r1 - r2) == 1:
            return True

        return False

    def edge_line_coords(self, pos1, pos2) -> tuple:
        """
        Calculate the canvas coordinates for drawing an edge wall line.

        Edge walls are drawn on the boundary between two cells.
        Horizontal edges are vertical lines, vertical edges are horizontal lines.

        Args:
            pos1: Tuple (row, col) of first cell
            pos2: Tuple (row, col) of second cell

        Returns:
            tuple: (x1, y1, x2, y2) coordinates for the line
        """
        r1, c1 = pos1
        r2, c2 = pos2

        if r1 == r2:
            # Horizontal adjacency: draw vertical line between columns
            col_min = min(c1, c2)
            x = (col_min + 1) * GRID_CELL_SIZE
            y1 = r1 * GRID_CELL_SIZE
            y2 = (r1 + 1) * GRID_CELL_SIZE
            return (x, y1, x, y2)

        else:
            # Vertical adjacency: draw horizontal line between rows
            row_min = min(r1, r2)
            y = (row_min + 1) * GRID_CELL_SIZE
            x1 = c1 * GRID_CELL_SIZE
            x2 = (c1 + 1) * GRID_CELL_SIZE
            return (x1, y, x2, y)

    def update_edge_wall_line(self, edge) -> None:
        """
        Update or create the visual representation of a single edge wall.

        If the edge already has a visual element, it's deleted and recreated
        to ensure proper layering and appearance.

        Args:
            edge: Frozenset containing two cell positions defining the edge
        """
        # Convert frozenset to list to access positions
        pos1, pos2 = list(edge)
        x1, y1, x2, y2 = self.edge_line_coords(pos1, pos2)

        # Delete existing line if present
        if edge in self.vis.edge_wall_items:
            self.vis.canvas.delete(self.vis.edge_wall_items[edge])

        # Draw new edge wall line
        line_id = self.vis.canvas.create_line(
            x1, y1, x2, y2, fill=UIColours.EDGE_WALL.value, width=3, tags="edge_wall"
        )
        self.vis.edge_wall_items[edge] = line_id

    def redraw_edge_walls(self) -> None:
        """
        Redraw all edge walls on the canvas.

        This clears all existing edge wall visual elements and recreates
        them from the current edge_walls set. Used after modifications
        to ensure consistency.
        """
        # Clear all existing edge wall visuals
        for line_id in self.vis.edge_wall_items.values():
            self.vis.canvas.delete(line_id)
        self.vis.edge_wall_items.clear()

        # Redraw all edge walls
        for edge in self.vis.manager.edge_walls:
            self.update_edge_wall_line(edge)

    def draw_edit_selection_marker(self, row, col) -> None:
        """
        Draw a visual marker around the selected cell in edit mode.

        The marker is a colored rectangle outline indicating the first
        cell selected for edge wall editing.

        Args:
            row: Row index of the selected cell
            col: Column index of the selected cell
        """
        # Calculate cell boundaries with small inset
        x1 = col * GRID_CELL_SIZE + 2
        y1 = row * GRID_CELL_SIZE + 2
        x2 = x1 + GRID_CELL_SIZE - 4
        y2 = y1 + GRID_CELL_SIZE - 4

        # Draw selection rectangle
        self.vis.edit_marker = self.vis.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            outline=UIColours.EDIT_SELECTION.value,
            width=3,
            fill="",  # No fill, just outline
            tags="edit_marker",
        )

    def clear_edit_marker(self) -> None:
        """
        Remove the edit selection marker from the canvas.

        Called when completing an edit operation or canceling selection.
        """
        if self.vis.edit_marker:
            self.vis.canvas.delete(self.vis.edit_marker)
            self.vis.edit_marker = None

    def draw_adjacent_markers(self, row, col) -> None:
        """
        Draw visual markers around cells adjacent to the selected cell.

        These markers indicate which cells can be clicked to toggle
        an edge wall with the selected cell.

        Args:
            row: Row index of the selected cell
            col: Column index of the selected cell
        """
        # Define all four adjacent positions (up, down, left, right)
        adjacent_positions = [
            (row - 1, col),  # Above
            (row + 1, col),  # Below
            (row, col - 1),  # Left
            (row, col + 1),  # Right
        ]

        # Draw marker for each valid adjacent position
        for adj_row, adj_col in adjacent_positions:
            # Check if position is within grid bounds
            if 0 <= adj_row < self.vis.rows and 0 <= adj_col < self.vis.cols:
                # Calculate cell boundaries with small inset
                x1 = adj_col * GRID_CELL_SIZE + 2
                y1 = adj_row * GRID_CELL_SIZE + 2
                x2 = x1 + GRID_CELL_SIZE - 4
                y2 = y1 + GRID_CELL_SIZE - 4

                # Draw adjacent marker rectangle
                marker = self.vis.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline=UIColours.EDIT_ADJACENT.value,
                    width=2,
                    fill="",  # No fill, just outline
                    tags="adjacent_marker",
                )
                self.vis.adjacent_markers.append(marker)

    def clear_adjacent_markers(self) -> None:
        """
        Remove all adjacent cell markers from the canvas.

        Called when completing an edit operation or canceling selection.
        """
        for marker in self.vis.adjacent_markers:
            self.vis.canvas.delete(marker)
        self.vis.adjacent_markers.clear()

    def save_edits(self) -> None:
        """
        Persist the current edge walls to file.

        Delegates to the floorplan manager to save edge walls to JSON.
        Raises an exception if the save operation fails.

        Raises:
            Exception: If edge wall saving fails
        """
        try:
            self.vis.manager.save_edge_walls()
            logger.info("Edge walls saved successfully")
        except Exception as e:
            logger.error(f"Failed to save edge walls: {e}")
            raise

    def clear_all_edits(self) -> None:
        """
        Revert all edge wall changes to the last saved state.

        This reloads edge walls from file, discarding any unsaved changes,
        and updates both the pathfinder and visual display.
        """
        # Reload edge walls from file
        self.vis.manager.load_edge_walls()
        # Update pathfinder with reverted edge walls
        self.vis.pathfinder.edge_walls = self.vis.manager.edge_walls
        # Refresh visual display
        self.redraw_edge_walls()
        logger.info("Edge walls reverted to last saved state")
