"""
Screen capture and image processing for 2248 bot
"""

import subprocess
import cv2
import numpy as np
import pytesseract
from typing import List, Tuple, Optional
import os
from config.default_config import ADB_DEVICE, SCREENSHOT_PATH


class ScreenCapture:
    def __init__(self):
        self.adb_device = ADB_DEVICE
        self.screenshot_path = SCREENSHOT_PATH
    
    def capture_screen(self) -> bool:
        """
        Capture screenshot from the emulator/device using ADB
        """
        try:
            cmd = f"adb -s {self.adb_device} exec-out screencap -p > {self.screenshot_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Screenshot saved to {self.screenshot_path}")
                return True
            else:
                print(f"Failed to capture screenshot: {result.stderr}")
                # Fallback to command without device specification
                cmd = f"adb exec-out screencap -p > {self.screenshot_path}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.returncode == 0
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return False
    
    def load_screenshot(self) -> Optional[np.ndarray]:
        """
        Load the screenshot image from file
        """
        if os.path.exists(self.screenshot_path):
            image = cv2.imread(self.screenshot_path)
            if image is not None:
                return image
            else:
                print("Could not load screenshot image")
                return None
        else:
            print(f"Screenshot file does not exist: {self.screenshot_path}")
            return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for better OCR results
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        return thresh
    
    def detect_game_board(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the game board area in the screenshot
        Returns (x, y, width, height) of the board region
        """
        # This is a simplified approach - in practice, you'd need more sophisticated
        # board detection based on the specific game UI
        height, width = image.shape[:2]
        
        # Assume the game board is roughly centered and takes up middle portion of screen
        # This would need adjustment based on actual game layout
        margin_x = width // 5  # 20% margin on sides
        margin_y = height // 4  # 25% margin on top/bottom (assuming UI elements at top/bottom)
        
        board_x = margin_x
        board_y = margin_y
        board_width = width - 2 * margin_x
        board_height = height - 2 * margin_y
        
        return (board_x, board_y, board_width, board_height)


class NumberRecognition:
    def __init__(self):
        # Initialize with common templates or pre-trained models for number recognition
        pass
    
    def extract_numbers_from_region(self, image: np.ndarray, grid_size: Tuple[int, int]) -> List[List[int]]:
        """
        Extract numbers from a grid region of the game board
        Args:
            image: The cropped game board image
            grid_size: (rows, cols) tuple representing the grid dimensions
        Returns:
            2D list representing the game board with numbers
        """
        rows, cols = grid_size
        board = [[0 for _ in range(cols)] for _ in range(rows)]
        
        img_height, img_width = image.shape[:2]
        
        cell_height = img_height // rows
        cell_width = img_width // cols
        
        for r in range(rows):
            for c in range(cols):
                # Extract the cell region
                y1 = r * cell_height
                y2 = min((r + 1) * cell_height, img_height)
                x1 = c * cell_width
                x2 = min((c + 1) * cell_width, img_width)
                
                cell_img = image[y1:y2, x1:x2]
                
                # Preprocess the cell for better OCR
                processed_cell = self.preprocess_cell(cell_img)
                
                # Extract number using OCR
                number = self.recognize_number(processed_cell)
                board[r][c] = number if number is not None else 0
        
        return board
    
    def preprocess_cell(self, cell_img: np.ndarray) -> np.ndarray:
        """
        Preprocess a single cell image for better OCR
        """
        # Convert to grayscale if needed
        if len(cell_img.shape) == 3:
            gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = cell_img
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        # Optionally apply morphological operations to clean up
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def recognize_number(self, cell_img: np.ndarray) -> Optional[int]:
        """
        Recognize the number in a single cell using OCR
        """
        try:
            # Configure tesseract for digits only
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
            
            # Perform OCR
            text = pytesseract.image_to_string(cell_img, config=custom_config)
            
            # Clean up the recognized text
            text = text.strip()
            
            # Try to convert to integer
            if text.isdigit():
                return int(text)
            elif text:
                # Handle special cases or fuzzy matching
                # For example, '0' might be recognized as 'O'
                text = text.replace('O', '0').replace('l', '1').replace('I', '1')
                if text.isdigit():
                    return int(text)
            
            return None
        except Exception as e:
            print(f"Error recognizing number: {e}")
            return None


def get_game_state(grid_size: Tuple[int, int] = (6, 6)) -> List[List[int]]:
    """
    Main function to capture screen and extract game state
    """
    capturer = ScreenCapture()
    
    if not capturer.capture_screen():
        print("Failed to capture screen")
        return []
    
    image = capturer.load_screenshot()
    if image is None:
        print("Failed to load screenshot")
        return []
    
    # Detect the game board region
    board_region = capturer.detect_game_board(image)
    if board_region is None:
        print("Could not detect game board")
        return []
    
    x, y, w, h = board_region
    board_image = image[y:y+h, x:x+w]
    
    # Extract numbers from the board
    recognizer = NumberRecognition()
    board_state = recognizer.extract_numbers_from_region(board_image, grid_size)
    
    return board_state