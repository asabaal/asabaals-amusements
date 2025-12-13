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

class TestAPISimple(unittest.TestCase):
    
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

if __name__ == '__main__':
    unittest.main()