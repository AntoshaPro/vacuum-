"""
Test script to verify the 2248 bot components work together
"""

import unittest
from logic.game_logic import GameLogic
from game_io.screen_capture import get_game_state
from core.bot_controller import BotController


class TestGameLogic(unittest.TestCase):
    def setUp(self):
        self.game_logic = GameLogic()

    def test_find_chains(self):
        """Test finding chains in a sample board"""
        board = [
            [2, 2, 4, 4],
            [2, 0, 4, 8],
            [0, 0, 8, 8],
            [2, 2, 2, 2]
        ]
        
        chains = self.game_logic.find_all_chains(board)
        
        # Should find at least the horizontal 2-chain in first row and vertical 2-chains
        self.assertGreaterEqual(len(chains), 1)
        
        # Verify all chains have at least 2 cells
        for chain in chains:
            self.assertGreaterEqual(len(chain), 2)
    
    def test_simulate_merge(self):
        """Test merging a chain"""
        board = [
            [2, 2, 4, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        
        chain = [(0, 0), (0, 1)]  # Two 2's in first row
        new_board, score = self.game_logic.simulate_merge(board, chain)
        
        # After merging two 2's, we should get a 4 in the first position
        self.assertEqual(new_board[0][0], 4)
        self.assertEqual(new_board[0][1], 0)  # Second cell should be cleared
        self.assertEqual(score, 4)  # Score should be 2+2=4
    
    def test_evaluate_position(self):
        """Test position evaluation"""
        board = [
            [2, 4, 8, 16],
            [32, 64, 128, 256],
            [512, 1024, 2048, 0],
            [0, 0, 0, 0]
        ]
        
        score = self.game_logic.evaluate_position(board, {
            'max_tile': 1.0,
            'empty_cells': 2.0,
            'monotonicity': 1.0,
            'smoothness': 1.5,
            'cluster_penalty': 0.5
        })
        
        # Just verify it returns a number and doesn't crash
        self.assertIsInstance(score, (int, float))


class TestBotController(unittest.TestCase):
    def setUp(self):
        self.bot = BotController(grid_size=(4, 4))

    def test_select_best_chain(self):
        """Test selecting the best chain from multiple options"""
        board = [
            [2, 2, 4, 4],
            [2, 0, 4, 8],
            [0, 0, 8, 8],
            [2, 2, 2, 2]
        ]
        
        chains = [
            [(0, 0), (0, 1)],  # Horizontal 2-chain
            [(3, 0), (3, 1), (3, 2), (3, 3)],  # 4-chain in last row
        ]
        
        best_chain = self.bot.select_best_chain(board, chains)
        
        # Should return one of the chains
        self.assertIsNotNone(best_chain)
        self.assertIn(best_chain, chains)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    # For quick functionality check
    print("Testing basic functionality...")
    
    # Test game logic
    logic = GameLogic()
    
    # Simple test board
    test_board = [
        [2, 2, 0, 0],
        [4, 4, 4, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    
    print("Original board:")
    for row in test_board:
        print(row)
    
    # Find chains
    chains = logic.find_all_chains(test_board)
    print(f"\nFound {len(chains)} chains:")
    for i, chain in enumerate(chains):
        print(f"Chain {i+1}: {chain}")
    
    # Test the first chain
    if chains:
        new_board, score = logic.simulate_merge(test_board, chains[0])
        print(f"\nAfter merging first chain, board becomes:")
        for row in new_board:
            print(row)
        print(f"Score gained: {score}")
    
    # Run full unit tests
    print("\nRunning unit tests...")
    run_tests()