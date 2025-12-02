"""
A* and Dijkstra Search Algorithm Implementation for pathfinding

This module provides pathfinding capabilities on a floorplan grid using the A* algorithm
(with optional heuristic-free Dijkstra variant). It supports obstacle avoidance and
edge wall constraints.

Classes:
    Cell: Represents a grid cell with position and cost metrics (g, h, f).
    SearchAlgorithm: Implements A*/Dijkstra search for finding optimal paths on a floorplan.
"""

import logging
from itertools import count
from queue import PriorityQueue
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class Cell:
    """
    Represents a single cell in the search grid with pathfinding cost metrics.

    This class is used to store information about explored cells during the search process,
    including their position and the cost components (g, h, f) used in A* algorithm.

    Attributes:
        position (tuple): The (row, col) coordinates of the cell in the grid.
        g (float): The cost from the start node to this cell (actual path cost).
        h (float): The heuristic estimated cost from this cell to the goal (estimated remaining cost).
        f (float): The total estimated cost (f = g + h), used for prioritization in A*.
    """

    def __init__(self, position, g=0.0, h=0.0) -> None:
        """
        Initialize a Cell with position and cost metrics.

        Args:
            position (tuple): The (row, col) coordinates of the cell.
            g (float, optional): Cost from start to this cell. Defaults to 0.0.
            h (float, optional): Heuristic cost from this cell to goal. Defaults to 0.0.
        """
        self.position = position
        self.g = g
        self.h = h
        self.f = g + h


class SearchAlgorithm:
    """
    A* pathfinding algorithm implementation with support for grid-based navigation.

    This class implements the A* search algorithm (or Dijkstra when heuristic is zero-valued)
    to find optimal paths on a floorplan grid. It handles obstacles, edge walls, and provides
    pathfinding statistics.

    The algorithm explores cells based on their f-score (g + h), where:
    - g: actual cost from start to current cell
    - h: heuristic estimate from current cell to goal

    Attributes:
        floorplan (ndarray): 2D grid where 0 represents walkable space and 1 represents walls.
        rows (int): Number of rows in the floorplan.
        cols (int): Number of columns in the floorplan.
        edge_walls (set): Set of frozensets representing blocked edges between cells.
        heuristic (callable): Function that estimates distance between two positions.
        nodes_explored (int): Counter for total nodes explored during search.
        counter (itertools.count): Tiebreaker counter for maintaining FIFO order in priority queue.
        algo_name (str): Name of the algorithm being used ("A*" or "Dijkstra").
    """

    def __init__(
        self,
        floorplan,
        edge_walls=None,
        heuristic=None,
    ) -> None:
        """
        Initialize the SearchAlgorithm with a floorplan and optional parameters.

        Args:
            floorplan (ndarray): 2D grid array where 0=walkable space, 1=wall.
            edge_walls (set, optional): Set of frozensets representing blocked edges.
                Each frozenset contains two positions that cannot be traversed between.
                Defaults to empty set.
            heuristic (callable, optional): Function(pos1, pos2) -> float that estimates
                distance between two positions. If None, defaults to manhattan_distance.
                If it returns 0, algorithm operates as Dijkstra instead of A*.
        """
        self.floorplan = floorplan
        self.rows, self.cols = floorplan.shape
        self.edge_walls = edge_walls or set()
        self.heuristic = heuristic if heuristic is not None else self.manhattan_distance
        self.nodes_explored = 0
        self.counter = count()  # Use itertools.count() for efficient counter

        # Detect algorithm type based on heuristic behavior
        algo_name = (
            "Dijkstra"
            if heuristic is not None and heuristic((0, 0), (1, 1)) == 0
            else "A*"
        )
        self.algo_name = algo_name
        logger.info(f"{algo_name} search initialized: {self.rows}x{self.cols} grid")

    def search(
        self, start, goal
    ) -> Tuple[Optional[List[Tuple[int, int]]], int, List[Cell]]:
        """
        Find a path from start to goal position on the floorplan.

        This is the main entry point for the search algorithm. It validates input positions,
        performs the A*/Dijkstra search, and returns the path along with search statistics.

        Args:
            start (tuple): The (row, col) starting position.
            goal (tuple): The (row, col) goal position.

        Returns:
            tuple: A 3-tuple containing:
                - Optional[List[Tuple[int, int]]]: The path from start to goal (None if no path exists).
                - int: Total number of nodes explored during search.
                - List[Cell]: List of Cell objects representing explored cells with their costs.
        """
        if not self.validate_position(start, "start"):
            return (None, 0, [])
        if not self.validate_position(goal, "goal"):
            return (None, 0, [])

        logger.info(f"Searching: {start} → {goal}")

        self.nodes_explored = 0
        self.counter = count()  # Reset counter for new search

        path, nodes, explored_cells = self.searches(start, goal)

        if path:
            logger.info(
                f"Path found: {len(path)} steps, {self.nodes_explored} nodes explored"
            )
        else:
            logger.warning(f"No path found after exploring {self.nodes_explored} nodes")

        return (path, self.nodes_explored, explored_cells)

    def searches(
        self, start, goal
    ) -> Tuple[Optional[List[Tuple[int, int]]], int, List[Cell]]:
        """
        Core A* search / Dijkstra's algorithm implementation.

        Uses a priority queue to explore cells with lowest f-score first. Maintains open and
        closed sets to avoid reprocessing cells. Returns path reconstruction on goal found.

        Args:
            start (tuple): The (row, col) starting position.
            goal (tuple): The (row, col) goal position.

        Returns:
            tuple: A 3-tuple containing:
                - Optional[List[Tuple[int, int]]]: Path from start to goal (None if unreachable).
                - int: Number of nodes explored in this search.
                - List[Cell]: List of all explored cells with their cost metrics.
        """
        # Handle trivial case where start equals goal
        if start == goal:
            return ([start], 0, [])

        # Initialize priority queue and tracking sets
        open_queue = PriorityQueue()
        open_queue.put((0.0, next(self.counter), start))

        open_set = {start}
        g_score = {start: 0.0}  # Actual cost from start to each node
        came_from = {}  # Parent pointer for path reconstruction
        closed_set = set()  # Already evaluated nodes
        explored_cells = []  # Track all explored cells for visualization
        nodes = 0

        while not open_queue.empty():
            current_f, _, current = open_queue.get()
            open_set.discard(current)

            # Skip if already processed (can happen with duplicate queue entries)
            if current in closed_set:
                continue

            closed_set.add(current)
            nodes += 1
            self.nodes_explored += 1

            # Record cell exploration data
            current_g = g_score[current]
            current_h = self.heuristic(current, goal)
            explored_cells.append(Cell(current, current_g, current_h))

            # Goal found - reconstruct and return path
            if current == goal:
                path = self.reconstruct_path(came_from, current, start)
                return (path, nodes, explored_cells)

            # Evaluate all neighbors of current node
            current_g = g_score[current]

            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue

                # Calculate tentative cost to neighbor
                tentative_g = current_g + 1.0

                # Update neighbor if this path is better
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    h = self.heuristic(neighbor, goal)
                    f = tentative_g + h

                    # Add to open set if not already there
                    if neighbor not in open_set:
                        open_queue.put((f, next(self.counter), neighbor))
                        open_set.add(neighbor)

        # No path found after exhausting all reachable nodes
        return (None, nodes, explored_cells)

    def get_neighbors(self, position) -> List[Tuple[int, int]]:
        """
        Get all valid neighboring cells (up, down, left, right) from a position.

        Checks for obstacles (walls), grid boundaries, and edge wall constraints.

        Args:
            position (tuple): The (row, col) position to get neighbors for.

        Returns:
            List[Tuple[int, int]]: List of valid neighboring positions.
        """
        neighbors = []
        row, col = position

        # Check all four cardinal directions
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (row + dr, col + dc)
            if self.is_valid_move(position, new_pos):
                neighbors.append(new_pos)

        return neighbors

    def is_valid_move(self, from_pos, to_pos) -> bool:
        """
        Check if movement from one position to another is valid.

        Validates destination is within bounds, not a wall, and not blocked by edge walls.

        Args:
            from_pos (tuple): The (row, col) current position.
            to_pos (tuple): The (row, col) destination position.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        if not self.is_valid_neighbor(to_pos):
            return False

        # Check if edge between positions is blocked
        if frozenset((from_pos, to_pos)) in self.edge_walls:
            return False

        return True

    def is_valid_neighbor(self, position) -> bool:
        """
        Check if a position is a valid neighbor (walkable space within bounds).

        Args:
            position (tuple): The (row, col) position to validate.

        Returns:
            bool: True if position is walkable and within grid bounds, False otherwise.
        """
        row, col = position

        # Check bounds
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False

        # Check if position is a wall (cell value 1 = wall, 0 = walkable)
        # Direct integer comparison is faster than string conversion
        if self.floorplan[row, col] == 1:
            return False

        return True

    def reconstruct_path(self, came_from, current, start) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from start to goal using parent pointers.

        Follows the came_from dictionary backwards from goal to start, then reverses
        to return the path in correct order.

        Args:
            came_from (dict): Dictionary mapping each position to its parent position.
            current (tuple): The goal position (starting point for reconstruction).
            start (tuple): The start position (ending point for reconstruction).

        Returns:
            List[Tuple[int, int]]: The complete path from start to goal.
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def manhattan_distance(self, pos1, pos2) -> float:
        """
        Calculate Manhattan distance (taxicab distance) between two positions.

        Used as the default heuristic for A* search. Manhattan distance is admissible
        for grid-based movement with 4-directional (cardinal) moves.

        Args:
            pos1 (tuple): The first (row, col) position.
            pos2 (tuple): The second (row, col) position.

        Returns:
            float: The Manhattan distance between the two positions.
        """
        return float(abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))

    def validate_position(self, position, label) -> bool:
        """
        Validate that a position is valid for pathfinding (within bounds and not a wall).

        Logs appropriate error messages if validation fails.

        Args:
            position (tuple): The (row, col) position to validate.
            label (str): A descriptive label for the position (e.g., "start", "goal")
                used in error logging.

        Returns:
            bool: True if position is valid, False otherwise.
        """
        row, col = position

        # Check bounds
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            logger.error(f"Invalid {label} position (out of bounds): {position}")
            return False

        # Check if position is a wall (direct integer comparison)
        if self.floorplan[row, col] == 1:
            logger.error(f"Invalid {label} position (wall): {position}")
            return False

        return True
