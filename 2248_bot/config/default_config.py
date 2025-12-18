"""
Configuration settings for the 2248 bot
"""

# Game board settings - no hard-coded grid dimensions
# Grid detection is done automatically from the screenshot

# ADB/emulator settings
ADB_DEVICE = "emulator-5554"  # Default emulator device ID
SCREENSHOT_PATH = "/tmp/screenshot.png"

# Timing settings
MOVE_DELAY = 0.5  # Delay between moves in seconds
ANIMATION_WAIT_TIME = 1.0  # Time to wait for animations to complete

# Vision settings
OCR_THRESHOLD = 0.8  # Minimum confidence for number recognition
TEMPLATE_MATCH_THRESHOLD = 0.85  # Threshold for template matching

# Heuristic weights
HEURISTIC_WEIGHTS = {
    'max_tile': 1.0,
    'empty_cells': 2.0,
    'monotonicity': 1.0,
    'smoothness': 1.5,
    'cluster_penalty': 0.5
}

# Logging settings
LOG_FILE = "2248_bot.log"
LOG_LEVEL = "INFO"