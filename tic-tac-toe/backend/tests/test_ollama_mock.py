import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_client import OllamaClient

class TestOllamaClientMock(unittest.TestCase):
    
    @patch('subprocess.run')
    def test_ollama_client_success(self, mock_run):
        """Test Ollama client with successful response"""
        # Mock successful subprocess response
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "4"
        
        client = OllamaClient('test-model')
        result = client.get_move([' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], 'X')
        
        self.assertEqual(result, 4)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_ollama_client_timeout(self, mock_run):
        """Test Ollama client timeout handling"""
        # Mock timeout
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
        
        client = OllamaClient('test-model')
        result = client.get_move([' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], 'X')
        
        self.assertIsNone(result)
    
    @patch('subprocess.run')
    def test_ollama_client_error(self, mock_run):
        """Test Ollama client error handling"""
        # Mock subprocess error
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Model not found"
        
        client = OllamaClient('test-model')
        result = client.get_move([' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], 'X')
        
        self.assertIsNone(result)
    
    @patch('subprocess.run')
    def test_move_extraction(self, mock_run):
        """Test move extraction from response"""
        # Mock response with number in text
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "I choose position 7 for my move"
        
        client = OllamaClient('test-model')
        result = client.get_move([' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], 'X')
        
        self.assertEqual(result, 7)

if __name__ == '__main__':
    unittest.main()