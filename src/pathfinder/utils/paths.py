"""
Path utilities for resource management in development and bundled environments.

This module provides utilities for handling file paths in a way that works
correctly in both development environments and PyInstaller-bundled executables.

When an application is bundled with PyInstaller, files are extracted to a
temporary directory. This module abstracts away the complexity of finding
resources in both scenarios.

Functions:
    get_resource_path: Get absolute path to a resource file (read-only in bundles)
    get_writable_path: Get absolute path for writing files (works in bundles)
    initialize_user_data: Copy default data files to writable location on first run
"""

import shutil
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for development and PyInstaller bundles.

    This function provides a unified way to access resource files (like JSON data,
    images, config files, etc.) that works in both scenarios:

    1. **Development mode**: Running with `uv run app` or `python -m app`
       - Resources are accessed from their original locations in src/

    2. **PyInstaller bundle**: Running the compiled .exe
       - Resources are extracted to a temporary folder (_MEIPASS)
       - This function automatically finds them there

    The function checks for the presence of `sys._MEIPASS`, which PyInstaller
    sets to the temporary extraction directory. If not found, it assumes we're
    in development mode and calculates the path relative to the project root.

    Args:
        relative_path: Path relative to the project root directory.
                      Example: "src/app/data/edge_walls.json"

    Returns:
        Path: Absolute path to the resource file that works in both
              development and bundled contexts.

    Examples:
        >>> # Get path to data file
        >>> edge_walls = get_resource_path("src/app/data/edge_walls.json")
        >>> print(edge_walls)
        Path('C:/Users/.../src/app/data/edge_walls.json')  # In development

        >>> # Or when bundled:
        >>> print(edge_walls)
        Path('C:/Users/.../Temp/_MEI123/src/app/data/edge_walls.json')  # In exe

        >>> # Use with FloorplanManager
        >>> from app.data import FloorplanManager
        >>> data_path = get_resource_path("src/app/data/edge_walls.json")
        >>> manager = FloorplanManager(floorplan_data, edge_walls_path=data_path)

    Notes:
        - The relative_path should always use forward slashes (/)
        - The function converts to the appropriate path separator for the OS
        - Always test both development and bundled modes before release
        - When using PyInstaller, ensure files are included with --add-data

    See Also:
        - PyInstaller documentation on handling data files
        - README_BUILD.md for build instructions and --add-data usage
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # This attribute only exists when running as a bundled executable
        base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    except AttributeError:
        # Running in normal Python environment (development mode)
        # Calculate base path as project root (3 levels up from this file)
        # utils/paths.py -> utils -> app -> src -> project_root
        base_path = Path(__file__).parent.parent.parent.parent

    # Combine base path with relative path and return
    return base_path / relative_path


def get_writable_path(relative_path: str) -> Path:
    """
    Get absolute path for writing files, works in development and PyInstaller bundles.

    This function returns a writable location for user data files:

    1. **Development mode**: Writes to project directory (src/app/data/)
    2. **PyInstaller bundle**: Writes to same directory as the .exe

    This approach keeps user data next to the executable, making it easy to:
    - Find and back up the data file
    - Move the app by copying the entire folder
    - Delete all app data by removing the folder

    Args:
        relative_path: Filename for the writable file.
                      Example: "edge_walls.json"

    Returns:
        Path: Absolute path to a writable location.

    Examples:
        >>> # Get writable path for edge walls
        >>> edge_walls = get_writable_path("edge_walls.json")
        >>> print(edge_walls)
        Path('C:/Users/.../src/pathfinder/data/edge_walls.json')  # In development

        >>> # Or when bundled:
        >>> print(edge_walls)
        Path('C:/Users/.../PATHFINDER/edge_walls.json')  # Next to .exe

        >>> # Use with FloorplanManager
        >>> from pathfinder.data import FloorplanManager
        >>> data_path = get_writable_path("edge_walls.json")
        >>> manager = FloorplanManager(floorplan_data, edge_walls_path=data_path)

    Notes:
        - In bundled mode, the file is created in the same directory as the .exe
        - Ensures parent directories exist before returning the path
        - User must have write permissions to the directory (may fail in Program Files)
        - Consider running from a user-writable location like Desktop or Documents

    See Also:
        - get_resource_path for read-only bundled resources
    """
    try:
        # Running as PyInstaller bundle - use directory where .exe is located
        # This check detects if we're in a bundled executable
        _ = sys._MEIPASS  # type: ignore[attr-defined]

        # Get the directory containing the executable
        # sys.executable points to the .exe file when bundled
        base_path = Path(sys.executable).parent

    except AttributeError:
        # Running in development mode - use project data directory
        # Calculate base path as project root (4 levels up from this file)
        base_path = Path(__file__).parent.parent.parent.parent / "src" / "pathfinder" / "data"

        # Ensure directory exists in development
        base_path.mkdir(parents=True, exist_ok=True)

    # Combine base path with relative path and return
    return base_path / relative_path


def initialize_user_data(default_file_path: str, writable_filename: str) -> Path:
    """
    Initialize user data by copying default file to writable location if needed.

    This function ensures that bundled default/initial data files are copied
    to the application directory on first run. Subsequent runs will use the
    user's modified version without overwriting it.

    Typical workflow:
    1. Application bundles a default edge_walls.json with PyInstaller
    2. On first run, this function copies it next to the .exe
    3. Application loads from the .exe directory
    4. User edits are saved next to the .exe
    5. User can easily find, back up, or reset the file

    Args:
        default_file_path: Path to the bundled default file (relative to project root)
                          Example: "src/app/data/edge_walls.json"
        writable_filename: Filename to use in the writable location
                          Example: "edge_walls.json"

    Returns:
        Path: Absolute path to the writable file (either existing or newly copied)

    Examples:
        >>> # Initialize edge walls data
        >>> edge_walls_path = initialize_user_data(
        ...     "src/pathfinder/data/edge_walls.json",
        ...     "edge_walls.json"
        ... )
        >>> # Use the returned path with FloorplanManager
        >>> manager = FloorplanManager(floorplan_data, edge_walls_path=edge_walls_path)

    Notes:
        - Only copies if the writable file doesn't already exist
        - Preserves user edits across application restarts
        - In development: copies to src/pathfinder/data/ directory
        - In bundled mode: copies to same directory as .exe
        - User can delete the file to reset to defaults (will be re-copied on next run)
        - Falls back to empty initialization if default file is missing
    """
    # Get the writable location for the user data
    writable_path = get_writable_path(writable_filename)

    # If file already exists in writable location, use it (don't overwrite user data)
    if writable_path.exists():
        return writable_path

    # File doesn't exist yet - try to copy from bundled default
    try:
        # Get path to the bundled default file
        default_path = get_resource_path(default_file_path)

        if default_path.exists():
            # Copy default file to writable location
            shutil.copy2(default_path, writable_path)
        else:
            # Default file doesn't exist - create empty file
            # This handles the case where no default data was provided
            writable_path.write_text("[]", encoding="utf-8")

    except Exception:
        # If copy fails for any reason, create empty file
        # This ensures the application doesn't crash on first run
        writable_path.write_text("[]", encoding="utf-8")

    return writable_path
