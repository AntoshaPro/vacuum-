# Automatic Field Size Detection Feature

## Overview
This document describes the automatic field size detection feature implemented in the 2248 bot. The bot can now automatically determine the grid dimensions of the game board instead of requiring hardcoded values.

## Key Improvements

### 1. Enhanced Screen Capture Module
- **Board Region Detection**: Uses edge detection and Hough transforms to identify the game board area within screenshots
- **Grid Size Detection**: Implements multiple algorithms to determine the number of rows and columns:
  - Contour analysis to find rectangular cell patterns
  - Edge-based detection with enhanced morphological operations
  - Pattern-based detection analyzing repeating elements
  - Spacing analysis to find regularly spaced elements
- **No Hardcoded Values**: Completely removes any hard-coded grid dimensions or tile sizes

### 2. Updated Function Signatures
- `get_game_state()` now returns both the board state and the board region
- The bot controller uses the detected board region for accurate coordinate mapping
- Default behavior is now auto-detection unless specific dimensions are provided

### 3. Robust Fallback Mechanisms
- Multiple detection algorithms ensure reliable results across different game layouts:
  - Primary: Contour-based detection for rectangular patterns
  - Secondary: Enhanced edge detection with cross-shaped kernels and bilateral filtering
  - Tertiary: Pattern-based detection using signal analysis
  - Quaternary: Spacing consistency checks with adaptive thresholds
- Tolerance-based grouping handles variations in cell positioning
- Reasonable limits prevent detection of invalid grid sizes

## Technical Implementation

### Board Region Detection
```python
def detect_game_board(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    # Uses edge detection and Hough transforms to find grid boundaries
    # Falls back to estimation if line detection fails
```

### Grid Size Detection
```python
def detect_grid_size(self, board_image: np.ndarray) -> Tuple[int, int]:
    # Primary method: contour analysis for rectangular patterns
    # Secondary method: enhanced edge detection with cross kernels
    # Tertiary method: pattern-based detection for repeating elements
    # Quaternary method: spacing consistency analysis
```

### Integration with Main Loop
- First run: detects grid size automatically
- Subsequent runs: uses detected size for consistency
- Provides command-line override option for specific dimensions

## Benefits

1. **Universal Compatibility**: Works with different 2248 game variants and board sizes
2. **No Hardcoding**: Eliminates need to specify board dimensions in configuration
3. **Robust Detection**: Multiple algorithms ensure reliable results across various resolutions and layouts
4. **Resolution Independence**: Automatically adapts to different emulator resolutions and aspect ratios
5. **Backward Compatibility**: Still accepts manual grid size specification

## Usage

### Auto-detection (default):
```bash
python -m core.bot_controller
```

### Manual specification (still supported):
```bash
python -m core.bot_controller --rows 5 --cols 5
```

## Files Modified

- `game_io/screen_capture.py`: Added detection algorithms and updated function signatures
- `core/bot_controller.py`: Updated to handle auto-detected dimensions and board regions
- `config/default_config.py`: Removed hardcoded board size configuration
- `README.md`: Updated usage instructions and feature descriptions
- `requirements.txt`: Added scipy dependency for peak detection

## Testing

The implementation includes:
- Unit tests for detection algorithms
- Integration tests with the main bot logic
- A demonstration script (`demo_autodetect.py`) to showcase the functionality

## Algorithm Details

### Contour-based Detection
1. Applies threshold to enhance grid lines
2. Finds contours that match rectangular patterns
3. Groups contour positions to count distinct rows/columns

### Enhanced Edge-based Detection
1. Uses cross-shaped morphological kernels to enhance both horizontal and vertical lines
2. Applies bilateral filtering to preserve edges while reducing noise
3. Calculates gradients to find potential grid lines
4. Sums gradients along X and Y axes
5. Finds peaks in the sums to identify grid boundaries
6. Estimates grid size based on number of detected boundaries

### Pattern-based Detection
1. Analyzes repeating patterns by summing along axes
2. Uses peak detection to identify regularly spaced elements
3. Validates spacing consistency to confirm grid structure

### Spacing Analysis
1. Applies adaptive thresholds to find the most consistent spacing
2. Checks if spacings are relatively consistent (std < 30% of mean)
3. Estimates number of cells based on transition points if regular spacing fails

The system is designed to work with the existing OCR and game logic components while adding the capability to automatically adapt to different board sizes without any hard-coded values.