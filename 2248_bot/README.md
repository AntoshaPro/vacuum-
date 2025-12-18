# 2248 Number Puzzle Bot

A bot designed to play the 2248 number puzzle game on mobile emulators (BlueStacks/LDPlayer) on macOS with M2 chip.

## Overview

This bot plays the 2248 Number Puzzle game by:
1. Capturing screenshots of the game board
2. Recognizing numbers on the board using OCR
3. Finding valid chains of identical numbers
4. Evaluating possible moves using heuristics
5. Executing moves through ADB commands

## Architecture

The bot is organized into several modules:

- `core/`: Main bot controller and orchestrator
- `logic/`: Game logic for finding chains and evaluating positions
- `game_io/`: Input/output operations (screen capture, input simulation)
- `config/`: Configuration settings
- `utils/`: Utility functions (logging, helpers)

## Requirements

- Python 3.7+
- Android Debug Bridge (ADB)
- Tesseract OCR
- OpenCV
- NumPy
- Pytesseract

## Installation

```bash
pip install -r requirements.txt
```

Make sure you have Tesseract installed on your system:
- On macOS: `brew install tesseract`

## Usage

1. Start your Android emulator (make sure it's accessible via ADB)
2. Launch the 2248 game
3. Run the bot:

```bash
python -m core.bot_controller --rows 6 --cols 6
```

Options:
- `--rows`: Number of rows in the game board (default: 6)
- `--cols`: Number of columns in the game board (default: 6)
- `--no-gui`: Run without GUI (headless mode)

## Configuration

Adjust the settings in `config/default_config.py` to match your environment:
- ADB device ID
- Screen capture settings
- Timing delays
- Heuristic weights
- Board size

## How It Works

1. **Screen Capture**: Uses ADB to take screenshots of the game
2. **Number Recognition**: Uses OCR to identify numbers in each cell
3. **Chain Detection**: Finds connected chains of identical numbers in 8 directions
4. **Move Evaluation**: Simulates each possible move and evaluates the resulting position
5. **Move Execution**: Sends touch/swipe commands to the emulator via ADB

## Heuristics

The bot uses several heuristics to evaluate board positions:
- Max tile value
- Number of empty cells
- Monotonicity (preference for ordered arrangements)
- Smoothness (penalty for large differences between adjacent tiles)
- Cluster penalty (penalty for clustering small values)

## Notes

- The bot assumes a 6x6 board by default, but this can be configured
- Performance depends on accurate OCR recognition
- Timing settings may need adjustment based on emulator performance
- The bot continues playing until manually stopped or the game ends