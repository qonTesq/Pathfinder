#!/usr/bin/env python3
"""
Image to Matrix Converter Script.

This script converts a floor plan image to a binary matrix representation
for use in pathfinding algorithms.

OpenCV is a library of programming functions for computer vision applications.

Requirements:
    - opencv-python>=4.11.0
    - numpy>=2.3.4

Usage:
    python scripts/convert.py
    # or
    uv run scripts/convert.py
"""

import os

import cv2
import numpy as np

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the image
image_path = os.path.join(script_dir, "..", "assets", "floorplan1_nolegend.JPG")
image = cv2.imread(image_path)

# Check if the image was loaded successfully
if image is None:  # pyright: ignore[reportUnnecessaryComparison]
    print("Error: Unable to load image.")
    exit(1)

# Resize the image to 40x40
resized_image = cv2.resize(image, (40, 40))

# Convert the resized image to grayscale
gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

# Threshold the image
_, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

# Invert the binary image
binary = cv2.bitwise_not(binary)

# Convert the binary image to a matrix of 0s and 1s
matrix = (binary / 255).astype(int)

# Save the matrix into a text file
output_path = os.path.join(script_dir, "..", "assets", "floorplan_matrix.txt")
np.savetxt(output_path, matrix, fmt="%d")

print("Matrix saved to assets/floorplan_matrix.txt")
