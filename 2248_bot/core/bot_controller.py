"""
Main bot controller for the 2248 game bot
"""

import time
import logging
from typing import List, Tuple, Optional
from game_io.screen_capture import get_game_state
from game_io.input_handler import execute_move
from logic.game_logic import GameLogic
from config.default_config import HEURISTIC_WEIGHTS, LOG_FILE, LOG_LEVEL, BOARD_SIZE, MOVE_DELAY


class BotController:
    def __init__(self, grid_size: Tuple[int, int] = None):
        self.grid_size = grid_size or (BOARD_SIZE['rows'], BOARD_SIZE['cols'])
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
        
        while True:
            try:
                # Capture current game state
                print("Capturing game state...")
                board = get_game_state(self.grid_size)
                
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
                # Note: We need the board region info to calculate screen coordinates
                # This is a simplified version - in practice, we'd pass actual board region
                board_region = (100, 100, 400, 400)  # Placeholder values
                success = execute_move(best_chain, board_region, self.grid_size)
                
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
    parser.add_argument("--rows", type=int, default=BOARD_SIZE['rows'], help="Number of rows in the game board")
    parser.add_argument("--cols", type=int, default=BOARD_SIZE['cols'], help="Number of columns in the game board")
    parser.add_argument("--no-gui", action="store_true", help="Run without GUI (headless mode)")
    
    args = parser.parse_args()
    
    grid_size = (args.rows, args.cols)
    bot = BotController(grid_size)
    
    print(f"Starting 2248 bot with grid size: {grid_size[0]}x{grid_size[1]}")
    
    bot.run()


if __name__ == "__main__":
    main()