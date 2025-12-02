"""
Floorplan Visualizer Module for Pathfinder Application.

This module contains the main FloorplanVisualizer class that serves as the
central coordinator for the entire visualization system. It integrates all
UI components, manages application state, and coordinates interactions between
the user interface, pathfinding algorithms, and data management.

The visualizer acts as the "main controller" that:
- Initializes all UI components and sub-systems
- Maintains application state (positions, paths, mode, etc.)
- Delegates operations to specialized component classes
- Coordinates data flow between components
- Provides a unified interface for the main application

This architecture promotes separation of concerns by delegating specific
responsibilities to specialized classes (renderer, animator, editor, etc.)
while maintaining centralized state management and coordination.
"""

import logging
import tkinter as tk

from ..config import APP_TITLE
from ..core import SearchAlgorithm
from .animator import PathAnimator
from .builder import UIBuilder
from .controller import PathController
from .editor import EdgeWallEditor
from .handler import InteractionHandler
from .renderer import FloorplanRenderer
from .updater import InformationUpdater

logger = logging.getLogger(__name__)


class FloorplanVisualizer:
    """
    Main coordinator class for the hospital floorplan pathfinding visualizer.

    This class serves as the central hub that integrates all visualization
    components and manages the overall application state. It coordinates:
    - UI component lifecycle (creation, updates, cleanup)
    - Application state (mode, positions, paths, markers)
    - Event handling and user interactions
    - Data flow between pathfinding, rendering, and editing systems

    Architecture:
    The visualizer follows a delegation pattern where specialized classes
    handle specific responsibilities:
    - UIBuilder: Constructs UI components and layout
    - FloorplanRenderer: Handles all canvas drawing operations
    - PathAnimator: Manages path animation sequences
    - EdgeWallEditor: Handles edge wall editing functionality
    - PathController: Manages pathfinding operations
    - InteractionHandler: Processes user input events
    - InformationUpdater: Updates information panel

    State Management:
    The visualizer maintains centralized state that all components can access:
    - Position state: start_pos, goals, goal_markers
    - Path state: current_path, path_items, explored_cells
    - Animation state: is_animating, animation_segments
    - Edit state: edit_first, edge_wall_items
    - UI state: mode, algorithm selection, visualization options

    Attributes:
        root: Tkinter root window
        manager: FloorplanManager for data operations
        floorplan: NumPy array representing the hospital layout
        rows: Number of rows in the floorplan grid
        cols: Number of columns in the floorplan grid
        canvas: Main canvas for drawing (initialized by UIBuilder)

        # Cell and visualization items
        cell_items: Dict mapping (row, col) to canvas rectangle IDs
        wall_items: List of canvas IDs for wall boundaries
        path_items: List of canvas IDs for path visualization
        explored_items: List of canvas IDs for explored node dots
        edge_wall_items: Dict mapping edge to canvas line ID

        # Position and path state
        start_pos: Tuple (row, col) of start position or None
        start_marker: Canvas ID of start marker circle or None
        start_label: Canvas ID of start marker label or None
        goals: List of (row, col) tuples for goal positions
        goal_markers: Dict mapping goal position to (marker_id, label_id)
        current_path: List of (row, col) tuples forming current path
        explored_cells: List of Cell objects explored during pathfinding

        # Animation state
        is_animating: Boolean flag indicating if animation is running
        animation_segments: List of path segments for multi-goal animation
        current_segment_index: Index of currently animating segment
        complete_path_for_final_display: Complete path after animation
        visited_segment_goals: Goals visited so far during animation
        total_nodes_explored: Total nodes explored across all segments
        algorithm_name: Name of algorithm used for current path
        goals_visited: Number of goals visited in current path

        # Edit mode state
        mode: Current mode ("path" for Search, "edit" for Edit)
        edit_first: First selected cell for edge wall editing or None
        edit_marker: Canvas ID of edit selection marker or None
        adjacent_markers: List of canvas IDs for adjacent cell markers

        # UI component references
        stats_frame: Frame containing right-side controls
        algorithm_frame: Frame containing algorithm selector
        show_explored_check: Checkbutton for explored nodes toggle
        find_path_button: Button to execute pathfinding
        clear_path_button: Button to clear path and markers
        save_edits_button: Button to save edge wall changes
        clear_edits_button: Button to reset/revert edge wall changes
        path_stats_frame: Frame containing information display
        path_stats_text: Text widget for information display
        mode_var: StringVar for mode selection
        algorithm_var: StringVar for algorithm selection
        show_explored_var: BooleanVar for explored nodes toggle

        # Configuration
        display_coords: Boolean for coordinate display (future feature)

        # Component instances (delegation pattern)
        pathfinder: SearchAlgorithm instance for pathfinding operations
        renderer: FloorplanRenderer for canvas drawing
        animator: PathAnimator for path animation
        editor: EdgeWallEditor for edge wall management
        path_controller: PathController for pathfinding coordination
        interaction_handler: InteractionHandler for user input
        ui_builder: UIBuilder for UI construction
        information_updater: InformationUpdater instance for information panel updates
    """

    def __init__(self, root, floorplan_manager) -> None:
        """
        Initialize the floorplan visualizer with all components and state.

        This constructor:
        1. Stores references to root window and data manager
        2. Loads floorplan data and dimensions
        3. Initializes all state variables
        4. Creates component instances (renderer, animator, etc.)
        5. Builds the UI through UIBuilder
        6. Renders the initial floorplan
        7. Binds event handlers
        8. Configures initial mode

        Args:
            root: Tkinter root window or Toplevel widget
            floorplan_manager: FloorplanManager instance for data operations
        """
        # Store references to main application components
        self.root = root
        self.manager = floorplan_manager
        self.root.title(APP_TITLE)

        # Load floorplan data from manager
        self.floorplan = self.manager.get_floorplan()
        self.rows, self.cols = self.manager.get_dimensions()

        # Canvas reference (will be initialized by UIBuilder)
        self.canvas = None

        # Initialize canvas item tracking dictionaries
        # These store canvas IDs for later manipulation (delete, modify)
        self.cell_items = {}  # Maps (row, col) -> rectangle ID
        self.wall_items = []  # List of boundary line IDs

        # Initialize position and marker state
        self.start_pos = None  # (row, col) or None
        self.current_path = []  # List of (row, col) positions
        self.path_items = []  # Canvas IDs for path visualization
        self.explored_items = []  # Canvas IDs for explored node dots
        self.explored_cells = []  # List of Cell objects from pathfinding
        self.start_marker = None  # Canvas ID of start marker circle
        self.start_label = None  # Canvas ID of start marker text
        self.goals = []  # List of (row, col) goal positions
        self.goal_markers = {}  # Maps (row, col) -> (marker_id, label_id)

        # Initialize animation state
        self.is_animating = False  # Flag to control animation loop
        self.animation_segments = []  # List of path segments for animation
        self.current_segment_index = 0  # Current segment being animated
        self.complete_path_for_final_display = []  # Full path after animation
        self.visited_segment_goals = []  # Goals visited during animation
        self.total_nodes_explored = 0  # Cumulative exploration count
        self.algorithm_name = ""  # "A*" or "Dijkstra"
        self.goals_visited = 0  # Number of goals in current path
        self.display_coords = False  # Future feature for coordinate display

        # Initialize edit mode state
        self.mode = "path"  # Current mode: "path" or "edit"
        self.edit_first = None  # First selected cell in edit mode
        self.edit_marker = None  # Canvas ID of edit selection marker
        self.adjacent_markers = []  # Canvas IDs of adjacent cell markers
        self.edge_wall_items = {}  # Maps edge frozenset -> line ID

        # UI component references (initialized by UIBuilder)
        self.stats_frame = None  # Right-side control panel frame
        self.algorithm_frame = None  # Algorithm selector frame
        self.show_explored_check = None  # Explored nodes checkbutton
        self.find_path_button = None  # Search button
        self.clear_path_button = None  # Clear path button
        self.save_edits_button = None  # Save edits button
        self.clear_edits_button = None  # Reset edits button
        self.path_stats_frame = None  # Information display frame
        self.path_stats_text = None  # Information text widget
        self.mode_var = None  # StringVar for mode radio buttons

        # Initialize Tkinter variables for UI controls
        self.algorithm_var = tk.StringVar(value="A*")  # Default to A*
        self.show_explored_var = tk.BooleanVar(value=True)  # Show explored by default

        # Initialize pathfinding engine with floorplan and edge walls
        self.pathfinder = SearchAlgorithm(
            self.floorplan, edge_walls=self.manager.edge_walls
        )

        # Create component instances using delegation pattern
        # Each component handles a specific aspect of functionality
        self.renderer = FloorplanRenderer(self)  # Canvas drawing operations
        self.animator = PathAnimator(self)  # Path animation sequences
        self.editor = EdgeWallEditor(self)  # Edge wall editing
        self.path_controller = PathController(self)  # Pathfinding coordination
        self.interaction_handler = InteractionHandler(self)  # User input processing
        self.ui_builder = UIBuilder(self)  # UI construction
        self.information_updater = InformationUpdater(self)  # Information panel updates

        # Build the user interface
        self.ui_builder.build_ui()

        # Draw the initial floorplan
        self.renderer.draw_floorplan()

        # Verify canvas was initialized by UIBuilder
        assert self.canvas is not None, "Canvas should be initialized by UIBuilder"

        # Bind click event handler to canvas
        self.canvas.bind("<Button-1>", self.interaction_handler.on_canvas_click)

        # Configure initial mode (Search mode)
        self.on_mode_change()

    def find_and_draw_path(self) -> None:
        """
        Delegate pathfinding operation to PathController.

        This method is called when the user clicks the Search button.
        It triggers the multi-goal pathfinding algorithm and initiates
        animated visualization of the result.

        The PathController handles:
        - Validation of start and goal positions
        - Goal prioritization based on ward urgency
        - Path segment computation
        - Animation initialization
        """
        self.path_controller.find_and_draw_path()

    def clear_path(self) -> None:
        """
        Delegate path clearing operation to PathController.

        This method is called when the user clicks the Clear button
        in Search mode. It removes all path-related visualizations
        and resets position markers.

        The PathController clears:
        - Start position and marker
        - Goal positions and markers
        - Path visualization
        - Explored nodes visualization
        - Animation state
        """
        self.path_controller.clear_path()

    def update_path_stats(
        self,
        algorithm=None,
        path_length=None,
        nodes_explored=None,
        goals_visited=None,
    ) -> None:
        """
        Delegate information panel update to InformationUpdater.

        This method is called whenever the information panel needs to
        be refreshed with current state or pathfinding results.

        Args:
            algorithm: Name of algorithm used ("A*" or "Dijkstra")
            path_length: Number of steps in the computed path
            nodes_explored: Number of nodes explored during search
            goals_visited: Number of goals visited in multi-goal path
        """
        self.information_updater.update_path_stats(
            algorithm, path_length, nodes_explored, goals_visited
        )

    def on_mode_change(self) -> None:
        """
        Delegate mode change handling to InteractionHandler.

        This method is called when the user switches between Search
        and Edit modes using the radio buttons. The handler manages
        the complex state transitions and UI updates required.

        Mode changes involve:
        - Showing/hiding mode-specific controls
        - Clearing incompatible state
        - Updating information display
        - Refreshing canvas elements
        """
        self.interaction_handler.on_mode_change()

    def on_algorithm_change(self) -> None:
        """
        Delegate algorithm change handling to InteractionHandler.

        This method is called when the user switches between A* and
        Dijkstra algorithms. The handler updates the pathfinder's
        heuristic function and clears any existing path.

        Algorithm changes affect:
        - Pathfinder heuristic (Manhattan distance vs zero)
        - Existing path visualization (cleared)
        - Information display
        """
        self.interaction_handler.on_algorithm_change()

    def on_show_explored_change(self) -> None:
        """
        Delegate explored nodes visibility toggle to InteractionHandler.

        This method is called when the user toggles the "Highlight
        explored nodes" checkbox. The handler shows or hides the
        explored node visualizations accordingly.

        Toggling affects:
        - Visibility of explored node dots on canvas
        - No impact on pathfinding computation
        """
        self.interaction_handler.on_show_explored_change()

    def save_edits(self) -> None:
        """
        Delegate edge wall save operation to InteractionHandler.

        This method is called when the user clicks the Save button
        in Edit mode. The handler persists edge wall changes to file
        and displays appropriate feedback.

        Save operation:
        - Writes edge walls to JSON file
        - Shows success/error message dialog
        - Maintains current edit state
        """
        self.interaction_handler.save_edits()

    def clear_edits(self) -> None:
        """
        Delegate edge wall revert operation to InteractionHandler.

        This method is called when the user clicks the Reset button
        in Edit mode. The handler reverts all unsaved edge wall changes
        and refreshes the display.

        Reset operation:
        - Reloads edge walls from file
        - Discards unsaved changes
        - Updates pathfinder and visualization
        """
        self.interaction_handler.clear_edits()
