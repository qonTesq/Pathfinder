"""
Theme and styling utilities for the Pathfinder application.

This module provides platform-specific theme configuration and styling
functions for the Tkinter GUI. It handles:
- Dark/light mode theming
- Platform-specific styling (Windows, macOS, Linux)
- Sun Valley ttk theme integration
- Windows-specific effects (Mica, header colors)

Functions:
    apply_theme: Apply platform-specific theme styling to the application window
"""

import logging
import sys
import tkinter as tk

import sv_ttk

from ..config import DARK_MODE
from .logger import setup_logger

# Initialize logger for this module
logger: logging.Logger = setup_logger(__name__)


def apply_theme(root: tk.Tk) -> None:
    """
    Apply platform-specific theme styling to the application window.

    This function configures the application's appearance based on:
    1. The operating system (Windows, macOS, Linux)
    2. System dark mode preference (automatically detected)
    3. Python version and available styling libraries

    On Windows 11+: Uses pywinstyles to apply native Windows 11 Mica effect
    with matching header colors. On Windows 10: Applies dark/light style and
    fixes rendering with alpha adjustment workaround.

    On all platforms: Sets the sv_ttk (Sun Valley) theme to match system
    dark mode preference for consistent cross-platform appearance.

    Args:
        root (tk.Tk): The root Tkinter window to apply the theme to.

    Returns:
        None

    Side Effects:
        - Modifies the appearance of the root window
        - Sets the global sv_ttk theme
        - May apply Windows-specific styling if on Windows
    """

    # Apply platform-specific styling for Windows
    if sys.platform == "win32":
        import pywinstyles

        version = sys.getwindowsversion()

        # Windows 11+ (build 22000 and later): Use native Mica effect with header color
        if version.major == 10 and version.build >= 22000:
            # Set header color to match dark/light mode preference
            header_color = "#1c1c1c" if DARK_MODE else "#fafafa"
            pywinstyles.change_header_color(root, header_color)

        # Windows 10: Apply dark/light style with workaround for rendering issues
        elif version.major == 10:
            # Apply the appropriate style based on dark mode
            style_name = "dark" if DARK_MODE else "normal"
            pywinstyles.apply_style(root, style_name)

            # Workaround: Toggle alpha to force window redraw and fix rendering glitches
            # This fixes occasional UI artifacts on Windows 10
            root.wm_attributes("-alpha", 0.99)
            root.wm_attributes("-alpha", 1)

    # Apply Sun Valley theme globally for all platforms
    # This ensures consistent styling of ttk widgets across OS
    sv_ttk.set_theme("dark" if DARK_MODE else "light")

    logger.debug(f"Applied {'dark' if DARK_MODE else 'light'} theme on {sys.platform}")
