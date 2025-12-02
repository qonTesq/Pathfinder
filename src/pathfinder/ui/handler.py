"""
Interaction Handler Module for Pathfinder Visualizer.

This module contains the InteractionHandler class responsible for processing
all user interactions with the visualizer interface. It handles:
- Mouse click events on the canvas
- Mode switching (Search vs Edit)
- Algorithm selection changes
- Visualization toggle events
- Save/clear operations

The handler acts as a bridge between user input and the various UI components,
delegating actions to appropriate specialized classes while maintaining overall
interaction flow and state consistency.
"""

import logging
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger(__name__)


class InteractionHandler:
    """
    Processes user interactions and coordinates UI component responses.

    This class serves as the central event handler for user input,
    managing the interaction flow between the user and the visualizer.
    It handles:
    - Canvas click events for setting start/goal positions or editing walls
    - Mode changes between Search and Edit modes
    - Algorithm selection (A* vs Dijkstra)
    - Visualization options (show/hide explored nodes)
    - Save and clear operations

    The handler maintains consistency across modes by showing/hiding
    appropriate controls and clearing incompatible state when switching.

    Attributes:
        vis: Reference to the parent FloorplanVisualizer instance
    """

    def __init__(self, visualizer) -> None:
        """
        Initialize the InteractionHandler with a reference to the visualizer.

        Args:
            visualizer: The parent FloorplanVisualizer instance
        """
        self.vis = visualizer

    def on_canvas_click(self, event) -> None:
        """
        Handle mouse click events on the floorplan canvas.

        Behavior depends on current mode:
        - Search mode: Sets start position (first click) or adds goal (subsequent clicks)
        - Edit mode: Toggles edge walls between selected adjacent cells

        Click validation:
        - Must be within grid bounds
        - Cannot select wall cells (value == "1")
        - In Search mode, prevents duplicate positions
        - In Search mode, limits goals to 15 maximum
        - In Search mode, prevents adding goals after path computation

        Args:
            event: Tkinter mouse click event containing x, y coordinates
        """
        from ..config import GRID_CELL_SIZE

        # Convert canvas coordinates to grid coordinates
        col = event.x // GRID_CELL_SIZE
        row = event.y // GRID_CELL_SIZE

        # Validate click is within grid bounds
        if not (0 <= row < self.vis.rows and 0 <= col < self.vis.cols):
            return

        # Check if cell is a wall (cannot be selected)
        # Direct integer comparison is faster than string conversion
        if self.vis.floorplan[row, col] == 1:
            messagebox.showwarning("Invalid Position", "Cannot select a wall cell.")
            return

        # Route to appropriate handler based on mode
        if self.vis.mode == "edit":
            # Edit mode: Handle edge wall editing
            self.vis.editor.handle_edit_click(row, col)
        else:
            # Search mode: Handle start/goal position setting
            if self.vis.start_pos is None:
                # First click sets start position
                self.set_start_position((row, col))
            else:
                pos = (row, col)

                # Prevent setting start as goal
                if pos == self.vis.start_pos:
                    messagebox.showinfo(
                        "Already Selected",
                        "This cell is already set as the start position.",
                    )
                    return

                # Prevent duplicate goals
                if pos in self.vis.goals:
                    messagebox.showinfo(
                        "Already Selected",
                        "This cell is already added as a goal.",
                    )
                    return

                # Prevent adding goals after path is computed
                if self.vis.current_path:
                    messagebox.showinfo(
                        "Path Already Computed",
                        "Please clear the current path before adding new goals.",
                    )
                    return

                # Enforce maximum of 15 goals
                if len(self.vis.goals) >= 15:
                    messagebox.showwarning(
                        "Maximum Goals",
                        "Maximum of 15 goals reached. Clear path to add more.",
                    )
                    return

                # Add new goal position
                self.vis.goals.append(pos)
                self.vis.renderer.draw_position_marker(
                    pos, "goal", index=len(self.vis.goals)
                )
                self.vis.update_path_stats()

    def set_start_position(self, pos) -> None:
        """
        Set the starting position for pathfinding.

        Creates a visual marker on the canvas and updates the information
        display. The start position is the origin for all path computations.

        Args:
            pos: Tuple (row, col) representing the start position
        """
        self.vis.start_pos = pos
        cell_value = self.vis.floorplan[pos[0], pos[1]]

        # Draw start marker on canvas
        self.vis.start_marker, self.vis.start_label = (
            self.vis.renderer.draw_position_marker(pos, "start")
        )

        # Update information panel
        self.vis.update_path_stats()
        logger.info(f"Start position set to {pos}, cell value: {cell_value}")

    def on_mode_change(self) -> None:
        """
        Handle mode switching between Search and Edit modes.

        This method manages the complex state transitions when changing modes:

        Search mode:
        - Shows algorithm selector, explored nodes checkbox
        - Shows Search and Clear buttons
        - Hides Save and Reset edits buttons
        - Clears edit mode markers and state

        Edit mode:
        - Hides algorithm selector and explored nodes checkbox
        - Shows Save and Reset edits buttons
        - Hides Search and Clear path buttons
        - Clears all path-related visualizations and markers
        - Displays edge walls for editing

        The method ensures clean transitions by clearing mode-specific
        state and updating the UI to show only relevant controls.
        """
        mode = self.vis.mode_var.get()
        self.vis.mode = mode

        # Hide all mode-specific buttons (will show appropriate ones below)
        self.vis.find_path_button.pack_forget()
        self.vis.clear_path_button.pack_forget()
        self.vis.save_edits_button.pack_forget()
        self.vis.clear_edits_button.pack_forget()
        self.vis.algorithm_frame.pack_forget()
        self.vis.show_explored_check.pack_forget()

        if mode == "path":
            # Switching to Search mode

            # Clear any edit mode markers
            self.vis.editor.clear_edit_marker()
            self.vis.editor.clear_adjacent_markers()
            self.vis.edit_first = None

            # Show search mode controls
            self.vis.algorithm_frame.pack(fill="x", padx=5, pady=(0, 5))
            self.vis.show_explored_check.pack(fill="x", padx=5, pady=(0, 5))
            self.vis.find_path_button.pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 3), pady=(5, 5)
            )
            self.vis.clear_path_button.pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 5), pady=(5, 5)
            )

            # Update information display
            self.vis.update_path_stats()

            logger.info("Switched to Path mode")
        else:
            # Switching to Edit mode

            # Stop any ongoing animation
            self.vis.animator.stop_animation()

            # Clear path visualization
            for item in self.vis.path_items:
                self.vis.canvas.delete(item)
            self.vis.path_items.clear()

            # Clear explored nodes visualization
            for item in self.vis.explored_items:
                self.vis.canvas.delete(item)
            self.vis.explored_items.clear()

            # Clear start marker and state
            if self.vis.start_marker:
                self.vis.canvas.delete(self.vis.start_marker)
                self.vis.start_marker = None
            if self.vis.start_label:
                self.vis.canvas.delete(self.vis.start_label)
                self.vis.start_label = None
            self.vis.start_pos = None

            # Clear all goal markers and state
            for marker_id, label_id in self.vis.goal_markers.values():
                if marker_id:
                    self.vis.canvas.delete(marker_id)
                if label_id:
                    self.vis.canvas.delete(label_id)
            self.vis.goal_markers.clear()
            self.vis.goals.clear()

            # Clear path and exploration data
            self.vis.current_path.clear()
            self.vis.explored_cells.clear()
            self.vis.visited_segment_goals.clear()

            # Show edit mode controls
            self.vis.save_edits_button.pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 3), pady=(5, 5)
            )
            self.vis.clear_edits_button.pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 5), pady=(5, 5)
            )

            # Display edge walls for editing
            self.vis.editor.redraw_edge_walls()

            # Update information display
            self.vis.update_path_stats()

            logger.info("Switched to Edit mode")

    def on_algorithm_change(self) -> None:
        """
        Handle algorithm selection changes between A* and Dijkstra.

        Updates the pathfinder's heuristic function:
        - A*: Uses Manhattan distance heuristic for faster, guided search
        - Dijkstra: Uses zero heuristic (uniform cost search) for exhaustive exploration

        When the algorithm changes, any existing path is cleared since it may
        have been computed with a different algorithm. This ensures the displayed
        path always matches the selected algorithm.
        """
        algorithm = self.vis.algorithm_var.get()
        logger.info(f"Algorithm changed to {algorithm}")

        # Update heuristic function based on selection
        if algorithm == "Dijkstra":
            # Dijkstra uses zero heuristic (uniform cost search)
            self.vis.pathfinder.heuristic = lambda p1, p2: 0.0
        else:
            # A* uses Manhattan distance heuristic
            self.vis.pathfinder.heuristic = self.vis.pathfinder.manhattan_distance

        # Clear existing path since it may have been computed differently
        self.vis.path_controller.clear_current_path()

        # Update information display
        self.vis.update_path_stats()

    def on_show_explored_change(self) -> None:
        """
        Handle toggling of explored nodes visualization.

        When enabled, shows small dots on all cells that were explored
        during pathfinding. When disabled, hides these visualizations.

        This helps users understand the search space and compare
        algorithm efficiency (A* vs Dijkstra exploration patterns).
        """
        show_explored = self.vis.show_explored_var.get()
        logger.info(f"Show explored nodes: {show_explored}")

        if show_explored and self.vis.explored_cells:
            # Show explored cells if data exists
            self.vis.renderer.draw_explored_cells(self.vis.explored_cells)
        else:
            # Hide explored cells
            for item in self.vis.explored_items:
                self.vis.canvas.delete(item)
            self.vis.explored_items.clear()

    def save_edits(self) -> None:
        """
        Save edge wall edits to persistent storage.

        Delegates to the editor's save method and shows appropriate
        feedback dialogs. Called when the user clicks the Save button
        in Edit mode.

        Shows success or error message based on save operation result.
        """
        try:
            self.vis.editor.save_edits()
            messagebox.showinfo("Success", "Edge walls saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save edge walls: {e}")

    def clear_edits(self) -> None:
        """
        Clear all unsaved edge wall edits and revert to last saved state.

        This operation:
        1. Clears edit mode selection markers
        2. Reloads edge walls from file (discarding changes)
        3. Updates the visual display
        4. Refreshes the information panel

        Called when the user clicks the Reset button in Edit mode,
        providing a way to undo changes without saving.
        """
        # Clear edit mode visual markers
        self.vis.editor.clear_edit_marker()
        self.vis.editor.clear_adjacent_markers()
        self.vis.edit_first = None

        # Revert to last saved state
        self.vis.editor.clear_all_edits()

        # Update information display
        self.vis.update_path_stats()
