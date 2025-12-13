import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_client import OllamaClient

class TestOllamaCoverage(unittest.TestCase):
    """Test coverage for missing lines in ollama_client.py"""
    
    @patch('ollama_client.subprocess.run')
    @patch('ollama_client.subprocess.Popen')
    def test_generate_error_returncode(self, mock_popen, mock_run):
        """Test generate method with non-zero returncode (lines 27-28)"""
        mock_echo_proc = MagicMock()
        mock_popen.return_value = mock_echo_proc
        
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Model not found"
        
        client = OllamaClient('test-model')
        result = client.generate("test prompt")
        
        # Should return None on error
        self.assertIsNone(result)
    
    @patch('ollama_client.subprocess.run')
    @patch('ollama_client.subprocess.Popen')
    def test_generate_timeout_exception(self, mock_popen, mock_run):
        """Test generate method with timeout exception (lines 37-38)"""
        mock_echo_proc = MagicMock()
        mock_popen.return_value = mock_echo_proc
        
        # Mock timeout exception
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 5)
        
        client = OllamaClient('test-model')
        result = client.generate("test prompt")
        
        # Should return None on timeout
        self.assertIsNone(result)
    
    @patch('ollama_client.subprocess.run')
    @patch('ollama_client.subprocess.Popen')
    def test_generate_general_exception(self, mock_popen, mock_run):
        """Test generate method with general exception (lines 39-41)"""
        mock_echo_proc = MagicMock()
        mock_popen.return_value = mock_echo_proc
        
        # Mock general exception (not timeout)
        mock_run.side_effect = Exception("General error")
        
        client = OllamaClient('test-model')
        result = client.generate("test prompt")
        
        # Should return None on general exception
        self.assertIsNone(result)
    
    @patch('ollama_client.subprocess.run')
    @patch('ollama_client.subprocess.Popen')
    def test_generate_success_with_lines(self, mock_popen, mock_run):
        """Test generate method with multiple lines in response"""
        # Mock successful subprocess response with multiple lines
        mock_echo_proc = MagicMock()
        mock_popen.return_value = mock_echo_proc
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Thinking...\n4\nI choose position 4"
        
        client = OllamaClient('test-model')
        result = client.generate("test prompt")
        
        # Should return last non-empty line
        self.assertEqual(result, "I choose position 4")
        
        # Verify subprocess calls
        mock_popen.assert_called_once()
        mock_run.assert_called_once()
    
    @patch('ollama_client.subprocess.run')
    @patch('ollama_client.subprocess.Popen')
    def test_generate_empty_response(self, mock_popen, mock_run):
        """Test generate method with empty response"""
        mock_echo_proc = MagicMock()
        mock_popen.return_value = mock_echo_proc
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "   \n  \n   "  # Only whitespace
        
        client = OllamaClient('test-model')
        result = client.generate("test prompt")
        
        # Should return stripped empty string
        self.assertEqual(result, "")
    
    @patch('ollama_client.subprocess.run')
    @patch('ollama_client.subprocess.Popen')
    def test_generate_no_lines(self, mock_popen, mock_run):
        """Test generate method with no lines in response"""
        mock_echo_proc = MagicMock()
        mock_popen.return_value = mock_echo_proc
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        
        client = OllamaClient('test-model')
        result = client.generate("test prompt")
        
        # Should return empty string
        self.assertEqual(result, "")
    
    @patch('ollama_client.subprocess.run')
    def test_get_move_none_response(self, mock_run):
        """Test get_move with None response from generate (line 54)"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "some response"
        
        # Mock generate to return None
        with patch.object(OllamaClient, 'generate', return_value=None):
            client = OllamaClient('test-model')
            result = client.get_move([' '] * 9, 'X')
            
            # Should return None when generate returns None
            self.assertIsNone(result)
    
    @patch('ollama_client.subprocess.run')
    def test_get_move_valid_bounds(self, mock_run):
        """Test get_move with valid bounds response (line 61)"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "4"  # Valid move
        
        client = OllamaClient('test-model')
        result = client.get_move([' '] * 9, 'X')
        
        # Should return valid move
        self.assertEqual(result, 4)
    
    @patch('ollama_client.subprocess.run')
    def test_get_move_out_of_bounds(self, mock_run):
        """Test get_move with out of bounds response"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "9"  # Out of bounds
        
        client = OllamaClient('test-model')
        result = client.get_move([' '] * 9, 'X')
        
        # Should return None for out of bounds move
        self.assertIsNone(result)
    
    @patch('ollama_client.subprocess.run')
    def test_get_move_no_numbers(self, mock_run):
        """Test get_move with no numbers in response"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "I don't want to make a move"
        
        client = OllamaClient('test-model')
        result = client.get_move([' '] * 9, 'X')
        
        # Should return None when no numbers found
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()