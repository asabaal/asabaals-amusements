import unittest
import requests
import time
import subprocess
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestEndToEnd(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Start server for end-to-end testing"""
        cls.base_url = "http://localhost:8000"
    
    def setUp(self):
        """Reset game before each test"""
        try:
            requests.post(f"{self.base_url}/new_game", 
                        json={"player_x_type": "human", "player_o_type": "human"})
        except:
            pass
    
    def test_complete_human_game(self):
        """Test complete human vs human game"""
        # Start new game
        response = requests.post(f"{self.base_url}/new_game", 
                             json={"player_x_type": "human", "player_o_type": "human"})
        self.assertEqual(response.status_code, 200)
        
        # Play a complete game (X wins)
        moves = [(0, "X"), (4, "O"), (1, "X"), (5, "O"), (2, "X")]  # X wins top row
        
        for position, expected_player in moves:
            response = requests.post(f"{self.base_url}/move", json={"position": position})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["board"][position], expected_player)
        
        # Check game is won
        response = requests.get(f"{self.base_url}/state")
        data = response.json()
        self.assertEqual(data["status"], "win")
        self.assertEqual(data["winner"], "X")
    
    def test_draw_game(self):
        """Test complete game ending in draw"""
        # Start new game
        requests.post(f"{self.base_url}/new_game", 
                    json={"player_x_type": "human", "player_o_type": "human"})
        
        # Play to a draw
        moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]  # Known draw sequence
        
        for position in moves:
            response = requests.post(f"{self.base_url}/move", json={"position": position})
            self.assertEqual(response.status_code, 200)
        
        # Check game is draw
        response = requests.get(f"{self.base_url}/state")
        data = response.json()
        self.assertEqual(data["status"], "draw")
        self.assertIsNone(data["winner"])
    
    def test_ai_game_configuration(self):
        """Test AI vs AI game configuration"""
        # Start AI vs AI game
        response = requests.post(f"{self.base_url}/new_game", 
                             json={
                                 "player_x_type": "ai",
                                 "player_o_type": "ai", 
                                 "player_x_model": "llama3.2:1b",
                                 "player_o_model": "granite4:3b"
                             })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check configuration
        self.assertEqual(data["player_x_type"], "ai")
        self.assertEqual(data["player_o_type"], "ai")
        self.assertEqual(data["player_x_model"], "llama3.2:1b")
        self.assertEqual(data["player_o_model"], "granite4:3b")
    
    def test_invalid_game_configurations(self):
        """Test invalid game configurations are rejected"""
        # Test invalid player type
        response = requests.post(f"{self.base_url}/new_game", 
                             json={"player_x_type": "invalid", "player_o_type": "human"})
        self.assertEqual(response.status_code, 400)
        
        # Test missing required fields
        response = requests.post(f"{self.base_url}/new_game", json={})
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_game_state_consistency(self):
        """Test game state remains consistent across requests"""
        # Start game
        requests.post(f"{self.base_url}/new_game", 
                    json={"player_x_type": "human", "player_o_type": "human"})
        
        # Make a move
        requests.post(f"{self.base_url}/move", json={"position": 0})
        
        # Check state consistency
        response1 = requests.get(f"{self.base_url}/state")
        response2 = requests.get(f"{self.base_url}/state")
        
        data1 = response1.json()
        data2 = response2.json()
        
        # States should be identical
        self.assertEqual(data1["board"], data2["board"])
        self.assertEqual(data1["current_player"], data2["current_player"])
        self.assertEqual(data1["status"], data2["status"])

if __name__ == '__main__':
    unittest.main()