"""
Path Controller Module for Pathfinder Visualizer.

This module contains the PathController class responsible for managing
pathfinding operations. It handles:
- Multi-goal path computation with priority-based ordering
- Path validation and verification
- Integration with pathfinding algorithms (A*, Dijkstra)
- Path visualization coordination

The controller implements intelligent goal prioritization based on hospital
ward urgency levels, ensuring critical wards are visited first.
"""

import logging
from queue import PriorityQueue
from tkinter import messagebox

from ..config import WARDS

logger = logging.getLogger(__name__)


class PathController:
    """
    Manages pathfinding operations and multi-goal path computation.

    This class serves as the main controller for pathfinding functionality,
    coordinating between the UI, pathfinding algorithms, and visualization
    components. It handles:
    - Single and multi-goal path computation
    - Ward priority-based goal ordering
    - Path segment management
    - Path clearing and validation
    - Statistics tracking (nodes explored, path length)

    The controller supports visiting multiple goals in priority order,
    where goals in more critical hospital wards are visited first.

    Attributes:
        vis: Reference to the parent FloorplanVisualizer instance
    """

    def __init__(self, visualizer) -> None:
        """
        Initialize the PathController with a reference to the visualizer.

        Args:
            visualizer: The parent FloorplanVisualizer instance
        """
        self.vis = visualizer

    def find_and_draw_path(self) -> None:
        """
        Find and visualize the optimal path from start to all goal positions.

        This method implements multi-goal pathfinding with priority ordering:
        1. Validates that start and goals are set
        2. Orders goals by ward priority (critical wards first)
        3. Computes path segments between consecutive waypoints
        4. Aggregates segments into complete path
        5. Initiates animated visualization

        The path is computed incrementally, where each segment goes from
        the current position to the next highest-priority goal. Segments
        are stitched together to form the complete path.

        Shows error dialogs if:
        - No start position or goals are set
        - No valid path exists between any waypoints
        """
        # Validate that required positions are set
        if self.vis.start_pos is None or not self.vis.goals:
            messagebox.showwarning(
                "Missing Positions", "Set a start and at least one goal."
            )
            return

        # Clear any existing path visualization
        self.clear_current_path()

        algorithm_name = self.vis.algorithm_var.get()
        logger.info(
            f"Using {algorithm_name} algorithm with {len(self.vis.goals)} goal(s)"
        )

        # Order goals by priority (most urgent wards first)
        prioritized_goals = self.prioritize_goals()

        # Initialize tracking variables for path computation
        complete_path = []  # Full path across all segments
        path_segments = []  # Individual segments for animation
        total_nodes_explored = 0  # Cumulative exploration count
        all_explored_cells = []  # All cells explored across segments
        current_pos = self.vis.start_pos  # Current position (waypoint)
        visited_goals = []  # Goals visited in order
        failed_goals = []  # Goals that couldn't be reached

        # Compute path segment to each goal in priority order
        for priority, goal_index, goal_pos in prioritized_goals:
            logger.info(f"Computing path to goal {goal_pos} (priority {-priority})")

            # Run pathfinding algorithm from current position to goal
            path_segment, nodes_explored, explored_cells = self.vis.pathfinder.search(
                current_pos, goal_pos
            )

            # Checks for the starting position not being valid
            if path_segment is None and current_pos == self.vis.start_pos:
                logger.warning(
                    f"Staring position is not valid {current_pos}. Skipping this start to next goal {goal_pos}."
                )
                failed_goals.append(current_pos)
                current_pos = goal_pos
                continue
            # Checks if the path was not valid
            elif path_segment is None:
                logger.warning(
                    f"No path found to goal at {goal_pos}. Skipping this goal."
                )
                failed_goals.append(goal_pos)
                continue

            # Store segment for animation
            path_segments.append(path_segment)

            # Add segment to complete path (skip first position to avoid duplicates)
            if complete_path:
                complete_path.extend(path_segment[1:])
            else:
                complete_path.extend(path_segment)

            # Accumulate statistics
            total_nodes_explored += nodes_explored
            all_explored_cells.extend(explored_cells)

            # Update current position for next segment
            current_pos = goal_pos
            visited_goals.append(goal_pos)

        # If valid path found, visualize it
        if complete_path:
            self.vis.current_path = complete_path
            self.vis.explored_cells = all_explored_cells

            # Start animated visualization
            self.vis.animator.start_animation(
                path_segments,
                complete_path,
                total_nodes_explored,
                algorithm_name,
                len(visited_goals),
            )

            logger.info(
                "Multi-goal path found with %d steps, %d nodes explored",
                len(complete_path),
                total_nodes_explored,
            )

        if failed_goals and visited_goals:
            # Show warning if some goals couldn't be reached
            failed_goals_str = ", ".join([str(pos) for pos in failed_goals])
            messagebox.showwarning(
                "PARTIAL FAILURE",
                f"Could not find path to: {failed_goals_str}",
            )
            logger.warning(
                f"Partial failure: {len(failed_goals)} unreachable goal(s), {len(visited_goals)} reached."
            )
        elif not visited_goals:
            # Only show error if no goals were reached at all
            messagebox.showerror(
                "FAILURE", "Could not find a path to any of the goals."
            )
            logger.error("Failure: No valid path found to any goal.")

    def prioritize_goals(self) -> list:
        """
        Order goals by ward priority to visit critical areas first.

        Goals are prioritized based on the urgency level of the hospital
        ward they are located in. Higher priority wards (e.g., emergency,
        ICU) are visited before lower priority wards.

        Priority values are negated before adding to the queue so that
        Python's PriorityQueue (min-heap) returns highest priority first.

        Optimized to avoid repeated string conversions and dictionary lookups.

        Returns:
            list: List of tuples (negative_priority, original_index, goal_position)
                  sorted by priority descending (most urgent first)
        """
        priority_queue = PriorityQueue()

        for index, goal_pos in enumerate(self.vis.goals):
            row, col = goal_pos
            # Direct integer access - no string conversion needed
            cell_value = self.vis.floorplan[row, col]

            # Determine priority based on cell value
            if cell_value == 0:
                # Corridor: neutral priority
                priority = 0
            elif cell_value == 1:
                # Wall: should never happen, but handle gracefully
                priority = 0
            else:
                # Ward cell: use ward's defined priority
                # Convert to string only for dictionary lookup
                cell_str = str(cell_value)
                ward = WARDS.get(cell_str)
                priority = ward.priority if ward else 0

            # Add to queue with negated priority [higher priority = lower number (in this case, more urgent is the smallest number)]
            priority_queue.put((-1 * priority, index, goal_pos))

            logger.info(
                f"Goal {goal_pos} in ward/cell '{cell_value}' has priority {priority}"
            )

        # Extract all goals from queue into sorted list
        prioritized_goals = []
        while not priority_queue.empty():
            prioritized_goals.append(priority_queue.get())

        return prioritized_goals

    def clear_current_path(self) -> None:
        """
        Clear the current path visualization without removing markers.

        This removes:
        - Path lines and background rectangles
        - Explored node visualizations
        - Animation state

        Start and goal markers remain visible so the user can compute
        a new path with the same positions.
        """
        # Stop any ongoing animation
        self.vis.animator.stop_animation()

        # Delete path visual elements
        for item in self.vis.path_items:
            self.vis.canvas.delete(item)
        self.vis.path_items.clear()

        # Delete explored node visualizations
        for item in self.vis.explored_items:
            self.vis.canvas.delete(item)
        self.vis.explored_items.clear()

        # Reset animation state
        self.vis.animation_segments = []
        self.vis.current_segment_index = 0
        self.vis.complete_path_for_final_display = []
        self.vis.visited_segment_goals = []

    def clear_path(self) -> None:
        """
        Completely clear all path-related elements including markers.

        This removes:
        - Current path visualization (via clear_current_path)
        - Start position marker and state
        - All goal position markers and state
        - Path and exploration data

        Called when the user wants to start fresh with new positions.
        """
        # Clear path visualization
        self.clear_current_path()

        # Remove start marker
        if self.vis.start_marker:
            self.vis.canvas.delete(self.vis.start_marker)
            self.vis.start_marker = None
        if self.vis.start_label:
            self.vis.canvas.delete(self.vis.start_label)
            self.vis.start_label = None
        self.vis.start_pos = None

        # Remove all goal markers
        for marker_id, label_id in self.vis.goal_markers.values():
            if marker_id:
                self.vis.canvas.delete(marker_id)
            if label_id:
                self.vis.canvas.delete(label_id)
        self.vis.goal_markers.clear()
        self.vis.goals.clear()

        # Clear path data
        self.vis.current_path.clear()
        self.vis.explored_cells.clear()

        # Update information display
        self.vis.update_path_stats()

        logger.info("Path cleared")

    def validate_path(self, path) -> None:
        """
        Validate a computed path for correctness and integrity.

        This debugging method checks:
        - Path starts at the designated start position
        - Path ends at a goal position
        - All cells are within grid bounds
        - Path doesn't traverse wall cells
        - All moves are to adjacent cells (no diagonal or jumps)

        Validation results are logged. This method is primarily for
        debugging and quality assurance.

        Args:
            path: List of (row, col) tuples representing the path
        """
        if not path:
            logger.warning("Path validation: empty path")
            return

        logger.info(f"Validating path with {len(path)} steps")

        # Check start position
        if path[0] != self.vis.start_pos:
            logger.warning(
                f"Path does not start at start position {self.vis.start_pos}"
            )

        # Check end position
        if path[-1] not in self.vis.goals:
            logger.warning("Path does not end at a goal position")

        invalid_cells = 0

        # Validate each step in the path
        for i in range(len(path)):
            row, col = path[i]

            # Check bounds
            if not (0 <= row < self.vis.rows and 0 <= col < self.vis.cols):
                logger.error(f"Step {i}: Position {(row, col)} is out of bounds")
                invalid_cells += 1
                continue

            # Check for walls
            cell_value = str(self.vis.floorplan[row, col])
            if cell_value == "1":
                logger.error(f"Step {i}: Path goes through wall at {(row, col)}")
                invalid_cells += 1

            # Check adjacency with next cell
            if i < len(path) - 1:
                next_row, next_col = path[i + 1]
                row_diff = abs(next_row - row)
                col_diff = abs(next_col - col)

                # Valid moves have Manhattan distance of 1
                if row_diff + col_diff != 1:
                    logger.error(
                        f"Step {i}: Non-adjacent move from {(row, col)} to {(next_row, next_col)}"
                    )
                    invalid_cells += 1

        # Report validation results
        if invalid_cells > 0:
            logger.error(f"Path validation found {invalid_cells} invalid cells")
        else:
            logger.info("✓ Path validation successful")
