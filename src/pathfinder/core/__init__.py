"""
Core module for pathfinding and search algorithms.

This module exports the main classes used for grid-based pathfinding:
- SearchAlgorithm: A* and Dijkstra pathfinding implementation
- Cell: Representation of a grid cell with cost metrics

Example:
    >>> from app.core import SearchAlgorithm
    >>> algo = SearchAlgorithm(floorplan)
    >>> path, nodes_explored, explored_cells = algo.search(start, goal)
"""

from .search import Cell, SearchAlgorithm

__all__ = ["SearchAlgorithm", "Cell"]
