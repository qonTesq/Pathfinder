"""
Application configuration and constants.

This module defines all application-level settings, UI color schemes, grid dimensions,
and ward (department) information. These constants are used throughout the application
for consistent styling, behavior, and data management.

Constants:
    APP_TITLE (str): The title displayed in the application window.
    DARK_MODE (bool): Auto-detected dark mode preference based on system settings.
    LOG_LEVEL (str): Logging verbosity level.
    GRID_WIDTH (int): Number of columns in the pathfinding grid.
    GRID_HEIGHT (int): Number of rows in the pathfinding grid.
    GRID_CELL_SIZE (int): Pixel size of each grid cell in the UI.

Classes:
    UIColours: Enumeration of all UI color constants used in the interface.
    Ward: Data class representing a hospital ward with metadata.

Module-level Dictionaries:
    WARDS: Complete ward information mapping ward codes to Ward objects.
"""

from dataclasses import dataclass
from enum import Enum

import darkdetect

# ============================================================================
# APPLICATION METADATA
# ============================================================================

APP_TITLE = "Pathfinder"
"""str: The title displayed in the application window."""

DARK_MODE = darkdetect.isDark()
"""bool: Auto-detects whether the system is in dark mode (Windows/macOS/Linux)."""

LOG_LEVEL = "INFO"
"""str: Controls logging verbosity. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL."""

# ============================================================================
# GRID DIMENSIONS AND LAYOUT
# ============================================================================

GRID_WIDTH = 40
"""int: Number of columns in the pathfinding grid. Represents the x-axis size."""

GRID_HEIGHT = 40
"""int: Number of rows in the pathfinding grid. Represents the y-axis size."""

GRID_CELL_SIZE = 18
"""int: Pixel size of each grid cell when rendered in the UI. Used for scaling."""


# ============================================================================
# USER INTERFACE COLOR SCHEME
# ============================================================================


class UIColours(Enum):
    """
    Enumeration of all colors used in the user interface.

    This enum provides a centralized location for all color constants, making it easy
    to update the theme globally. Colors are selected based on whether dark mode is enabled.

    Attributes:
        WALL (str): Color for wall/obstacle cells. Uses black for contrast.
        CORRIDOR (str): Color for corridor cells. Light grey for visibility.
        UNKNOWN (str): Color for unexplored or unknown cells.
        BOUNDARY (str): Color for grid boundary lines.
        EXPLORED (str): Color for cells explored during pathfinding search.
        EDGE_WALL (str): Color for blocked edges between cells.
        EDIT_SELECTION (str): Color for selected cell during editing mode (orange).
        EDIT_ADJACENT (str): Color for adjacent cells to selection (blue).
    """

    # Basic cell types
    WALL = "black"
    CORRIDOR = "lightgrey"

    # Status and visualization
    UNKNOWN = "#CCCCCC"

    BOUNDARY = "#2C3E50"

    EXPLORED = "#4A4A4A"

    # Editing mode colors
    EDGE_WALL = "#2C3E50"
    EDIT_SELECTION = "#FF9800"
    EDIT_ADJACENT = "#2196F3"


# ============================================================================
# WARD (DEPARTMENT) INFORMATION
# ============================================================================


@dataclass
class Ward:
    """
    Represents a hospital ward (department) with metadata.

    A Ward is a logical grouping representing a hospital department (e.g., Emergency,
    ICU, Maternity). Each ward has a unique code, associated color, description,
    and priority level for pathfinding considerations.

    Attributes:
        code (str): Two-letter unique identifier for the ward (e.g., "EM" for Emergency).
        colour (str): Hex color code or named color for UI representation.
        description (str): Human-readable full name of the ward.
        priority (int): Numerical priority level (1-5). Higher numbers indicate
                       higher priority destinations for routing algorithms.
                       1 = Low priority, 5 = Critical/High priority.

    Example:
        >>> emergency_ward = Ward("EM", "#F1D561", "Emergency", 5)
        >>> print(emergency_ward.code)  # "EM"
        >>> print(emergency_ward.priority)  # 5
    """

    code: str
    """Two-letter ward code identifier (e.g., "EM", "IC", "GW")."""

    colour: str
    """Hex color code or named color for visual identification in the UI."""

    description: str
    """Full human-readable name of the ward/department."""

    priority: int
    """Priority level (1-5) where 5 is highest priority (critical/emergency)."""


WARDS = {
    "AD": Ward("AD", "#A1A0A0", "Admissions", 1),
    "GW": Ward("GW", "#E74C3C", "General Ward", 2),
    "EM": Ward("EM", "#F1D561", "Emergency", 5),
    "MT": Ward("MT", "#85C1E9", "Maternity", 4),
    "SU": Ward("SU", "#CF799A", "Surgical", 4),
    "ON": Ward("ON", "#49A577", "Oncology", 5),
    "IC": Ward("IC", "#F5B041", "ICU", 5),
    "IW": Ward("IW", "#759AB8", "Isolation", 1),
    "PD": Ward("PD", "#B9DD8A", "Pediatric", 3),
    "BU": Ward("BU", "#8F497E", "Burn", 5),
    "HE": Ward("HE", "#EB984E", "Hematology", 3),
    "MD": Ward("MD", "#B7D34B", "Medical", 2),
}
"""
Dictionary of all hospital wards, keyed by their two-letter code.

This comprehensive mapping provides all ward information in one place for easy lookup
and iteration. Keys are 2-letter ward codes, values are Ward dataclass instances.

Ward Priority Legend:
    1 = Low priority (Admissions, Isolation)
    2 = Standard priority (General Ward, Medical)
    3 = Medium-high priority (Pediatric, Hematology)
    4 = High priority (Maternity, Surgical)
    5 = Critical/Highest priority (Emergency, Oncology, ICU, Burn)
"""
