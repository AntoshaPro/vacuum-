#!/usr/bin/env python3
"""
Demo script to showcase the automatic field size detection feature
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from game_io.screen_capture import ScreenCapture
import numpy as np
import cv2


def create_test_board_image():
    """
    Create a synthetic test image to simulate a game board for testing the detection algorithms
    """
    # Create a blank image (simulating a screenshot)
    height, width = 800, 600
    image = np.ones((height, width, 3), dtype=np.uint8) * 240  # Light gray background
    
    # Draw a grid (simulating a 5x5 game board)
    board_x, board_y = 100, 150
    board_width, board_height = 400, 400
    rows, cols = 5, 5
    
    cell_width = board_width // cols
    cell_height = board_height // rows
    
    # Draw grid lines
    for i in range(rows + 1):
        y = board_y + i * cell_height
        cv2.line(image, (board_x, y), (board_x + board_width, y), (200, 200, 200), 2)
    
    for j in range(cols + 1):
        x = board_x + j * cell_width
        cv2.line(image, (x, board_y), (x, board_y + board_height), (200, 200, 200), 2)
    
    # Draw some sample cells
    for i in range(rows):
        for j in range(cols):
            cell_x = board_x + j * cell_width
            cell_y = board_y + i * cell_height
            # Draw rectangle for the cell
            cv2.rectangle(image, 
                         (cell_x + 2, cell_y + 2), 
                         (cell_x + cell_width - 2, cell_y + cell_height - 2), 
                         (255, 255, 255), -1)  # White cell
            
            # Draw a number in the cell (for visualization)
            cv2.putText(image, f"{2**(i+j+1)}", 
                       (cell_x + cell_width//3, cell_y + cell_height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    return image


def demo_automatic_detection():
    """
    Demonstrate the automatic field size detection functionality
    """
    print("=== 2248 Bot: Automatic Field Size Detection Demo ===\n")
    
    # Create a test image
    print("1. Creating a test game board image...")
    test_image = create_test_board_image()
    print(f"   Created test image with dimensions: {test_image.shape[1]}x{test_image.shape[0]}")
    
    # Initialize the screen capture module
    capturer = ScreenCapture()
    
    # Test board region detection
    print("\n2. Detecting game board region...")
    board_region = capturer.detect_game_board(test_image)
    if board_region:
        x, y, w, h = board_region
        print(f"   Detected board region: (x={x}, y={y}, width={w}, height={h})")
    else:
        print("   Failed to detect board region")
        return
    
    # Extract the board image
    board_x, board_y, board_w, board_h = board_region
    board_image = test_image[board_y:board_y+board_h, board_x:board_x+board_w]
    
    # Test grid size detection
    print("\n3. Detecting grid size from board image...")
    detected_size = capturer.detect_grid_size(board_image)
    print(f"   Detected grid size: {detected_size[0]} rows x {detected_size[1]} columns")
    
    # Show what the get_game_state function would return (without OCR)
    print("\n4. Simulating get_game_state function behavior...")
    print("   In a real scenario, the bot would:")
    print(f"   - Capture screen and detect board region: {board_region}")
    print(f"   - Detect grid size: {detected_size[0]}x{detected_size[1]}")
    print("   - Extract numbers from each cell using OCR")
    print("   - Find valid chains and execute moves")
    
    print("\n=== Demo completed successfully! ===")
    print("\nKey features implemented:")
    print("- Automatic detection of game board region using edge detection")
    print("- Automatic detection of grid dimensions using contour analysis")
    print("- Fallback methods for robust detection")
    print("- Support for various grid sizes (not hardcoded)")


if __name__ == "__main__":
    demo_automatic_detection()