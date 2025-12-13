import unittest
from game import TicTacToeGame, GameStatus

class TestTicTacToeGame(unittest.TestCase):
    
    def setUp(self):
        self.game = TicTacToeGame()
    
    def test_initial_state(self):
        """Test game initializes correctly"""
        self.assertEqual(self.game.board, [" "] * 9)
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.status, GameStatus.IN_PROGRESS)
        self.assertIsNone(self.game.winner)
    
    def test_valid_move_detection(self):
        """Test valid move detection"""
        self.assertTrue(self.game.is_valid_move(0))
        self.assertTrue(self.game.is_valid_move(8))
        self.assertFalse(self.game.is_valid_move(-1))
        self.assertFalse(self.game.is_valid_move(9))
        # Test after making a move
        self.game.make_move(0)
        self.assertFalse(self.game.is_valid_move(0))  # Can't move on occupied space
    
    def test_invalid_move_after_placement(self):
        """Test invalid move after placing piece"""
        self.game.make_move(0)
        self.assertFalse(self.game.is_valid_move(0))  # Can't move on occupied space
    
    def test_simple_move(self):
        """Test making a simple move"""
        result = self.game.make_move(0)
        self.assertTrue(result)
        self.assertEqual(self.game.board[0], "X")
        self.assertEqual(self.game.current_player, "O")
    
    def test_win_detection_row(self):
        """Test win detection in rows"""
        # X wins in top row
        self.game.make_move(0)  # X
        self.game.make_move(3)  # O
        self.game.make_move(1)  # X
        self.game.make_move(4)  # O
        result = self.game.make_move(2)  # X wins
        
        self.assertTrue(result)
        self.assertEqual(self.game.status, GameStatus.WIN)
        self.assertEqual(self.game.winner, "X")
    
    def test_win_detection_column(self):
        """Test win detection in columns"""
        # O wins in left column
        self.game.make_move(1)  # X
        self.game.make_move(0)  # O
        self.game.make_move(2)  # X
        self.game.make_move(3)  # O
        self.game.make_move(5)  # X
        result = self.game.make_move(6)  # O wins
        
        self.assertTrue(result)
        self.assertEqual(self.game.status, GameStatus.WIN)
        self.assertEqual(self.game.winner, "O")
    
    def test_win_detection_diagonal(self):
        """Test win detection in diagonals"""
        # X wins in diagonal
        self.game.make_move(0)  # X
        self.game.make_move(1)  # O
        self.game.make_move(4)  # X
        self.game.make_move(2)  # O
        result = self.game.make_move(8)  # X wins
        
        self.assertTrue(result)
        self.assertEqual(self.game.status, GameStatus.WIN)
        self.assertEqual(self.game.winner, "X")
    
    def test_draw_detection(self):
        """Test draw detection"""
        # Create a draw scenario
        moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]  # Results in draw
        for move in moves:
            self.game.make_move(move)
        
        self.assertEqual(self.game.status, GameStatus.DRAW)
        self.assertIsNone(self.game.winner)
    
    def test_invalid_move_rejection(self):
        """Test that invalid moves are rejected"""
        # Try to make move out of bounds
        result = self.game.make_move(9)
        self.assertFalse(result)
        
        # Try to make move on occupied space
        self.game.make_move(0)
        result = self.game.make_move(0)
        self.assertFalse(result)
        
        # Try to make move after game ends
        # Force a win first
        for move in [0, 3, 1, 4, 2]:  # X wins
            self.game.make_move(move)
        result = self.game.make_move(5)
        self.assertFalse(result)
    
    def test_get_empty_positions(self):
        """Test getting empty positions"""
        self.assertEqual(self.game.get_empty_positions(), list(range(9)))
        
        self.game.make_move(0)
        self.game.make_move(4)
        expected = [1, 2, 3, 5, 6, 7, 8]
        self.assertEqual(self.game.get_empty_positions(), expected)
    
    def test_reset_functionality(self):
        """Test game reset functionality"""
        # Make some moves
        self.game.make_move(0)
        self.game.make_move(4)
        
        # Reset game
        self.game.reset()
        
        # Check reset state
        self.assertEqual(self.game.board, [" "] * 9)
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.status, GameStatus.IN_PROGRESS)
        self.assertIsNone(self.game.winner)
    
    def test_get_state(self):
        """Test getting game state"""
        self.game.make_move(0)
        state = self.game.get_state()
        
        expected_board = ["X", " ", " ", " ", " ", " ", " ", " ", " "]
        self.assertEqual(state['board'], expected_board)
        self.assertEqual(state['current_player'], "O")
        self.assertEqual(state['status'], "in_progress")
        self.assertIsNone(state['winner'])
    
    def test_alternating_players(self):
        """Test that players alternate correctly"""
        initial_player = self.game.current_player
        
        self.game.make_move(0)
        self.assertNotEqual(self.game.current_player, initial_player)
        
        self.game.make_move(1)
        self.assertEqual(self.game.current_player, initial_player)

if __name__ == '__main__':
    unittest.main()