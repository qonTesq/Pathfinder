"""
Floorplan Renderer Module for Pathfinder Visualizer.

This module contains the FloorplanRenderer class responsible for all
canvas drawing operations. It handles:
- Rendering the floorplan grid with ward colors
- Drawing cell and ward boundaries
- Creating and managing position markers (start/goal)
- Visualizing paths and explored nodes
- Managing visual element layering and updates

The renderer separates all drawing logic from the main visualizer,
providing a clean interface for visual updates and maintaining
consistent appearance across the application.
"""

import logging
import tkinter as tk

from ..config import GRID_CELL_SIZE, WARDS, UIColours

logger = logging.getLogger(__name__)


class FloorplanRenderer:
    """
    Handles all canvas rendering operations for the floorplan visualizer.

    This class is responsible for drawing and updating all visual elements
    on the canvas, including:
    - Floorplan grid with ward-specific colors
    - Cell boundaries and ward separators
    - Start and goal position markers
    - Path visualization with connecting lines
    - Explored node indicators
    - Edge walls (managed by editor but drawn here)

    The renderer maintains visual consistency and proper layering of
    elements, ensuring markers and paths appear above the grid while
    boundaries remain visible.

    Attributes:
        vis: Reference to the parent FloorplanVisualizer instance
    """

    def __init__(self, visualizer) -> None:
        """
        Initialize the FloorplanRenderer with a reference to the visualizer.

        Args:
            visualizer: The parent FloorplanVisualizer instance
        """
        self.vis = visualizer

        # Pre-compute color map for all cells to avoid repeated lookups
        self._color_map = self.build_color_map()

    def build_color_map(self) -> dict:
        """
        Pre-compute color map for all cells in the floorplan.

        This optimization eliminates repeated string conversions and dictionary
        lookups during rendering by caching colors at initialization.

        Returns:
            dict: Mapping of (row, col) to color hex code
        """
        color_map = {}
        rows, cols = self.vis.floorplan.shape

        for row in range(rows):
            for col in range(cols):
                cell_value = str(self.vis.floorplan[row, col])

                if cell_value == "0":
                    color = UIColours.CORRIDOR.value
                elif cell_value == "1":
                    color = UIColours.WALL.value
                else:
                    ward = WARDS.get(cell_value)
                    color = ward.colour if ward else UIColours.UNKNOWN.value

                color_map[(row, col)] = color

        return color_map

    def colour_for_cell(self, row, col) -> str:
        """
        Get the pre-computed display color for a cell.

        Uses cached color map to avoid repeated string conversions and
        dictionary lookups, providing O(1) color retrieval.

        Args:
            row: Row index of the cell
            col: Column index of the cell

        Returns:
            str: Hex color code for the cell
        """
        return self._color_map.get((row, col), UIColours.UNKNOWN.value)

    def draw_floorplan(self) -> None:
        """
        Draw the complete floorplan grid on the canvas.

        This is the main rendering method that:
        1. Clears the canvas
        2. Draws all grid cells with appropriate colors
        3. Draws cell boundaries (walls)
        4. Redraws edge walls on top

        Called during initialization and when the floorplan needs to be
        completely refreshed (e.g., after mode changes).
        """
        # Clear all existing canvas elements
        self.vis.canvas.delete("all")
        self.vis.cell_items.clear()
        self.vis.wall_items.clear()

        # Draw each cell in the grid
        for row in range(self.vis.rows):
            for col in range(self.vis.cols):
                self.draw_cell(row, col)

        # Draw boundaries between cells and wards
        self.draw_cell_boundaries()

        # Redraw edge walls on top of grid
        self.vis.editor.redraw_edge_walls()

    def draw_cell(self, row, col) -> None:
        """
        Draw a single cell on the canvas with appropriate color.

        Creates a rectangle with the cell's ward-specific color and
        a gray outline. The cell ID is stored for potential updates.

        Args:
            row: Row index of the cell
            col: Column index of the cell
        """
        # Calculate cell position on canvas
        x1 = col * GRID_CELL_SIZE
        y1 = row * GRID_CELL_SIZE
        x2 = x1 + GRID_CELL_SIZE
        y2 = y1 + GRID_CELL_SIZE

        # Get appropriate color for this cell
        colour = self.colour_for_cell(row, col)

        # Create rectangle with color fill and gray outline
        rect_id = self.vis.canvas.create_rectangle(
            x1, y1, x2, y2, fill=colour, outline="gray", tags="cell"
        )

        # Store cell ID for future reference
        self.vis.cell_items[(row, col)] = rect_id

    def draw_ward_boundaries(self) -> None:
        """
        Draw boundaries between different wards (not currently used).

        This method would draw thicker lines between cells with different
        ward values, creating visual separation between hospital areas.
        Currently, draw_cell_boundaries is used instead for a cleaner look.

        Note: Kept for potential future use or alternative rendering modes.
        """
        for row in range(self.vis.rows):
            for col in range(self.vis.cols):
                current_value = str(self.vis.floorplan[row, col])

                # Check right neighbor for ward boundary
                if col < self.vis.cols - 1:
                    right_value = str(self.vis.floorplan[row, col + 1])
                    if (
                        current_value != right_value
                        and current_value != "1"
                        and right_value != "1"
                    ):
                        # Draw vertical line between different wards
                        x = (col + 1) * GRID_CELL_SIZE
                        y_start = row * GRID_CELL_SIZE
                        y_end = (row + 1) * GRID_CELL_SIZE
                        line_id = self.vis.canvas.create_line(
                            x, y_start, x, y_end, fill=UIColours.BOUNDARY.value, width=2
                        )
                        self.vis.wall_items.append(line_id)

                # Check bottom neighbor for ward boundary
                if row < self.vis.rows - 1:
                    bottom_value = str(self.vis.floorplan[row + 1, col])
                    if (
                        current_value != bottom_value
                        and current_value != "1"
                        and bottom_value != "1"
                    ):
                        # Draw horizontal line between different wards
                        y = (row + 1) * GRID_CELL_SIZE
                        x_start = col * GRID_CELL_SIZE
                        x_end = (col + 1) * GRID_CELL_SIZE
                        line_id = self.vis.canvas.create_line(
                            x_start, y, x_end, y, fill=UIColours.BOUNDARY.value, width=2
                        )
                        self.vis.wall_items.append(line_id)

    def draw_cell_boundaries(self) -> None:
        """
        Draw boundaries around wall cells to make them visually distinct.

        Wall cells get thin boundary lines on edges that border non-wall
        cells, creating a clear separation between walls and walkable areas.
        This improves visual clarity without cluttering the display.

        Boundaries are only drawn on edges where the wall meets a non-wall,
        avoiding redundant internal lines within wall blocks.
        """
        for row in range(self.vis.rows):
            for col in range(self.vis.cols):
                # Only draw boundaries for wall cells
                if str(self.vis.floorplan[row, col]) != "1":
                    continue

                # Calculate cell boundaries
                x1 = col * GRID_CELL_SIZE
                y1 = row * GRID_CELL_SIZE
                x2 = x1 + GRID_CELL_SIZE
                y2 = y1 + GRID_CELL_SIZE

                # Draw top boundary if needed
                if row == 0 or str(self.vis.floorplan[row - 1, col]) != "1":
                    line_id = self.vis.canvas.create_line(
                        x1, y1, x2, y1, fill=UIColours.BOUNDARY.value, width=1
                    )
                    self.vis.wall_items.append(line_id)

                # Draw bottom boundary if needed
                if (
                    row == self.vis.rows - 1
                    or str(self.vis.floorplan[row + 1, col]) != "1"
                ):
                    line_id = self.vis.canvas.create_line(
                        x1, y2, x2, y2, fill=UIColours.BOUNDARY.value, width=1
                    )
                    self.vis.wall_items.append(line_id)

                # Draw left boundary if needed
                if col == 0 or str(self.vis.floorplan[row, col - 1]) != "1":
                    line_id = self.vis.canvas.create_line(
                        x1, y1, x1, y2, fill=UIColours.BOUNDARY.value, width=1
                    )
                    self.vis.wall_items.append(line_id)

                # Draw right boundary if needed
                if (
                    col == self.vis.cols - 1
                    or str(self.vis.floorplan[row, col + 1]) != "1"
                ):
                    line_id = self.vis.canvas.create_line(
                        x2, y1, x2, y2, fill=UIColours.BOUNDARY.value, width=1
                    )
                    self.vis.wall_items.append(line_id)

    def draw_position_marker(self, pos, marker_type, index=None) -> tuple:
        """
        Draw a circular marker for start or goal positions.

        Markers are color-coded:
        - Start: Green circle with "S" label
        - Goal: Red circle with "G#" label (where # is the goal number)

        The markers are drawn as circles with contrasting borders and
        centered text labels for clear identification.

        Args:
            pos: Tuple (row, col) of the marker position
            marker_type: String "start" or "goal" indicating marker type
            index: Optional goal number for goal markers (1-indexed)

        Returns:
            tuple: (marker_id, label_id) canvas item IDs for the marker components
        """
        row, col = pos

        # Calculate cell boundaries and center point
        x1 = col * GRID_CELL_SIZE
        y1 = row * GRID_CELL_SIZE
        x2 = x1 + GRID_CELL_SIZE
        y2 = y1 + GRID_CELL_SIZE
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        radius = GRID_CELL_SIZE // 3

        if marker_type == "start":
            # Draw green start marker with "S" label
            marker_id = self.vis.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill="#4CAF50",  # Material green
                outline="#2E7D32",  # Darker green border
                width=2,
                tags=("start_marker",),
            )
            label_id = self.vis.canvas.create_text(
                cx,
                cy,
                text="S",
                fill="#FFFFFF",  # White text
                font=("Arial", 9, "bold"),
                tags=("start_marker",),
            )
            # Store marker IDs for later access
            self.vis.start_marker = marker_id
            self.vis.start_label = label_id
            return marker_id, label_id

        # Draw red goal marker with "G#" label
        marker_id = self.vis.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill="#F44336",  # Material red
            outline="#C62828",  # Darker red border
            width=2,
            tags=("goal_marker",),
        )
        label_id = None
        if index is not None:
            # Add goal number label
            label_id = self.vis.canvas.create_text(
                cx,
                cy,
                text=f"G{index}",
                fill="#FFFFFF",  # White text
                font=("Arial", 7, "bold"),
                tags=("goal_marker",),
            )
        # Store marker IDs for this goal position
        self.vis.goal_markers[pos] = (marker_id, label_id)
        return marker_id, label_id

    def redraw_markers_on_top(self, goals_to_show=None) -> None:
        """
        Redraw position markers on top of other canvas elements.

        This ensures markers remain visible above paths, explored nodes,
        and other visual elements by deleting and recreating them at the
        top of the canvas drawing order.

        Used after drawing paths or during animation to maintain marker
        visibility and proper layering.

        Args:
            goals_to_show: Optional list of goal positions to redraw.
                          If None, all goals are redrawn.
        """
        if goals_to_show is None:
            goals_to_show = self.vis.goals

        # Redraw start marker if it exists
        if self.vis.start_pos and self.vis.start_marker:
            # Delete existing marker elements
            self.vis.canvas.delete(self.vis.start_marker)
            if self.vis.start_label:
                self.vis.canvas.delete(self.vis.start_label)

            # Calculate marker position
            row, col = self.vis.start_pos
            x1 = col * GRID_CELL_SIZE
            y1 = row * GRID_CELL_SIZE
            x2 = x1 + GRID_CELL_SIZE
            y2 = y1 + GRID_CELL_SIZE
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            radius = GRID_CELL_SIZE // 3

            # Recreate start marker on top
            self.vis.start_marker = self.vis.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill="#4CAF50",
                outline="#2E7D32",
                width=2,
                tags=("start_marker",),
            )
            self.vis.start_label = self.vis.canvas.create_text(
                cx,
                cy,
                text="S",
                fill="#FFFFFF",
                font=("Arial", 9, "bold"),
                tags=("start_marker",),
            )

        # Redraw specified goal markers
        for goal_pos in goals_to_show:
            if goal_pos in self.vis.goal_markers:
                # Delete existing marker elements
                marker_id, label_id = self.vis.goal_markers[goal_pos]
                if marker_id:
                    self.vis.canvas.delete(marker_id)
                if label_id:
                    self.vis.canvas.delete(label_id)

            # Get goal index (1-indexed for display)
            goal_index = self.vis.goals.index(goal_pos) + 1

            # Calculate marker position
            row, col = goal_pos
            x1 = col * GRID_CELL_SIZE
            y1 = row * GRID_CELL_SIZE
            x2 = x1 + GRID_CELL_SIZE
            y2 = y1 + GRID_CELL_SIZE
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            radius = GRID_CELL_SIZE // 3

            # Recreate goal marker on top
            marker_id = self.vis.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill="#F44336",
                outline="#C62828",
                width=2,
                tags=("goal_marker",),
            )
            label_id = self.vis.canvas.create_text(
                cx,
                cy,
                text=f"G{goal_index}",
                fill="#FFFFFF",
                font=("Arial", 7, "bold"),
                tags=("goal_marker",),
            )
            # Update stored marker IDs
            self.vis.goal_markers[goal_pos] = (marker_id, label_id)

    def draw_path(self, path) -> None:
        """
        Draw the complete path on the canvas.

        The path is visualized with:
        - Semi-transparent gray background on path cells
        - White lines connecting consecutive cells
        - Smart clipping at start/goal markers to avoid overlap
        - Rounded line caps and joins for smooth appearance

        This method draws the final complete path after pathfinding
        and animation are complete.

        Args:
            path: List of (row, col) tuples representing the path
        """
        if not path:
            return

        # Draw background rectangles for path cells
        for pos in path:
            row, col = pos

            # Calculate cell boundaries with small inset
            x1 = col * GRID_CELL_SIZE + 1
            y1 = row * GRID_CELL_SIZE + 1
            x2 = x1 + GRID_CELL_SIZE - 2
            y2 = y1 + GRID_CELL_SIZE - 2

            # Create semi-transparent background using stipple
            bg_rect = self.vis.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="dimgray",
                outline="",
                width=0,
                stipple="gray50",  # Creates semi-transparent effect
                tags="path",
            )
            self.vis.path_items.append(bg_rect)

        # Draw connecting lines between consecutive path cells
        for i in range(len(path) - 1):
            row1, col1 = path[i]
            row2, col2 = path[i + 1]

            # Calculate center points of both cells
            x1 = col1 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            y1 = row1 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            x2 = col2 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            y2 = row2 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2

            # Clip line at start marker to avoid overlap
            if path[i] == self.vis.start_pos:
                dx = x2 - x1
                dy = y2 - y1
                distance = (dx**2 + dy**2) ** 0.5
                if distance > 0:
                    # Normalize direction vector
                    dx /= distance
                    dy /= distance
                    # Move start point away from marker center
                    clip_distance = GRID_CELL_SIZE // 3
                    x1 += dx * clip_distance
                    y1 += dy * clip_distance

            # Clip line at goal marker to avoid overlap
            if path[i + 1] in self.vis.goals:
                dx = x1 - x2
                dy = y1 - y2
                distance = (dx**2 + dy**2) ** 0.5
                if distance > 0:
                    # Normalize direction vector
                    dx /= distance
                    dy /= distance
                    # Move end point away from marker center
                    clip_distance = GRID_CELL_SIZE // 3
                    x2 += dx * clip_distance
                    y2 += dy * clip_distance

            # Draw path line with rounded caps and joins
            line = self.vis.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="white",
                width=3,
                tags="path",
                capstyle=tk.ROUND,  # Rounded line ends
                joinstyle=tk.ROUND,  # Rounded corners at turns
            )
            self.vis.path_items.append(line)

    def draw_explored_cells(self, explored_cells) -> None:
        """
        Draw small dots on cells explored during pathfinding.

        Explored cells are visualized as small colored dots to show
        which cells the algorithm examined. This helps users understand:
        - The search space coverage
        - Algorithm efficiency (A* vs Dijkstra)
        - How heuristics guide the search

        Start and goal cells are excluded from visualization as they
        already have prominent markers.

        Args:
            explored_cells: List of Cell objects explored during search
        """
        # Check if visualization is enabled
        if not self.vis.show_explored_var.get():
            return

        for cell in explored_cells:
            row, col = cell.position

            # Skip start and goal positions (already have markers)
            if (row, col) == self.vis.start_pos or (row, col) in self.vis.goals:
                continue

            # Calculate center of cell
            cx = col * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            cy = row * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            radius = 1  # Small dot

            # Draw exploration indicator dot
            dot = self.vis.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill=UIColours.EXPLORED.value,
                outline="",  # No outline for cleaner appearance
                tags="explored",
            )
            self.vis.explored_items.append(dot)
