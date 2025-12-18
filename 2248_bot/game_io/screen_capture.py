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
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Try to detect grid patterns using edge detection and Hough transform
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines in the image
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
        
        if lines is not None:
            # Separate horizontal and vertical lines
            horizontal_lines = []
            vertical_lines = []
            
            for rho, theta in lines[:, 0]:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                
                # Classify as horizontal or vertical (with some tolerance)
                if abs(theta) < np.pi / 4 or abs(theta - np.pi) < np.pi / 4:
                    vertical_lines.append((rho, theta))
                else:
                    horizontal_lines.append((rho, theta))
            
            # If we found both horizontal and vertical lines, try to determine the grid
            if len(horizontal_lines) >= 2 and len(vertical_lines) >= 2:
                # Sort lines by position
                horizontal_positions = []
                vertical_positions = []
                
                for rho, theta in horizontal_lines:
                    # For horizontal lines (theta ~ pi/2), y = rho / sin(theta)
                    if abs(np.sin(theta)) > 0.1:  # Avoid division by near-zero
                        y_pos = rho / np.sin(theta)
                        horizontal_positions.append(y_pos)
                
                for rho, theta in vertical_lines:
                    # For vertical lines (theta ~ 0), x = rho / cos(theta)
                    if abs(np.cos(theta)) > 0.1:  # Avoid division by near-zero
                        x_pos = rho / np.cos(theta)
                        vertical_positions.append(x_pos)
                
                if len(horizontal_positions) >= 2 and len(vertical_positions) >= 2:
                    horizontal_positions.sort()
                    vertical_positions.sort()
                    
                    # Find the bounding box of the grid
                    x_min, x_max = int(min(vertical_positions)), int(max(vertical_positions))
                    y_min, y_max = int(min(horizontal_positions)), int(max(horizontal_positions))
                    
                    # Adjust to ensure valid bounds
                    x_min = max(0, x_min)
                    y_min = max(0, y_min)
                    x_max = min(image.shape[1], x_max)
                    y_max = min(image.shape[0], y_max)
                    
                    return (x_min, y_min, x_max - x_min, y_max - y_min)
        
        # If line detection fails, fall back to a rough estimation
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
    
    def detect_grid_size(self, board_image: np.ndarray) -> Tuple[int, int]:
        """
        Automatically detect the grid size (rows, cols) from the board image
        Uses multiple approaches to ensure robust detection
        """
        # First, try contour-based detection
        rows, cols = self._detect_grid_by_contours(board_image)
        
        # If contour detection failed or seems unreliable, try edge-based detection
        if rows < 2 or cols < 2:
            rows, cols = self._detect_grid_by_edges(board_image)
        
        # As a last resort, try a pattern-based approach
        if rows < 2 or cols < 2:
            rows, cols = self._detect_grid_by_pattern(board_image)
        
        # Validate the detected grid size (reasonable limits for 2248 game)
        rows = max(2, min(10, rows))  # Reasonable range for 2248
        cols = max(2, min(10, cols))
        
        return (rows, cols)
    
    def _detect_grid_by_contours(self, board_image: np.ndarray) -> Tuple[int, int]:
        """
        Detect grid size using contour detection
        """
        # Convert to grayscale
        gray = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY) if len(board_image.shape) == 3 else board_image
        
        # Apply threshold to enhance grid lines
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Try to detect contours which might represent the grid cells
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours to find those that look like rectangles (potential cells)
        cell_contours = []
        for contour in contours:
            # Approximate the contour to a polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's roughly rectangular and has a reasonable size
            if len(approx) == 4:
                # Calculate the bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Only consider contours that are reasonably square-shaped
                if 0.5 <= aspect_ratio <= 2.0 and w > 10 and h > 10:
                    cell_contours.append((x, y, w, h))
        
        if len(cell_contours) >= 4:  # Need at least 4 cells to form a meaningful grid
            # Group contours by their row/column positions to count grid dimensions
            x_positions = sorted(set([x for x, y, w, h in cell_contours]))
            y_positions = sorted(set([y for x, y, w, h in cell_contours]))
            
            # Count distinct rows and columns by grouping close positions
            # This helps handle variations in exact positions
            rows = self._count_distinct_groups([y for x, y, w, h in cell_contours])
            cols = self._count_distinct_groups([x for x, y, w, h in cell_contours])
            
            return (rows, cols)
        
        return (0, 0)  # Detection failed
    
    def _detect_grid_by_pattern(self, board_image: np.ndarray) -> Tuple[int, int]:
        """
        Detect grid size by finding repeating patterns in the board image
        """
        gray = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY) if len(board_image.shape) == 3 else board_image
        
        # Look for regularly spaced patterns by analyzing the image histogram
        # Sum along the x and y axes to find regular intervals
        horizontal_sum = np.sum(gray, axis=1)  # Sum along x-axis (for each row)
        vertical_sum = np.sum(gray, axis=0)    # Sum along y-axis (for each column)
        
        # Find repeating patterns by looking for consistent intervals
        rows = self._find_regular_intervals(horizontal_sum)
        cols = self._find_regular_intervals(vertical_sum)
        
        return (rows, cols)
    
    def _find_regular_intervals(self, signal: np.ndarray) -> int:
        """
        Find the most likely number of intervals in a signal by looking for regular patterns
        """
        # Normalize the signal
        normalized_signal = (signal - np.min(signal)) / (np.max(signal) - np.min(signal) + 1e-6)
        
        # Look for the most common interval between local minima/maxima
        # This corresponds to the spacing between grid cells
        from scipy.signal import find_peaks
        
        # Find peaks in the signal
        peaks, _ = find_peaks(normalized_signal, height=0.3, distance=max(5, len(normalized_signal)//20))
        valleys, _ = find_peaks(-normalized_signal, height=-0.3, distance=max(5, len(normalized_signal)//20))
        
        # Combine peaks and valleys to get potential cell boundaries
        all_extrema = sorted(list(peaks) + list(valleys))
        
        if len(all_extrema) < 2:
            # If we can't find clear extrema, try a different approach
            # Look for areas where the signal changes significantly
            diff_signal = np.abs(np.diff(normalized_signal))
            peaks_diff, _ = find_peaks(diff_signal, height=0.2, distance=max(5, len(diff_signal)//20))
            
            if len(peaks_diff) >= 2:
                # Estimate number of cells based on number of transitions
                # Each transition typically indicates a boundary between cells
                return max(2, len(peaks_diff) - 1)
        
        # Calculate distances between extrema to find the most common spacing
        if len(all_extrema) >= 2:
            distances = []
            for i in range(1, len(all_extrema)):
                distances.append(all_extrema[i] - all_extrema[i-1])
            
            if distances:
                # The most common distance might indicate cell spacing
                # Count how many cells fit in the image based on typical spacing
                avg_distance = np.median(distances)
                if avg_distance > 0:
                    # Estimate number of cells by dividing image size by average distance
                    image_size = len(signal)
                    estimated_cells = int(image_size / avg_distance)
                    return max(2, min(estimated_cells, 10))
        
        # If pattern detection fails, return a default value
        return 5
    
    def _count_distinct_groups(self, positions, tolerance=None):
        """
        Count distinct groups of positions, considering nearby positions as the same group
        """
        if not positions:
            return 0
            
        sorted_pos = sorted(positions)
        
        # Calculate average distance to determine tolerance if not provided
        if tolerance is None:
            diffs = []
            for i in range(1, len(sorted_pos)):
                diffs.append(sorted_pos[i] - sorted_pos[i-1])
            tolerance = int(np.mean(diffs)) if diffs else 20
        
        groups = 0
        i = 0
        while i < len(sorted_pos):
            current_group_start = sorted_pos[i]
            groups += 1
            
            # Skip all positions that belong to this group
            while i < len(sorted_pos) and sorted_pos[i] - current_group_start < tolerance:
                i += 1
        
        return groups
    
    def _detect_grid_by_edges(self, board_image: np.ndarray) -> Tuple[int, int]:
        """
        Alternative method to detect grid size using edge detection
        """
        gray = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY) if len(board_image.shape) == 3 else board_image
        
        # Apply morphological operations to enhance grid lines
        # Use a cross-shaped kernel to enhance both horizontal and vertical lines
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        processed = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
        
        # Enhance the edges further with bilateral filter to preserve edges while reducing noise
        processed = cv2.bilateralFilter(processed, 9, 75, 75)
        
        # Calculate gradients to find edges
        grad_x = cv2.Sobel(processed, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(processed, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Threshold to get strong edges
        _, edges = cv2.threshold(np.uint8(gradient_magnitude), 30, 255, cv2.THRESH_BINARY)
        
        # Sum along axes to find potential grid lines
        vertical_sum = np.sum(edges, axis=0)  # Sum along y-axis to find vertical boundaries
        horizontal_sum = np.sum(edges, axis=1)  # Sum along x-axis to find horizontal boundaries
        
        # Find peaks in the sums (these correspond to grid lines)
        from scipy.signal import find_peaks
        
        # Use more robust peak detection with adaptive thresholds
        # Calculate adaptive thresholds based on the signal characteristics
        vert_max = np.max(vertical_sum)
        horiz_max = np.max(horizontal_sum)
        
        vert_threshold = max(vert_max * 0.15, np.mean(vertical_sum) * 2)  # Use both relative and absolute thresholds
        horiz_threshold = max(horiz_max * 0.15, np.mean(horizontal_sum) * 2)
        
        # Find peaks with more conservative distance settings to avoid missing peaks
        min_distance_x = max(10, edges.shape[1] // 15)  # At least 15 potential cells
        min_distance_y = max(10, edges.shape[0] // 15)
        
        # Find peaks in vertical sum (vertical grid lines)
        vertical_peaks, _ = find_peaks(vertical_sum, height=vert_threshold, distance=min_distance_x)
        # Find peaks in horizontal sum (horizontal grid lines)  
        horizontal_peaks, _ = find_peaks(horizontal_sum, height=horiz_threshold, distance=min_distance_y)
        
        # Estimate number of cells based on number of grid lines
        # Grid lines define the boundaries between cells
        rows = max(2, len(horizontal_peaks) - 1) if len(horizontal_peaks) > 1 else 0
        cols = max(2, len(vertical_peaks) - 1) if len(vertical_peaks) > 1 else 0
        
        # If we couldn't detect using this method, return 0s so other methods can be tried
        if rows < 2 or cols < 2:
            # Try a different approach - look for consistent spacing patterns
            rows = self._find_spacing_peaks(horizontal_sum)
            cols = self._find_spacing_peaks(vertical_sum)
        
        # Cap the values to reasonable ranges
        rows = min(10, max(2, rows))
        cols = min(10, max(2, cols))
        
        return (rows, cols)
    
    def _find_spacing_peaks(self, signal: np.ndarray) -> int:
        """
        Find the number of grid cells by looking for regular spacing patterns in the signal
        """
        # Normalize the signal
        normalized_signal = (signal - np.min(signal)) / (np.max(signal) - np.min(signal) + 1e-6)
        
        # Look for regularly spaced peaks that might indicate grid boundaries
        from scipy.signal import find_peaks
        
        # Try different thresholds to find the most consistent spacing
        best_count = 0
        best_threshold = 0.1
        
        for threshold in [0.1, 0.15, 0.2, 0.25, 0.3]:
            peaks, _ = find_peaks(normalized_signal, height=threshold, 
                                distance=max(5, len(normalized_signal)//12))
            
            if len(peaks) >= 2:
                # Check if the peaks are regularly spaced
                if len(peaks) > 1:
                    spacings = np.diff(peaks)
                    std_spacing = np.std(spacings)
                    mean_spacing = np.mean(spacings)
                    
                    # If spacings are relatively consistent (std < 30% of mean), this might be a good count
                    if mean_spacing > 0 and (std_spacing / mean_spacing) < 0.3:
                        cell_count = len(peaks) - 1
                        if cell_count > best_count and 2 <= cell_count <= 10:
                            best_count = cell_count
                            best_threshold = threshold
        
        if best_count >= 2:
            return best_count
        else:
            # If we can't find regular spacing, estimate based on average spacing
            # Look for the most common interval in the signal
            diff_signal = np.abs(np.diff(normalized_signal))
            peaks_diff, _ = find_peaks(diff_signal, height=0.1, 
                                     distance=max(5, len(diff_signal)//12))
            
            if len(peaks_diff) >= 2:
                # Estimate number of cells based on transition points
                return max(2, min(len(peaks_diff), 10))
        
        # If all else fails, return 0 (meaning detection failed for this method)
        return 0


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
        
        # Calculate cell dimensions dynamically based on the image and grid size
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


def get_game_state(grid_size: Tuple[int, int] = None) -> Tuple[List[List[int]], Tuple[int, int, int, int]]:
    """
    Main function to capture screen and extract game state
    If grid_size is None, it will be automatically detected from the image
    Returns a tuple of (board_state, board_region)
    """
    capturer = ScreenCapture()
    
    if not capturer.capture_screen():
        print("Failed to capture screen")
        return [], (0, 0, 0, 0)
    
    image = capturer.load_screenshot()
    if image is None:
        print("Failed to load screenshot")
        return [], (0, 0, 0, 0)
    
    # Detect the game board region
    board_region = capturer.detect_game_board(image)
    if board_region is None:
        print("Could not detect game board")
        return [], (0, 0, 0, 0)
    
    x, y, w, h = board_region
    board_image = image[y:y+h, x:x+w]
    
    # If grid size is not provided, detect it automatically
    if grid_size is None:
        detected_size = capturer.detect_grid_size(board_image)
        print(f"Automatically detected grid size: {detected_size[0]}x{detected_size[1]}")
        grid_size = detected_size
    
    # Extract numbers from the board
    recognizer = NumberRecognition()
    board_state = recognizer.extract_numbers_from_region(board_image, grid_size)
    
    return board_state, board_region