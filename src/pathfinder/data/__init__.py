"""
Data module for the Pathfinder application.

This package manages all floor plan data, including:
- Floor plan grid definition
- Floor plan data loading and management

The data module provides:
- FLOORPLAN: The hospital floor plan as a 2D list
- FloorplanManager: Class for loading and managing floor plan data

Components:
- floorplan.py: Contains the floor plan definition
- manager.py: FloorplanManager class for data access and statistics

Exports:
- FLOORPLAN: The floor plan data structure
- FloorplanManager: Manager class for floor plan data
"""

from .floorplan import FLOORPLAN
from .manager import FloorplanManager

__all__ = [
    "FLOORPLAN",
    "FloorplanManager",
]
