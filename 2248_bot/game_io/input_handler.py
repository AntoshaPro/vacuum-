"""
Input handling for 2248 bot: simulating touches and swipes via ADB
"""

import subprocess
import time
from typing import Tuple, List
from config.default_config import ADB_DEVICE, MOVE_DELAY, ANIMATION_WAIT_TIME


class InputHandler:
    def __init__(self):
        self.adb_device = ADB_DEVICE
        self.move_delay = MOVE_DELAY
        self.animation_wait_time = ANIMATION_WAIT_TIME
    
    def tap_coordinates(self, x: int, y: int) -> bool:
        """
        Tap at specific coordinates on the screen
        """
        try:
            cmd = f"adb -s {self.adb_device} shell input tap {x} {y}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Tapped at ({x}, {y})")
                time.sleep(self.move_delay)  # Small delay after tap
                return True
            else:
                print(f"Failed to tap at ({x}, {y}): {result.stderr}")
                return False
        except Exception as e:
            print(f"Error tapping at ({x}, {y}): {e}")
            return False
    
    def swipe_coordinates(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 200) -> bool:
        """
        Swipe from start coordinates to end coordinates
        """
        try:
            cmd = f"adb -s {self.adb_device} shell input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) in {duration_ms}ms")
                return True
            else:
                print(f"Failed to swipe: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error swiping: {e}")
            return False
    
    def perform_chain_selection(self, board_coords: List[Tuple[int, int]], cell_size: Tuple[int, int], 
                               board_offset: Tuple[int, int]) -> bool:
        """
        Perform a gesture to select a chain of cells
        This could be multiple taps or a complex gesture depending on the game implementation
        """
        if len(board_coords) < 2:
            print("Need at least 2 coordinates to form a chain")
            return False
        
        # Calculate screen coordinates for each board position
        screen_coords = []
        cell_width, cell_height = cell_size
        offset_x, offset_y = board_offset
        
        for row, col in board_coords:
            center_x = offset_x + col * cell_width + cell_width // 2
            center_y = offset_y + row * cell_height + cell_height // 2
            screen_coords.append((center_x, center_y))
        
        # For a chain selection, we might need to do multiple taps or a complex gesture
        # This depends on how the game recognizes chain selections
        # For now, we'll implement a multi-point gesture using individual taps
        
        success = True
        for i, (x, y) in enumerate(screen_coords):
            if i == 0:
                # First tap to start the selection
                if not self.tap_coordinates(x, y):
                    success = False
                    break
            else:
                # Subsequent taps to extend the chain
                # In real implementation, this might be a drag gesture instead
                time.sleep(0.1)  # Small delay between taps
                if not self.tap_coordinates(x, y):
                    success = False
                    break
        
        # Wait for animation to complete
        time.sleep(self.animation_wait_time)
        
        return success
    
    def calculate_cell_dimensions(self, board_region: Tuple[int, int, int, int], 
                                 grid_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calculate the dimensions of each cell based on board region and grid size
        """
        x, y, width, height = board_region
        rows, cols = grid_size
        
        cell_width = width // cols
        cell_height = height // rows
        
        return cell_width, cell_height


def execute_move(chain: List[Tuple[int, int]], board_region: Tuple[int, int, int, int], 
                grid_size: Tuple[int, int]) -> bool:
    """
    Execute a move by selecting a chain on the game board
    """
    handler = InputHandler()
    
    # Calculate cell dimensions
    cell_size = handler.calculate_cell_dimensions(board_region, grid_size)
    board_offset = (board_region[0], board_region[1])
    
    # Perform the chain selection
    return handler.perform_chain_selection(chain, cell_size, board_offset)