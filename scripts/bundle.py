#!/usr/bin/env python3
"""
PyInstaller Bundle Script for Pathfinder Application.

This script creates a standalone executable using PyInstaller that bundles
Python and all dependencies into a single file.

Requirements:
    - pyinstaller>=6.16.0

Usage:
    python scripts/bundle.py
    # or
    uv run scripts/bundle.py

The script will:
1. Clean previous builds
2. Build and sync dependencies
3. Create executable with PyInstaller using optimized settings

Output:
    - Windows: dist/Pathfinder.exe
    - macOS: dist/Pathfinder
    - Linux: dist/Pathfinder
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build() -> None:
    """Remove previous build artifacts."""
    print("[1/3] Cleaning previous builds...")

    dirs_to_clean = ["dist", "build"]
    files_to_clean = ["Pathfinder.spec"]

    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

    for file_name in files_to_clean:
        if Path(file_name).exists():
            Path(file_name).unlink()
            print(f"  Removed {file_name}")


def build_and_sync() -> None:
    """Build the package and sync dependencies."""
    print("\n[2/3] Building package and syncing dependencies...")

    # Build the package
    result = subprocess.run(
        ["uv", "build"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Build failed:\n{result.stderr}")
        raise RuntimeError("Failed to build package")

    print("  Package built successfully")

    # Sync dependencies
    result = subprocess.run(
        ["uv", "sync"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Sync failed:\n{result.stderr}")
        raise RuntimeError("Failed to sync dependencies")

    print("  Dependencies synced successfully")


def create_executable() -> Path:
    """
    Create the executable using PyInstaller.

    Returns:
        Path: Path to the created executable
    """
    print("\n[3/3] Creating executable with PyInstaller...")

    # Determine platform-specific settings
    system = platform.system()

    # Base PyInstaller command
    # Use run.py entry point to avoid relative import issues
    cmd = [
        "uv",
        "run",
        "pyinstaller",
        "run.py",
        "--name",
        "Pathfinder",
        "--onefile",
        "--windowed",
    ]

    # Add icon if it exists (platform-specific)
    if system == "Windows":
        icon_path = Path("src/pathfinder/assets/icon.ico")
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
            cmd.extend(["--add-data", f"{icon_path};src/pathfinder/assets"])
            print(f"  Adding icon: {icon_path}")
    elif system == "Darwin":  # macOS
        icon_path = Path("src/pathfinder/assets/icon.icns")
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
            cmd.extend(["--add-data", f"{icon_path}:src/pathfinder/assets"])
            print(f"  Adding icon: {icon_path}")
    else:  # Linux
        icon_path = Path("src/pathfinder/assets/icon.ico")
        if icon_path.exists():
            cmd.extend(["--add-data", f"{icon_path}:src/pathfinder/assets"])
            print(f"  Adding icon: {icon_path}")

    # Add data files
    data_file = Path("src/pathfinder/data/edge_walls.json")
    if data_file.exists():
        if system == "Windows":
            cmd.extend(["--add-data", f"{data_file};src/pathfinder/data"])
        else:
            cmd.extend(["--add-data", f"{data_file}:src/pathfinder/data"])
        print(f"  Adding data: {data_file}")

    # Exclude unnecessary modules to reduce size
    exclude_modules = [
        "cv2",  # OpenCV - only used in dev scripts, not in app
        "PIL",
        "matplotlib",
        "scipy",
        "pandas",
        "pytest",
        "setuptools",
        "unittest",
        "distutils",
        "email",
        "html",
        "http",
        "urllib",
        "xml",
        "pydoc",
        "doctest",
        "asyncio",
        # PyInstaller build dependencies - not needed at runtime
        "altgraph",
        "macholib",
        "packaging",
        "pefile",
        "pyinstaller_hooks_contrib",
        "pywin32_ctypes",
    ]

    for module in exclude_modules:
        cmd.extend(["--exclude-module", module])

    # Additional flags for optimization
    cmd.extend(
        [
            "--noconfirm",
            "--clean",
        ]
    )

    print("  Running PyInstaller...")
    print(f"  Command: {' '.join(cmd)}")

    # Run PyInstaller
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"\nPyInstaller failed:\n{result.stderr}")
        raise RuntimeError("Failed to create executable with PyInstaller")

    # Determine output path
    if system == "Windows":
        output_path = Path("dist/Pathfinder.exe")
    else:
        output_path = Path("dist/Pathfinder")

    if not output_path.exists():
        raise RuntimeError(f"Expected executable not found at {output_path}")

    print(f"  Created: {output_path}")
    return output_path


def main() -> int:
    """
    Main bundle function.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        print("=" * 60)
        print("Building Pathfinder with PyInstaller")
        print("=" * 60)
        print()
        print(f"Platform: {platform.system()} {platform.machine()}")
        print()

        # Build process
        clean_build()
        build_and_sync()
        output_path = create_executable()

        # Success message
        print()
        print("=" * 60)
        print("Build successful!")
        print("=" * 60)
        print()
        print(f"Executable: {output_path}")
        print()
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n\nBuild failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
