"""
Logging utilities for the 2248 bot
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from config.default_config import LOG_FILE, LOG_LEVEL


def setup_logger(name: str, log_file: str = None, level: str = None) -> logging.Logger:
    """
    Function to setup a logger with file and console handlers
    """
    log_file = log_file or LOG_FILE
    level = level or LOG_LEVEL
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_board_state(logger: logging.Logger, board: list, move_info: dict = None):
    """
    Log the current board state in a readable format
    """
    logger.info("Current Board State:")
    for i, row in enumerate(board):
        logger.info(f"Row {i}: {row}")
    
    if move_info:
        logger.info(f"Selected Chain: {move_info.get('selected_chain', [])}")
        logger.info(f"Chain Length: {len(move_info.get('selected_chain', []))}")


def log_performance_metrics(logger: logging.Logger, metrics: dict):
    """
    Log performance metrics like move time, evaluation time, etc.
    """
    logger.info("Performance Metrics:")
    for key, value in metrics.items():
        logger.info(f"{key}: {value}")