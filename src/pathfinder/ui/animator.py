"""
Path Animator Module for Pathfinder Visualizer.

This module contains the PathAnimator class responsible for animating
pathfinding visualizations. It provides smooth, step-by-step animation
of path discovery across multiple goal segments, helping users understand
how the pathfinding algorithm progresses through the floorplan.

The animator handles:
- Segment-by-segment path animation for multi-goal paths
- Smooth frame-by-frame path drawing
- Visual coordination with start/goal markers
- Final path display with complete statistics
"""

import logging
import tkinter as tk

from ..config import GRID_CELL_SIZE

logger = logging.getLogger(__name__)


class PathAnimator:
    """
    Manages animated visualization of pathfinding algorithms.

    This class orchestrates the step-by-step animation of path segments,
    creating a visual representation of how the pathfinding algorithm
    discovers routes between the start position and multiple goals.

    Features:
    - Animates each path segment individually
    - Shows progressive path building for multi-goal scenarios
    - Handles marker visibility during animation
    - Coordinates timing between segments
    - Displays final complete path with statistics

    The animation process:
    1. Start animation with all segments
    2. Animate first segment step-by-step
    3. Pause briefly, then move to next segment
    4. Repeat until all segments complete
    5. Display final consolidated path

    Attributes:
        vis: Reference to the parent FloorplanVisualizer instance
    """

    def __init__(self, visualizer) -> None:
        """
        Initialize the PathAnimator with a reference to the visualizer.

        Args:
            visualizer: The parent FloorplanVisualizer instance
        """
        self.vis = visualizer

    def start_animation(
        self,
        segments,
        complete_path,
        total_explored,
        algorithm_name,
        goals_visited,
    ):
        """
        Begin animated visualization of the pathfinding result.

        This is the main entry point for path animation. It initializes
        the animation state and begins animating the first segment.

        Args:
            segments: List of path segments, one per goal visited
            complete_path: Complete path from start through all goals
            total_explored: Total number of nodes explored during pathfinding
            algorithm_name: Name of algorithm used ("A*" or "Dijkstra")
            goals_visited: Number of goals visited in the path
        """
        # Store animation data
        self.vis.animation_segments = segments
        self.vis.current_segment_index = 0
        self.vis.complete_path_for_final_display = complete_path
        self.vis.total_nodes_explored = total_explored
        self.vis.algorithm_name = algorithm_name
        self.vis.goals_visited = goals_visited
        self.vis.is_animating = True
        self.vis.visited_segment_goals = []

        # Begin animating the first segment
        self.animate_next_segment()

    def animate_next_segment(self) -> None:
        """
        Transition to animating the next path segment.

        Called after completing a segment or starting animation. If all
        segments are complete, transitions to displaying the final path.
        Otherwise, clears the canvas and begins animating the next segment.

        This method handles:
        - Checking if animation is complete
        - Clearing previous segment visualization
        - Updating goal marker visibility
        - Starting animation of next segment
        """
        # Check if all segments are complete
        if self.vis.current_segment_index >= len(self.vis.animation_segments):
            self.show_final_path()
            return

        # Get the next segment to animate
        segment = self.vis.animation_segments[self.vis.current_segment_index]

        # Clear previous path visualization
        for item in self.vis.path_items:
            self.vis.canvas.delete(item)
        self.vis.path_items.clear()

        # Clear explored node visualization
        for item in self.vis.explored_items:
            self.vis.canvas.delete(item)
        self.vis.explored_items.clear()

        # Hide goals that haven't been visited yet (creates reveal effect)
        for goal_pos in list(self.vis.goal_markers.keys()):
            if goal_pos not in self.vis.visited_segment_goals:
                marker_id, label_id = self.vis.goal_markers[goal_pos]
                if marker_id:
                    self.vis.canvas.delete(marker_id)
                if label_id:
                    self.vis.canvas.delete(label_id)

        # Redraw markers once at the start of the segment
        current_segment_goal = segment[-1] if segment else None
        goals_to_show = list(self.vis.visited_segment_goals)
        if current_segment_goal and current_segment_goal not in goals_to_show:
            goals_to_show.append(current_segment_goal)
        self.vis.renderer.redraw_markers_on_top(goals_to_show)

        # Begin step-by-step animation of this segment
        self.animate_segment(segment, 0)

    def animate_segment(self, segment, step) -> None:
        """
        Animate a single step of a path segment.

        This method is called recursively to create the animation effect,
        drawing only the NEW path elements at each step (incremental rendering).
        This approach maintains O(n) complexity instead of O(n²).

        Each call:
        1. Draws ONLY the new cell and connecting line
        2. Schedules next step after a delay
        3. Or transitions to next segment when complete

        The path is drawn with:
        - Background rectangles on path cells
        - White lines connecting consecutive cells
        - Smart clipping at start/goal markers to avoid overlap
        - Smooth rounded line caps and joins

        Args:
            segment: List of (row, col) positions forming the segment
            step: Current step index in the segment (0-indexed)
        """
        # Check if animation was cancelled
        if not self.vis.is_animating:
            return

        # Check if segment is complete
        if step >= len(segment):
            # Mark this segment's goal as visited
            segment_goal = segment[-1] if segment else None
            if segment_goal and segment_goal not in self.vis.visited_segment_goals:
                self.vis.visited_segment_goals.append(segment_goal)

            # Move to next segment after brief pause
            self.vis.current_segment_index += 1
            self.vis.root.after(500, self.animate_next_segment)
            return

        # Draw ONLY the new cell background (incremental approach)
        pos = segment[step]
        row, col = pos

        # Calculate cell boundaries with small inset
        x1 = col * GRID_CELL_SIZE + 1
        y1 = row * GRID_CELL_SIZE + 1
        x2 = x1 + GRID_CELL_SIZE - 2
        y2 = y1 + GRID_CELL_SIZE - 2

        # Create semi-transparent background using stipple pattern
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

        # Draw connecting line from previous cell to current cell (if not first cell)
        if step > 0:
            row1, col1 = segment[step - 1]
            row2, col2 = segment[step]

            # Calculate center points of both cells
            x1 = col1 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            y1 = row1 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            x2 = col2 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            y2 = row2 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2

            # Clip line at start marker to avoid overlap (only for first segment)
            if step == 1 and segment[step - 1] == self.vis.start_pos:
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
            if segment[step] in self.vis.goals:
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
                joinstyle=tk.ROUND,  # Rounded corners
            )
            self.vis.path_items.append(line)

        # Schedule next animation step after 50ms delay
        self.vis.root.after(50, lambda: self.animate_segment(segment, step + 1))

    def show_final_path(self) -> None:
        """
        Display the complete final path after animation completes.

        This method:
        1. Stops the animation flag
        2. Clears animated path elements
        3. Draws the complete consolidated path
        4. Shows all explored nodes (if enabled)
        5. Displays all goal markers
        6. Updates statistics panel with final results

        The final display provides a clear view of the complete path
        and allows users to analyze the pathfinding results.
        """
        # Mark animation as complete
        self.vis.is_animating = False

        # Clear animated path visualization
        for item in self.vis.path_items:
            self.vis.canvas.delete(item)
        self.vis.path_items.clear()

        # Draw complete path
        self.vis.renderer.draw_path(self.vis.complete_path_for_final_display)

        # Draw explored cells if visualization is enabled
        self.vis.renderer.draw_explored_cells(self.vis.explored_cells)

        # Ensure all markers are visible on top of path
        self.vis.renderer.redraw_markers_on_top(self.vis.goals)

        # Update information panel with final statistics
        self.vis.update_path_stats(
            self.vis.algorithm_name,
            len(self.vis.complete_path_for_final_display),
            self.vis.total_nodes_explored,
            self.vis.goals_visited,
        )

    def stop_animation(self) -> None:
        """
        Immediately stop any ongoing animation.

        Sets the animation flag to False, causing the animation loop
        to terminate on its next iteration. Called when:
        - User switches modes
        - User clears the path
        - User starts a new pathfinding operation

        The animation will stop gracefully without completing, and
        any scheduled animation callbacks will be cancelled by checking
        the is_animating flag.
        """
        self.vis.is_animating = False
