import unittest
import json
import requests
import time
import subprocess
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAPIIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Start server for integration testing"""
        # Use safe silent-detachment protocol
        cmd = ["python", "main.py"]
        cls.server_process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)  # Wait for server to start
        cls.base_url = "http://localhost:8000"
    
    @classmethod
    def tearDownClass(cls):
        """Stop server after testing"""
        subprocess.run(["pkill", "-f", "python.*main.py"])
        time.sleep(1)
    
    def setUp(self):
        """Reset game before each test"""
        try:
            requests.post(f"{self.base_url}/new_game", 
                        json={"player_x_type": "human", "player_o_type": "human"})
        except:
            pass  # Server might not be ready
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Tic-Tac-Toe AI Arena")
    
    def test_new_game_endpoint(self):
        """Test new game creation"""
        response = requests.post(f"{self.base_url}/new_game", 
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
    
    def test_move_sequence(self):
        """Test sequence of moves"""
        # Start new game
        requests.post(f"{self.base_url}/new_game", 
                    json={"player_x_type": "human", "player_o_type": "human"})
        
        # Make moves
        response = requests.post(f"{self.base_url}/move", json={"position": 0})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["board"][0], "X")
        self.assertEqual(data["current_player"], "O")
        
        # Second move
        response = requests.post(f"{self.base_url}/move", json={"position": 4})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["board"][4], "O")
        self.assertEqual(data["current_player"], "X")
    
    def test_invalid_move(self):
        """Test invalid move handling"""
        # Start new game
        requests.post(f"{self.base_url}/new_game", 
                    json={"player_x_type": "human", "player_o_type": "human"})
        
        # Try invalid move (out of bounds)
        response = requests.post(f"{self.base_url}/move", json={"position": 9})
        self.assertEqual(response.status_code, 400)
        
        # Try move on occupied space
        requests.post(f"{self.base_url}/move", json={"position": 0})  # Occupy position 0
        response = requests.post(f"{self.base_url}/move", json={"position": 0})  # Try again
        self.assertEqual(response.status_code, 400)
    
    def test_state_endpoint(self):
        """Test getting current game state"""
        # Start new game
        requests.post(f"{self.base_url}/new_game", 
                    json={"player_x_type": "human", "player_o_type": "human"})
        
        # Get state
        response = requests.get(f"{self.base_url}/state")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check state structure
        self.assertIn("board", data)
        self.assertIn("current_player", data)
        self.assertIn("status", data)
        self.assertIn("winner", data)

if __name__ == '__main__':
    unittest.main()