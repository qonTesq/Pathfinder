"""
Information Updater Module for Pathfinder Visualizer.

This module contains the InformationUpdater class responsible for updating
the information panel that shows statistics, instructions, and current
state information to the user. The display adapts based on:
- Current mode (Search vs Edit)
- Selected positions (start, goals)
- Pathfinding results (algorithm, path length, nodes explored)
- Edit mode state

The information panel provides contextual feedback and guidance to help
users understand the current state and available actions.
"""

import logging
import tkinter as tk

logger = logging.getLogger(__name__)


class InformationUpdater:
    """
    Manages the information display panel for the visualizer.

    This class handles all updates to the text display that shows:
    - Current start and goal positions
    - Path statistics (length, nodes explored, algorithm used)
    - Edit mode instructions and state
    - Contextual help messages

    The display dynamically updates based on mode and application state,
    providing users with relevant information and guidance.

    Attributes:
        vis: Reference to the parent FloorplanVisualizer instance
    """

    def __init__(self, visualizer) -> None:
        """
        Initialize the InformationUpdater with a reference to the visualizer.

        Args:
            visualizer: The parent FloorplanVisualizer instance
        """
        self.vis = visualizer

    def update_path_stats(
        self,
        algorithm=None,
        path_length=None,
        nodes_explored=None,
        goals_visited=None,
    ) -> None:
        """
        Update the information panel with current statistics and state.

        This is the main method for refreshing the information display.
        It clears the current content and regenerates it based on the
        current mode and available data.

        The display shows different information depending on:
        - Mode: Search mode shows positions and pathfinding stats,
                Edit mode shows editing instructions
        - State: Prompts user for next action or displays results

        Args:
            algorithm: Name of pathfinding algorithm used ("A*" or "Dijkstra")
            path_length: Number of steps in the computed path
            nodes_explored: Number of nodes explored during search
            goals_visited: Number of goals visited in multi-goal path
        """
        # Enable text widget for editing
        self.vis.path_stats_text.config(state=tk.NORMAL)

        # Clear existing content
        self.vis.path_stats_text.delete("1.0", tk.END)

        # Display mode-appropriate information
        if self.vis.mode == "edit":
            self.display_edit_mode_info()
        else:
            self.display_path_mode_info(
                algorithm, path_length, nodes_explored, goals_visited
            )

        # Disable text widget to make it read-only
        self.vis.path_stats_text.config(state=tk.DISABLED)

    def display_edit_mode_info(self) -> None:
        """
        Display information and instructions for Edit mode.

        Shows contextual help based on the current edit state:
        - No cell selected: General instructions for adding edge walls
        - Cell selected: Shows selected cell and prompts for adjacent selection

        Edit mode allows users to toggle walls between adjacent cells
        by clicking two cells in sequence.
        """
        if self.vis.edit_first is None:
            # No cell selected yet - show general instructions
            text = (
                "Click a non-wall cell, then an adjacent cell to toggle a wall between them.\n\n"
                "Click 'Save' to persist or 'Reset' to revert."
            )
        else:
            # Cell selected - show selected position and next step
            text = f"First cell: {self.vis.edit_first}\n\nSelect an adjacent cell..."

        self.vis.path_stats_text.insert(tk.END, text)

    def display_path_mode_info(
        self,
        algorithm,
        path_length,
        nodes_explored,
        goals_visited,
    ) -> None:
        """
        Display information for Search mode including positions and results.

        Shows different information based on current state:
        1. No start: Prompt to set start position
        2. Start set: Show start, prompt for goals
        3. Goals set: Show start and goals, ready for search
        4. Path computed: Show full statistics including algorithm results

        The display guides users through the pathfinding workflow while
        providing detailed results after computation.

        Args:
            algorithm: Name of pathfinding algorithm used ("A*" or "Dijkstra")
            path_length: Number of steps in the computed path
            nodes_explored: Number of nodes explored during search
            goals_visited: Number of goals visited in multi-goal path
        """
        # Display start position or prompt
        if self.vis.start_pos:
            self.vis.path_stats_text.insert(tk.END, f"Start: {self.vis.start_pos}\n")
        else:
            self.vis.path_stats_text.insert(
                tk.END, "Click on grid to set start position\n"
            )

        # Display goals or prompt
        if self.vis.goals:
            # Format goals as comma-separated list
            goals_str = ", ".join([str(g) for g in self.vis.goals])
            self.vis.path_stats_text.insert(
                tk.END, f"Goals ({len(self.vis.goals)}): {goals_str}\n"
            )
        else:
            # Only show goal prompt after start is set
            if self.vis.start_pos:
                self.vis.path_stats_text.insert(
                    tk.END, "Click to add goals (up to 15)\n"
                )

        # Display pathfinding results if available
        if algorithm and path_length is not None:
            # Add separator line
            self.vis.path_stats_text.insert(tk.END, f"\nAlgorithm: {algorithm}\n")

            # Show number of goals visited if multiple goals
            if goals_visited is not None and goals_visited > 1:
                self.vis.path_stats_text.insert(
                    tk.END, f"Goals Visited: {goals_visited}\n"
                )

            # Show path length (number of steps)
            self.vis.path_stats_text.insert(tk.END, f"Path Length: {path_length}\n")

            # Show nodes explored (algorithm efficiency metric)
            self.vis.path_stats_text.insert(
                tk.END, f"Nodes Explored: {nodes_explored}\n"
            )

            # Prints SUCCESS after displaying stats; this will only be displayed if successful
            self.vis.path_stats_text.insert(tk.END, "\nSUCCESS\n")
