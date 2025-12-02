"""
UI Builder Module for Pathfinder Visualizer.

This module contains the UIBuilder class responsible for constructing all
UI components including the canvas, control panels, buttons, and interactive
elements. It separates the UI construction logic from the main visualizer.
"""

import logging
import tkinter as tk
from tkinter import ttk

from ..config import GRID_CELL_SIZE, WARDS

logger = logging.getLogger(__name__)


class UIBuilder:
    """
    Builds and constructs all UI components for the floorplan visualizer.

    This class handles the creation of:
    - Main canvas for floorplan display
    - Control panels and frames
    - Mode selectors (Search/Edit)
    - Algorithm selectors (A*/Dijkstra)
    - Action buttons
    - Ward legend
    - Information display area

    Attributes:
        vis: Reference to the parent FloorplanVisualizer instance
    """

    def __init__(self, visualizer) -> None:
        """
        Initialize the UIBuilder with a reference to the visualizer.

        Args:
            visualizer: The parent FloorplanVisualizer instance
        """
        self.vis = visualizer

    def build_ui(self) -> None:
        """
        Build the complete user interface.

        This is the main entry point that coordinates the creation of all
        UI components in the proper order.
        """
        self.create_canvas()
        self.create_controls_panel()

    def create_canvas(self) -> None:
        """
        Create the main canvas for displaying the floorplan grid.

        The canvas size is calculated based on the floorplan dimensions
        and the configured cell size. The canvas is positioned on the left
        side of the window.
        """
        # Calculate canvas dimensions based on grid size
        canvas_width = self.vis.cols * GRID_CELL_SIZE
        canvas_height = self.vis.rows * GRID_CELL_SIZE

        # Create canvas with white background for clear visualization
        self.vis.canvas = tk.Canvas(
            self.vis.root,
            width=canvas_width,
            height=canvas_height,
            bg="white",
            highlightthickness=0,  # Remove border highlight
        )
        self.vis.canvas.pack(side=tk.LEFT, padx=10, pady=10)

    def create_controls_panel(self) -> None:
        """
        Create the right-side control panel containing all UI controls.

        This panel includes:
        - Controls section (mode, algorithm, buttons)
        - Information section (statistics display)
        - Ward legend (color-coded ward information)
        """
        # Create fixed-width frame for controls on the right side
        self.vis.stats_frame = ttk.Frame(self.vis.root, width=300)
        self.vis.stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        self.vis.stats_frame.pack_propagate(False)  # Maintain fixed width

        # Build individual sections
        self.create_controls_section()
        self.create_information_section()
        self.create_ward_legend()

    def create_controls_section(self) -> None:
        """
        Create the controls section with mode selector, algorithm options, and buttons.

        This section allows users to:
        - Switch between Search and Edit modes
        - Select pathfinding algorithm (A* or Dijkstra)
        - Toggle explored nodes visualization
        - Trigger search/clear operations
        """
        # Create bordered frame for visual grouping
        controls_frame = ttk.LabelFrame(
            self.vis.stats_frame, text="Controls", borderwidth=3, relief="ridge"
        )
        controls_frame.pack(fill="x", pady=(10, 5))

        # Add all control elements
        self.create_mode_selector(controls_frame)
        self.create_algorithm_selector(controls_frame)
        self.create_explored_checkbox(controls_frame)
        self.create_path_buttons(controls_frame)
        self.create_edit_buttons(controls_frame)

    def create_mode_selector(self, parent) -> None:
        """
        Create radio buttons for switching between Search and Edit modes.

        Args:
            parent: The parent widget to contain the mode selector
        """
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill="x", padx=5, pady=(5, 5))
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)

        # Initialize mode variable with Search mode as default
        self.vis.mode_var = tk.StringVar(value="path")

        # Search mode: Find paths between start and goals
        ttk.Radiobutton(
            mode_frame,
            text="Search",
            variable=self.vis.mode_var,
            value="path",
            command=self.vis.on_mode_change,
        ).pack(side=tk.LEFT, padx=(6, 0))

        # Edit mode: Add/remove edge walls
        ttk.Radiobutton(
            mode_frame,
            text="Edit",
            variable=self.vis.mode_var,
            value="edit",
            command=self.vis.on_mode_change,
        ).pack(side=tk.LEFT, padx=(6, 0))

    def create_algorithm_selector(self, parent) -> None:
        """
        Create radio buttons for selecting the pathfinding algorithm.

        Args:
            parent: The parent widget to contain the algorithm selector
        """
        # Store reference to frame for dynamic show/hide
        self.vis.algorithm_frame = ttk.Frame(parent)
        self.vis.algorithm_frame.pack(fill="x", padx=5, pady=(0, 5))

        ttk.Label(self.vis.algorithm_frame, text="Algorithm:").pack(side=tk.LEFT)

        # A* algorithm: Uses heuristic for faster pathfinding
        ttk.Radiobutton(
            self.vis.algorithm_frame,
            text="A*",
            variable=self.vis.algorithm_var,
            value="A*",
            command=self.vis.on_algorithm_change,
        ).pack(side=tk.LEFT, padx=(6, 0))

        # Dijkstra algorithm: Exhaustive search without heuristic
        ttk.Radiobutton(
            self.vis.algorithm_frame,
            text="Dijkstra",
            variable=self.vis.algorithm_var,
            value="Dijkstra",
            command=self.vis.on_algorithm_change,
        ).pack(side=tk.LEFT, padx=(6, 0))

    def create_explored_checkbox(self, parent) -> None:
        """
        Create checkbox for toggling explored nodes visualization.

        Args:
            parent: The parent widget to contain the checkbox
        """
        # Checkbox to show/hide explored nodes during pathfinding
        self.vis.show_explored_check = ttk.Checkbutton(
            parent,
            text="Highlight explored nodes",
            variable=self.vis.show_explored_var,
            style="Switch.TCheckbutton",
            command=self.vis.on_show_explored_change,
        )
        self.vis.show_explored_check.pack(fill="x", padx=5, pady=(0, 5))

    def create_path_buttons(self, parent) -> None:
        """
        Create buttons for pathfinding operations (Search and Clear).

        These buttons are shown only in Search mode.

        Args:
            parent: The parent widget to contain the buttons
        """
        # Search button: Execute pathfinding algorithm
        self.vis.find_path_button = ttk.Button(
            parent,
            text="Search",
            style="Accent.TButton",  # Highlighted style for primary action
            width=6,
            command=self.vis.find_and_draw_path,
        )

        # Clear button: Remove current path and markers
        self.vis.clear_path_button = ttk.Button(
            parent, text="Clear", width=6, command=self.vis.clear_path
        )

    def create_edit_buttons(self, parent) -> None:
        """
        Create buttons for edge wall editing operations (Save and Reset).

        These buttons are shown only in Edit mode.

        Args:
            parent: The parent widget to contain the buttons
        """
        # Save button: Persist edge wall changes to file
        self.vis.save_edits_button = ttk.Button(
            parent,
            text="Save",
            style="Accent.TButton",  # Highlighted style for primary action
            width=6,
            command=self.vis.save_edits,
        )

        # Reset button: Revert to last saved edge wall state
        self.vis.clear_edits_button = ttk.Button(
            parent, text="Reset", width=6, command=self.vis.clear_edits
        )

    def create_information_section(self) -> None:
        """
        Create the information display section for showing statistics and instructions.

        This section displays:
        - Current start and goal positions
        - Path statistics (length, nodes explored)
        - Edit mode instructions
        - Algorithm information
        """
        # Create bordered frame for information display
        self.vis.path_stats_frame = ttk.LabelFrame(
            self.vis.stats_frame, text="Information", borderwidth=3, relief="ridge"
        )
        self.vis.path_stats_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Text widget for displaying multi-line information
        self.vis.path_stats_text = tk.Text(
            self.vis.path_stats_frame,
            height=6,
            wrap=tk.WORD,  # Word wrapping for readability
            font=("TkDefaultFont", 9),
            state=tk.DISABLED,  # Read-only by default
            relief=tk.FLAT,  # Flat appearance to match theme
            padx=2,
            pady=2,
        )
        self.vis.path_stats_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 5))

    def create_ward_legend(self) -> None:
        """
        Create the ward legend showing all hospital wards with their colors and priorities.

        The legend displays:
        - Color swatch for each ward
        - Ward name/description
        - Priority value (higher = more urgent)

        Wards are sorted by priority in descending order.
        """
        # Create bordered frame for ward legend
        wards_frame = ttk.LabelFrame(
            self.vis.stats_frame, text="Wards", borderwidth=3, relief="ridge"
        )
        wards_frame.pack(fill="x", pady=(0, 10))

        # Convert wards dictionary to sorted list by priority
        wards_list = [
            {
                "code": code,
                "name": ward.description,
                "colour": ward.colour,
                "priority": ward.priority,
            }
            for code, ward in WARDS.items()
        ]
        # Sort by priority descending (most urgent first)
        wards_list.sort(key=lambda x: x["priority"], reverse=True)

        # Create a row for each ward
        for i, info in enumerate(wards_list):
            # Extra padding for last item
            pady = (2, 5) if i == len(wards_list) - 1 else 2
            ward_frame = ttk.Frame(wards_frame)
            ward_frame.pack(anchor="w", padx=5, pady=pady, fill="x")

            # Color swatch showing ward's color
            swatch = tk.Canvas(
                ward_frame, width=18, height=18, bg=info["colour"], highlightthickness=0
            )
            swatch.pack(side=tk.LEFT, padx=(0, 5))

            # Ward name
            tk.Label(
                ward_frame, text=info["name"], font=("TkDefaultFont", 10), anchor="w"
            ).pack(side=tk.LEFT)

            # Separator line between name and priority
            ttk.Separator(ward_frame, orient="horizontal").pack(
                side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5)
            )

            # Priority value in parentheses
            tk.Label(
                ward_frame, text=f"({info['priority']})", font=("TkDefaultFont", 10)
            ).pack(side=tk.RIGHT)
