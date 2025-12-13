import unittest
from pydantic import ValidationError
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewGameRequest, MoveRequest, GameState

class TestModels(unittest.TestCase):
    
    def test_new_game_request_valid(self):
        """Test valid NewGameRequest creation"""
        # Human vs Human
        request = NewGameRequest(
            player_x_type="human",
            player_o_type="human"
        )
        self.assertEqual(request.player_x_type, "human")
        self.assertEqual(request.player_o_type, "human")
        self.assertIsNone(request.player_x_model)
        self.assertIsNone(request.player_o_model)
        
        # AI vs AI with models
        request = NewGameRequest(
            player_x_type="ai",
            player_o_type="ai",
            player_x_model="llama3.2:1b",
            player_o_model="qwen3:4b"
        )
        self.assertEqual(request.player_x_type, "ai")
        self.assertEqual(request.player_o_type, "ai")
        self.assertEqual(request.player_x_model, "llama3.2:1b")
        self.assertEqual(request.player_o_model, "qwen3:4b")
        
        # Human vs AI
        request = NewGameRequest(
            player_x_type="human",
            player_o_type="ai",
            player_o_model="granite4:3b"
        )
        self.assertEqual(request.player_x_type, "human")
        self.assertEqual(request.player_o_type, "ai")
        self.assertIsNone(request.player_x_model)
        self.assertEqual(request.player_o_model, "granite4:3b")
    
    def test_new_game_request_serialization(self):
        """Test NewGameRequest serialization to dict"""
        request = NewGameRequest(
            player_x_type="ai",
            player_o_type="human",
            player_x_model="phi4-mini-reasoning:latest"
        )
        
        data = request.model_dump()
        expected = {
            "player_x_type": "ai",
            "player_o_type": "human", 
            "player_x_model": "phi4-mini-reasoning:latest",
            "player_o_model": None
        }
        self.assertEqual(data, expected)
    
    def test_move_request_valid(self):
        """Test valid MoveRequest creation"""
        request = MoveRequest(position=4)
        self.assertEqual(request.position, 4)
        
        # Test all valid positions
        for pos in range(9):
            request = MoveRequest(position=pos)
            self.assertEqual(request.position, pos)
    
    def test_move_request_serialization(self):
        """Test MoveRequest serialization to dict"""
        request = MoveRequest(position=7)
        data = request.model_dump()
        self.assertEqual(data, {"position": 7})
    
    def test_game_state_valid(self):
        """Test valid GameState creation"""
        state = GameState(
            board=["X", "O", " ", " ", "X", " ", " ", " ", "O"],
            current_player="X",
            status="in_progress",
            winner=None,
            player_x_type="human",
            player_o_type="ai",
            player_x_model=None,
            player_o_model="llama3.2:1b"
        )
        
        self.assertEqual(state.board[0], "X")
        self.assertEqual(state.board[1], "O")
        self.assertEqual(state.current_player, "X")
        self.assertEqual(state.status, "in_progress")
        self.assertIsNone(state.winner)
        self.assertEqual(state.player_x_type, "human")
        self.assertEqual(state.player_o_type, "ai")
        self.assertIsNone(state.player_x_model)
        self.assertEqual(state.player_o_model, "llama3.2:1b")
    
    def test_game_state_win(self):
        """Test GameState with win condition"""
        state = GameState(
            board=["X", "X", "X", "O", "O", " ", " ", " ", " "],
            current_player="O",
            status="win",
            winner="X",
            player_x_type="human",
            player_o_type="human",
            player_x_model=None,
            player_o_model=None
        )
        
        self.assertEqual(state.status, "win")
        self.assertEqual(state.winner, "X")
        self.assertEqual(state.current_player, "O")
    
    def test_game_state_draw(self):
        """Test GameState with draw condition"""
        full_board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        state = GameState(
            board=full_board,
            current_player="X",
            status="draw",
            winner=None,
            player_x_type="ai",
            player_o_type="ai",
            player_x_model="llama3.2:1b",
            player_o_model="qwen3:4b"
        )
        
        self.assertEqual(state.status, "draw")
        self.assertIsNone(state.winner)
        self.assertEqual(len(state.board), 9)
    
    def test_game_state_serialization(self):
        """Test GameState serialization to dict"""
        state = GameState(
            board=[" ", " ", " ", " ", "X", " ", " ", " ", " "],
            current_player="O",
            status="in_progress",
            winner=None,
            player_x_type="human",
            player_o_type="ai",
            player_x_model=None,
            player_o_model="granite4:3b"
        )
        
        data = state.model_dump()
        expected = {
            "board": [" ", " ", " ", " ", "X", " ", " ", " ", " "],
            "current_player": "O",
            "status": "in_progress",
            "winner": None,
            "player_x_type": "human",
            "player_o_type": "ai",
            "player_x_model": None,
            "player_o_model": "granite4:3b"
        }
        self.assertEqual(data, expected)

if __name__ == '__main__':
    unittest.main()