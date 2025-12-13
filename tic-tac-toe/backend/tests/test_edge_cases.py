import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import TicTacToeGame, GameStatus
from agents import AgentFactory, AIAgent
from ollama_client import OllamaClient

class TestEdgeCases(unittest.TestCase):
    
    def setUp(self):
        self.game = TicTacToeGame()
    
    def test_all_win_conditions(self):
        """Test all possible win conditions"""
        # Test all 8 win combinations
        
        # Row wins
        for row in range(3):
            game = TicTacToeGame()
            start_pos = row * 3
            # Use distractions that don't interfere with winning row
            if row == 0:  # Top row (0,1,2)
                distractions = [8, 7]
            elif row == 1:  # Middle row (3,4,5)
                distractions = [8, 7]
            else:  # Bottom row (6,7,8)
                distractions = [0, 1]
            
            game.make_move(start_pos)     # X
            game.make_move(distractions[0])  # O (distraction)
            game.make_move(start_pos + 1) # X
            game.make_move(distractions[1])  # O (distraction)
            result = game.make_move(start_pos + 2) # X wins
            
            self.assertTrue(result)
            self.assertEqual(game.status, GameStatus.WIN)
            self.assertEqual(game.winner, "X")
        
        # Column wins
        for col in range(3):
            game = TicTacToeGame()
            # Use distractions that don't interfere with winning column
            if col == 0:  # Left column (0,3,6)
                distractions = [1, 2]
            elif col == 1:  # Middle column (1,4,7)
                distractions = [0, 2]
            else:  # Right column (2,5,8)
                distractions = [0, 1]
            
            game.make_move(col)           # X
            game.make_move(distractions[0])  # O (distraction)
            game.make_move(col + 3)       # X
            game.make_move(distractions[1])  # O (distraction)
            result = game.make_move(col + 6) # X wins
            
            self.assertTrue(result)
            self.assertEqual(game.status, GameStatus.WIN)
            self.assertEqual(game.winner, "X")
        
        # Diagonal wins
        # Top-left to bottom-right
        game = TicTacToeGame()
        game.make_move(0)  # X
        game.make_move(1)  # O
        game.make_move(4)  # X
        game.make_move(2)  # O
        result = game.make_move(8)  # X wins
        self.assertTrue(result)
        self.assertEqual(game.status, GameStatus.WIN)
        self.assertEqual(game.winner, "X")
        
        # Top-right to bottom-left
        game = TicTacToeGame()
        game.make_move(2)  # X
        game.make_move(0)  # O
        game.make_move(4)  # X
        game.make_move(1)  # O
        result = game.make_move(6)  # X wins
        self.assertTrue(result)
        self.assertEqual(game.status, GameStatus.WIN)
        self.assertEqual(game.winner, "X")
    
    def test_o_wins(self):
        """Test O winning scenarios"""
        game = TicTacToeGame()
        # Alternating moves with O winning
        game.make_move(0)  # X
        game.make_move(1)  # O
        game.make_move(6)  # X
        game.make_move(4)  # O
        game.make_move(2)  # X
        result = game.make_move(7)  # O wins in middle column
        
        self.assertTrue(result)
        self.assertEqual(game.status, GameStatus.WIN)
        self.assertEqual(game.winner, "O")
    
    def test_multiple_draw_scenarios(self):
        """Test various draw scenarios"""
        draw_scenarios = [
            [0, 1, 2, 4, 3, 5, 7, 6, 8],  # Verified draw scenario
            [4, 0, 2, 1, 3, 5, 7, 6, 8],  # Center-first draw
            [1, 0, 2, 4, 3, 5, 7, 6, 8],  # Edge-first draw
        ]
        
        for moves in draw_scenarios:
            game = TicTacToeGame()
            for move in moves:
                if game.status == GameStatus.IN_PROGRESS:
                    result = game.make_move(move)
                    self.assertTrue(result, f"Move {move} failed in scenario {moves}")
            
            self.assertEqual(game.status, GameStatus.DRAW, f"Expected draw but got {game.status} for scenario {moves}")
            self.assertIsNone(game.winner)
    
    def test_immediate_win_prevention(self):
        """Test that game ends immediately when someone wins"""
        game = TicTacToeGame()
        
        # Set up X about to win
        game.make_move(0)  # X
        game.make_move(3)  # O
        game.make_move(1)  # X
        game.make_move(4)  # O
        
        # X makes winning move
        result = game.make_move(2)  # X wins
        
        self.assertTrue(result)
        self.assertEqual(game.status, GameStatus.WIN)
        self.assertEqual(game.winner, "X")
        
        # Try to make another move after game ends
        result = game.make_move(5)
        self.assertFalse(result)  # Should not allow moves after win
    
    def test_board_boundary_conditions(self):
        """Test board edge cases"""
        # Test all valid positions initially
        for pos in range(9):
            game = TicTacToeGame()
            self.assertTrue(game.is_valid_move(pos))
        
        # Test boundary positions
        boundary_positions = [-1, 9, 10, 100]
        for pos in boundary_positions:
            self.assertFalse(self.game.is_valid_move(pos))
            result = self.game.make_move(pos)
            self.assertFalse(result)
    
    def test_full_board_sequence(self):
        """Test playing until board is full or game ends"""
        moves = []
        game = TicTacToeGame()
        
        # Fill board sequentially
        for i in range(9):
            if game.status == GameStatus.IN_PROGRESS:
                result = game.make_move(i)
                if result:
                    moves.append(i)
        
        # Should make at least 5 moves (minimum for win) and at most 9
        self.assertGreaterEqual(len(moves), 5)
        self.assertLessEqual(len(moves), 9)
        self.assertTrue(all(0 <= pos <= 8 for pos in moves))
    
    @patch('ollama_client.subprocess.run')
    def test_ai_agent_edge_cases(self, mock_run):
        """Test AI agent with various response formats"""
        # Test with different response formats
        test_cases = [
            ("4", 4),                    # Simple number
            ("I choose 7", 7),           # Number in text
            ("Position 5 is best", 5),   # Number with text
            ("42", 4),                   # First digit only
            ("no numbers here", None),   # No numbers
            ("", None),                  # Empty response
        ]
        
        for response_text, expected_move in test_cases:
            with self.subTest(response=response_text):
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = response_text
                
                client = OllamaClient('test-model')
                result = client.get_move([' '] * 9, 'X')
                self.assertEqual(result, expected_move)
    
    def test_agent_factory_edge_cases(self):
        """Test AgentFactory with edge cases"""
        # Test case sensitivity
        with self.assertRaises(ValueError):
            AgentFactory.create_agent('Human')
        
        with self.assertRaises(ValueError):
            AgentFactory.create_agent('AI')
        
        with self.assertRaises(ValueError):
            AgentFactory.create_agent('HUMAN')
        
        # Test empty string
        with self.assertRaises(ValueError):
            AgentFactory.create_agent('')
        
        # Test None - skip as type checking happens at runtime
        # AgentFactory.create_agent(None) would cause TypeError at runtime
    
    def test_game_state_persistence(self):
        """Test game state consistency across operations"""
        # Make some moves
        self.game.make_move(0)
        self.game.make_move(4)
        self.game.make_move(1)
        
        # Get state
        state1 = self.game.get_state()
        
        # Make more moves
        self.game.make_move(5)
        state2 = self.game.get_state()
        
        # States should be different
        self.assertNotEqual(state1['board'], state2['board'])
        self.assertNotEqual(state1['current_player'], state2['current_player'])
        
        # But status should be consistent (both in progress)
        self.assertEqual(state1['status'], state2['status'])
    
    def test_multiple_game_instances(self):
        """Test multiple game instances don't interfere"""
        game1 = TicTacToeGame()
        game2 = TicTacToeGame()
        
        # Make different moves in each game
        game1.make_move(0)
        game2.make_move(4)
        
        # Games should have different states
        self.assertNotEqual(game1.board, game2.board)
        self.assertEqual(game1.board[0], "X")
        self.assertEqual(game1.board[4], " ")
        self.assertEqual(game2.board[0], " ")
        self.assertEqual(game2.board[4], "X")
    
    def test_reset_after_complex_game(self):
        """Test reset after complex game scenario"""
        # Play a complex game
        moves = [0, 4, 1, 5, 2, 6, 3, 7, 8]
        for move in moves:
            if self.game.status == GameStatus.IN_PROGRESS:
                self.game.make_move(move)
        
        # Reset the game
        self.game.reset()
        
        # Verify reset state
        self.assertEqual(self.game.board, [" "] * 9)
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.status, GameStatus.IN_PROGRESS)
        self.assertIsNone(self.game.winner)
        
        # Game should be playable again
        self.assertTrue(self.game.make_move(0))
        self.assertEqual(self.game.board[0], "X")

if __name__ == '__main__':
    unittest.main()