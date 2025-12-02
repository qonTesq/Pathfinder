"""
Logging configuration and utilities for the Pathfinder application.

This module provides centralized logging setup and utility functions for
retrieving configured loggers throughout the application. It handles:

- Console logging with formatted output
- Optional file logging with configurable paths
- Configurable log levels from settings
- Consistent timestamp and message formatting
- Automatic file logging in production (bundled .exe)
- Log rotation to prevent excessive file sizes

All loggers created through this module will have consistent formatting
and output destinations, making it easier to track application flow and
debug issues.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from ..config import LOG_LEVEL


def is_production() -> bool:
    """
    Check if the application is running as a bundled executable.

    Returns:
        bool: True if running as PyInstaller bundle, False otherwise
    """
    return hasattr(sys, "_MEIPASS")


def get_log_directory() -> Path:
    """
    Get the appropriate directory for log files.

    In production (bundled .exe): logs/ folder next to the executable
    In development: logs/ folder in the project root

    Returns:
        Path: Directory path for log files
    """
    if is_production():
        # Running as bundled .exe - put logs next to the executable
        log_dir = Path(sys.executable).parent / "logs"
    else:
        # Running in development - put logs in project root
        log_dir = Path(__file__).parent.parent.parent.parent / "logs"

    # Ensure the directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def cleanup_old_logs(log_dir: Path, max_logs: int = 5) -> None:
    """
    Remove old log files, keeping only the most recent ones.

    Args:
        log_dir: Directory containing log files
        max_logs: Maximum number of log files to keep (default: 5)
    """
    if not log_dir.exists():
        return

    try:
        # Get all log files sorted by modification time (newest first)
        log_files = sorted(
            log_dir.glob("pathfinder_*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        # Remove old log files beyond the max_logs limit
        for old_log in log_files[max_logs:]:
            try:
                old_log.unlink()
            except Exception:
                pass  # Ignore errors when deleting old logs
    except Exception:
        pass  # Ignore errors in cleanup process


def get_session_log_filename() -> str:
    """
    Generate a timestamped log filename for the current session.

    Returns:
        str: Log filename in format 'pathfinder_YYYY-MM-DD_HH-MM-SS.log'
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"pathfinder_{timestamp}.log"


# Global flag to track if root logger has been configured
root_logger_configured = False


def setup_logger(name, log_file=None, level=LOG_LEVEL) -> logging.Logger:
    """
    Set up and configure a logger with console and optional file output.

    Creates a logger with the specified name and configures it with:
    - Console handler for immediate output to stdout
    - Automatic file logging ONLY in production (bundled .exe)
    - Optional custom file handler for additional logging
    - Consistent formatting for all messages
    - Configurable log level

    In development mode:
    - Logs only to console (stdout)
    - No log files are created

    In production builds (bundled .exe):
    - Logs are automatically saved to logs/pathfinder_YYYY-MM-DD_HH-MM-SS.log (next to the .exe)
    - New log file created each time the application starts
    - Keeps only the 5 most recent log files

    The first call to setup_logger configures the root logger, so all subsequent
    loggers (even those using logging.getLogger() directly) will inherit the
    console and file handlers automatically.

    Args:
        name: Logger name, typically the module name (__name__)
        log_file: Optional Path object for additional log file. If provided,
                  creates an extra FileHandler in addition to the automatic
                  production logging. Parent directories are created automatically.
        level: Log level as a string (e.g., 'INFO', 'DEBUG'). Defaults to
               LOG_LEVEL from config.

    Returns:
        Configured logging.Logger instance ready for use

    Example:
        >>> # Simple usage (auto-logs to file in production only)
        >>> logger = setup_logger(__name__)
        >>> logger.info('Application started')

        >>> # With custom additional log file
        >>> from pathlib import Path
        >>> logger = setup_logger(__name__, log_file=Path('custom.log'))
        >>> logger.error('An error occurred')
    """
    global root_logger_configured

    # Get or create logger with the specified name
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Configure root logger once so all child loggers inherit handlers
    if not root_logger_configured:
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))

        # Set up consistent message formatting
        # Format: timestamp - logger name - level - message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create console handler for stdout output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Automatically enable file logging ONLY in production (bundled .exe)
        # In development mode, logs only go to console
        if is_production():
            try:
                log_dir = get_log_directory()

                # Clean up old log files, keeping only the 5 most recent
                cleanup_old_logs(log_dir, max_logs=5)

                # Create a new timestamped log file for this session
                log_filename = get_session_log_filename()
                session_log_file = log_dir / log_filename

                # Use regular FileHandler for session-based logging
                file_handler = logging.FileHandler(
                    session_log_file,
                    encoding="utf-8",
                )
                file_handler.setLevel(getattr(logging, level.upper()))
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

                # Log that file logging is enabled (only to console to avoid recursion)
                console_handler.emit(
                    root_logger.makeRecord(
                        "pathfinder.utils.logger",
                        logging.INFO,
                        __file__,
                        0,
                        f"Production mode: Logging to {session_log_file}",
                        (),
                        None,
                    )
                )
            except Exception as e:
                # If file logging fails, continue with console only
                console_handler.emit(
                    root_logger.makeRecord(
                        "pathfinder.utils.logger",
                        logging.WARNING,
                        __file__,
                        0,
                        f"Failed to enable file logging: {e}",
                        (),
                        None,
                    )
                )
        else:
            # Development mode - console logging only
            console_handler.emit(
                root_logger.makeRecord(
                    "pathfinder.utils.logger",
                    logging.INFO,
                    __file__,
                    0,
                    "Development mode: Logging to console only",
                    (),
                    None,
                )
            )

        root_logger_configured = True

    # If a custom log file is specified, add handler to this specific logger
    if log_file:
        try:
            # Create parent directories if they don't exist
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # Set up consistent message formatting
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            # Create file handler for custom log file
            custom_file_handler = logging.FileHandler(log_file, encoding="utf-8")
            custom_file_handler.setLevel(getattr(logging, level.upper()))
            custom_file_handler.setFormatter(formatter)
            logger.addHandler(custom_file_handler)
        except Exception as e:
            logger.warning(f"Failed to create custom log file {log_file}: {e}")

    return logger


def get_logger(name) -> logging.Logger:
    """
    Get an existing logger by name.

    Retrieves a logger that was previously configured or creates a default
    one if it doesn't exist. This is useful for getting loggers in modules
    that haven't explicitly set one up.

    Args:
        name: Logger name to retrieve

    Returns:
        logging.Logger instance with the specified name

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug('Debug information')
    """
    return logging.getLogger(name)
