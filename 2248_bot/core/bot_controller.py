"""
Main bot controller for the 2248 game bot
"""

import time
import logging
from typing import List, Tuple, Optional
from game_io.screen_capture import get_game_state
from game_io.input_handler import execute_move
from logic.game_logic import GameLogic
from config.default_config import HEURISTIC_WEIGHTS, LOG_FILE, LOG_LEVEL, MOVE_DELAY


class BotController:
    def __init__(self, grid_size: Tuple[int, int] = None):
        self.grid_size = grid_size  # Allow None for auto-detection
        self.game_logic = GameLogic()
        self.move_history = []
        self.score_history = []
        
        # Setup logging
        logging.basicConfig(
            filename=LOG_FILE,
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """
        Main loop of the bot: capture state, find best move, execute move, repeat
        """
        print("Starting 2248 bot...")
        self.logger.info("Starting 2248 bot")
        
        # Track if we've detected the grid size
        detected_grid_size = None
        board_region = None  # Track the board region for move execution
        
        while True:
            try:
                # Capture current game state
                print("Capturing game state...")
                
                # If we haven't detected the grid size yet, pass None to auto-detect
                # Otherwise, use the previously detected size for consistency
                capture_grid_size = detected_grid_size if detected_grid_size else self.grid_size
                board, detected_region = get_game_state(capture_grid_size)
                
                # Update the board region for move execution
                if detected_region and detected_region != (0, 0, 0, 0):
                    board_region = detected_region
                
                # If we're using auto-detection and haven't detected the size yet, 
                # the get_game_state function would have determined the size
                if self.grid_size is None and board and not detected_grid_size:
                    # Confirm the grid size based on the actual board dimensions received
                    detected_grid_size = (len(board), len(board[0]) if board else 0)
                    print(f"Confirmed grid size: {detected_grid_size[0]}x{detected_grid_size[1]}")
                
                if not board or len(board) == 0:
                    print("Failed to get valid game state, retrying...")
                    time.sleep(MOVE_DELAY * 2)
                    continue
                
                print(f"Current board state: {board}")
                self.logger.info(f"Current board state: {board}")
                
                # Find all possible chains
                print("Finding all possible chains...")
                chains = self.game_logic.find_all_chains(board)
                
                if not chains:
                    print("No valid chains found! Game might be over.")
                    self.logger.warning("No valid chains found, game might be over")
                    time.sleep(MOVE_DELAY * 5)  # Wait longer before trying again
                    continue
                
                print(f"Found {len(chains)} possible chains")
                
                # Evaluate each chain and select the best one
                best_chain = self.select_best_chain(board, chains)
                
                if best_chain is None:
                    print("Could not select a best chain!")
                    time.sleep(MOVE_DELAY)
                    continue
                
                print(f"Selected chain: {best_chain}")
                
                # Record the move
                self.move_history.append({
                    'board': [row[:] for row in board],  # Deep copy
                    'selected_chain': best_chain[:]
                })
                
                # Execute the move
                # Use the detected board region and grid size for coordinate calculation
                # Fallback to a reasonable default if detection failed
                effective_grid_size = detected_grid_size or self.grid_size or (5, 5)
                success = execute_move(best_chain, board_region, effective_grid_size)
                
                if success:
                    print("Move executed successfully")
                    self.logger.info(f"Move executed successfully for chain: {best_chain}")
                else:
                    print("Failed to execute move")
                    self.logger.error(f"Failed to execute move for chain: {best_chain}")
                
                # Wait before next move to allow animations to complete
                time.sleep(MOVE_DELAY)
                
            except KeyboardInterrupt:
                print("\nBot stopped by user")
                self.logger.info("Bot stopped by user")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(MOVE_DELAY * 2)
    
    def select_best_chain(self, board: List[List[int]], chains: List[List[Tuple[int, int]]]) -> Optional[List[Tuple[int, int]]]:
        """
        Select the best chain based on position evaluation after simulation
        """
        best_chain = None
        best_score = float('-inf')
        
        for chain in chains:
            # Simulate the merge for this chain
            simulated_board, score_gain = self.game_logic.simulate_merge(board, chain)
            
            # Evaluate the resulting position
            position_score = self.game_logic.evaluate_position(simulated_board, HEURISTIC_WEIGHTS)
            
            # Add the score gain as a bonus
            total_score = position_score + score_gain * 0.1  # Weight the immediate gain less than positional score
            
            if total_score > best_score:
                best_score = total_score
                best_chain = chain
        
        return best_chain
    
    def get_current_score(self) -> int:
        """
        Calculate the current score based on the board state
        """
        # This is a simplified calculation - the actual scoring might be different
        # depending on how the game calculates scores
        if len(self.move_history) > 0:
            # Get the last recorded board state to estimate current score
            last_move = self.move_history[-1]
            board = last_move['board']
            score = sum(sum(row) for row in board if row)
            return score
        return 0


def main():
    """
    Entry point for the 2248 bot
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="2248 Game Bot")
    parser.add_argument("--rows", type=int, help="Number of rows in the game board (default: auto-detect)")
    parser.add_argument("--cols", type=int, help="Number of columns in the game board (default: auto-detect)")
    parser.add_argument("--no-gui", action="store_true", help="Run without GUI (headless mode)")
    
    args = parser.parse_args()
    
    # Use provided grid size or None for auto-detection
    grid_size = (args.rows, args.cols) if args.rows and args.cols else None
    bot = BotController(grid_size)
    
    if grid_size:
        print(f"Starting 2248 bot with grid size: {grid_size[0]}x{grid_size[1]}")
    else:
        print("Starting 2248 bot with automatic grid size detection")
    
    bot.run()


if __name__ == "__main__":
    main()