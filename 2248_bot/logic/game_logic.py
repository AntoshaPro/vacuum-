"""
Game logic for 2248 puzzle: finding chains, merging, and evaluation
"""

import numpy as np
from typing import List, Tuple, Optional, Set


class GameLogic:
    def __init__(self):
        # 8 directions: up, down, left, right, and 4 diagonals
        self.directions = [
            (-1, 0),  # Up
            (1, 0),   # Down
            (0, -1),  # Left
            (0, 1),   # Right
            (-1, -1), # Up-left
            (-1, 1),  # Up-right
            (1, -1),  # Down-left
            (1, 1)    # Down-right
        ]

    def find_all_chains(self, board: List[List[int]]) -> List[List[Tuple[int, int]]]:
        """
        Find all valid chains of identical numbers on the board.
        Each chain consists of connected cells with the same number (min 2 cells).
        """
        rows, cols = len(board), len(board[0])
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        all_chains = []

        for r in range(rows):
            for c in range(cols):
                if board[r][c] != 0 and not visited[r][c]:
                    chain = self._find_chain_dfs(board, r, c, visited)
                    if len(chain) >= 2:  # Only consider chains with 2 or more cells
                        all_chains.append(chain)

        return all_chains

    def _find_chain_dfs(self, board: List[List[int]], start_r: int, start_c: int, 
                        visited: List[List[bool]], chain: Optional[List[Tuple[int, int]]] = None) -> List[Tuple[int, int]]:
        """Find a connected chain starting from (start_r, start_c) using DFS."""
        if chain is None:
            chain = []
        
        rows, cols = len(board), len(board[0])
        num_to_match = board[start_r][start_c]
        
        if visited[start_r][start_c] or board[start_r][start_c] == 0 or board[start_r][start_c] != num_to_match:
            return chain
        
        visited[start_r][start_c] = True
        chain.append((start_r, start_c))
        
        # Explore all 8 directions
        for dr, dc in self.directions:
            nr, nc = start_r + dr, start_c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not visited[nr][nc] and board[nr][nc] == num_to_match:
                    self._find_chain_dfs(board, nr, nc, visited, chain)
        
        return chain

    def simulate_merge(self, board: List[List[int]], chain: List[Tuple[int, int]]) -> Tuple[List[List[int]], int]:
        """
        Simulate merging a chain and return the resulting board and score gained.
        """
        new_board = [row[:] for row in board]  # Deep copy the board
        score_gained = 0
        
        if len(chain) < 2:
            return new_board, 0
        
        # Calculate merged value: 2^(log2(original_value) + len(chain))
        original_value = board[chain[0][0]][chain[0][1]]
        if original_value == 0:
            return new_board, 0
            
        # Calculate how many times we need to double based on chain length
        merged_value = original_value * (2 ** (len(chain) - 1))
        
        # Clear the chain positions
        for r, c in chain:
            new_board[r][c] = 0
        
        # Place the merged tile (for now, just place it at the first position)
        new_board[chain[0][0]][chain[0][1]] = merged_value
        
        # Calculate score (sum of all values in the chain)
        score_gained = original_value * len(chain)
        
        return new_board, score_gained

    def evaluate_position(self, board: List[List[int]], weights: dict) -> float:
        """
        Evaluate the board position using heuristics.
        """
        score = 0.0
        rows, cols = len(board), len(board[0])
        
        # Count occupied cells
        occupied_count = sum(1 for r in range(rows) for c in range(cols) if board[r][c] != 0)
        empty_count = rows * cols - occupied_count
        
        # Max tile value
        max_tile = max(max(row) for row in board) if any(max(row) for row in board) else 0
        
        # Apply heuristic components
        score += weights['max_tile'] * max_tile
        score += weights['empty_cells'] * empty_count
        score += weights['monotonicity'] * self._calculate_monotonicity(board)
        score += weights['smoothness'] * self._calculate_smoothness(board)
        score -= weights['cluster_penalty'] * self._calculate_cluster_penalty(board)
        
        return score

    def _calculate_monotonicity(self, board: List[List[int]]) -> float:
        """Calculate monotonicity of the board (prefer tiles arranged in increasing/decreasing order)."""
        rows, cols = len(board), len(board[0])
        total_monotonicity = 0
        
        # Check rows (left to right)
        for r in range(rows):
            for c in range(cols - 1):
                if board[r][c] != 0 and board[r][c+1] != 0:
                    if board[r][c] >= board[r][c+1]:
                        total_monotonicity += 1
                    else:
                        total_monotonicity -= 1
        
        # Check columns (top to bottom)
        for c in range(cols):
            for r in range(rows - 1):
                if board[r][c] != 0 and board[r+1][c] != 0:
                    if board[r][c] >= board[r+1][c]:
                        total_monotonicity += 1
                    else:
                        total_monotonicity -= 1
        
        return total_monotonicity

    def _calculate_smoothness(self, board: List[List[int]]) -> float:
        """Calculate smoothness (penalize large differences between adjacent tiles)."""
        rows, cols = len(board), len(board[0])
        smoothness = 0
        
        for r in range(rows):
            for c in range(cols):
                if board[r][c] != 0:
                    # Check adjacent cells
                    for dr, dc in [(0, 1), (1, 0)]:  # Only check right and down to avoid double counting
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != 0:
                            diff = abs(board[r][c] - board[nr][nc])
                            smoothness -= diff
        
        return smoothness

    def _calculate_cluster_penalty(self, board: List[List[int]]) -> float:
        """Calculate penalty for clustering of small values."""
        rows, cols = len(board), len(board[0])
        penalty = 0
        
        for r in range(rows):
            for c in range(cols):
                if board[r][c] != 0:
                    # Check adjacent cells for similar small values
                    for dr, dc in self.directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != 0:
                            # Higher penalty for clustering of small values
                            if board[r][c] < 32 and board[nr][nc] < 32:
                                penalty += 1
        
        return penalty