import unittest
import json
import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
app = main.app
from game import GameStatus

class TestAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct message"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Tic-Tac-Toe AI Arena")
    
    def test_new_game_endpoint(self):
        """Test new game creation"""
        response = self.client.post("/new_game", 
            json={
                "player_x_type": "human",
                "player_o_type": "human"
            })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check initial game state
        self.assertEqual(data["board"], [" "] * 9)
        self.assertEqual(data["current_player"], "X")
        self.assertEqual(data["status"], "in_progress")
        self.assertIsNone(data["winner"])
        self.assertEqual(data["player_x_type"], "human")
        self.assertEqual(data["player_o_type"], "human")
    
    def test_new_game_with_ai(self):
        """Test new game with AI players"""
        response = self.client.post("/new_game", 
            json={
                "player_x_type": "ai",
                "player_o_type": "ai",
                "player_x_model": "llama3.2:1b",
                "player_o_model": "qwen3:4b"
            })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["player_x_type"], "ai")
        self.assertEqual(data["player_o_type"], "ai")
        self.assertEqual(data["player_x_model"], "llama3.2:1b")
        self.assertEqual(data["player_o_model"], "qwen3:4b")
    
    def test_invalid_new_game(self):
        """Test new game with invalid player types"""
        response = self.client.post("/new_game", 
            json={
                "player_x_type": "invalid",
                "player_o_type": "human"
            })
        self.assertEqual(response.status_code, 400)
    
    def test_move_endpoint(self):
        """Test making a move"""
        # First start a game
        self.client.post("/new_game", 
            json={"player_x_type": "human", "player_o_type": "human"})
        
        # Make a move
        response = self.client.post("/move", json={"position": 0})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check move was applied
        self.assertEqual(data["board"][0], "X")
        self.assertEqual(data["current_player"], "O")
    
    def test_invalid_move(self):
        """Test invalid move handling"""
        # First start a game
        self.client.post("/new_game", 
            json={"player_x_type": "human", "player_o_type": "human"})
        
        # Try invalid move (out of bounds)
        response = self.client.post("/move", json={"position": 9})
        self.assertEqual(response.status_code, 400)
        
        # Try move on occupied space
        self.client.post("/move", json={"position": 0})  # Occupy position 0
        response = self.client.post("/move", json={"position": 0})  # Try again
        self.assertEqual(response.status_code, 400)
    
    def test_state_endpoint(self):
        """Test getting current game state"""
        # First start a game
        self.client.post("/new_game", 
            json={"player_x_type": "human", "player_o_type": "human"})
        
        # Get state
        response = self.client.get("/state")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check state structure
        self.assertIn("board", data)
        self.assertIn("current_player", data)
        self.assertIn("status", data)
        self.assertIn("winner", data)
        self.assertIn("player_x_type", data)
        self.assertIn("player_o_type", data)

if __name__ == '__main__':
    unittest.main()