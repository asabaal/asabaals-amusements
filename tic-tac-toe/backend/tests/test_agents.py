import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent, HumanAgent, AIAgent, AgentFactory

class TestAgents(unittest.TestCase):
    
    def test_human_agent(self):
        """Test HumanAgent functionality"""
        agent = HumanAgent()
        self.assertIsInstance(agent, Agent)
        
        # Human agent should always return None (moves come via API)
        result = agent.get_move([' '] * 9, 'X')
        self.assertIsNone(result)
    
    @patch('agents.OllamaClient')
    def test_ai_agent(self, mock_ollama_client):
        """Test AIAgent functionality"""
        # Mock OllamaClient
        mock_client = MagicMock()
        mock_client.get_move.return_value = 4
        mock_ollama_client.return_value = mock_client
        
        agent = AIAgent('test-model')
        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.model, 'test-model')
        
        # Test get_move delegates to OllamaClient
        result = agent.get_move([' '] * 9, 'X')
        self.assertEqual(result, 4)
        mock_client.get_move.assert_called_once_with([' '] * 9, 'X')
    
    @patch('agents.OllamaClient')
    def test_ai_agent_default_model(self, mock_ollama_client):
        """Test AIAgent uses default model"""
        mock_client = MagicMock()
        mock_client.get_move.return_value = 0
        mock_ollama_client.return_value = mock_client
        
        agent = AIAgent()
        self.assertEqual(agent.model, 'llama3.2:1b')
        mock_ollama_client.assert_called_once_with('llama3.2:1b')
    
    def test_agent_factory_human(self):
        """Test AgentFactory creates human agents"""
        agent = AgentFactory.create_agent('human')
        self.assertIsInstance(agent, HumanAgent)
    
    @patch('agents.OllamaClient')
    def test_agent_factory_ai(self, mock_ollama_client):
        """Test AgentFactory creates AI agents"""
        mock_client = MagicMock()
        mock_client.get_move.return_value = 0
        mock_ollama_client.return_value = mock_client
        
        agent = AgentFactory.create_agent('ai', 'test-model')
        self.assertIsInstance(agent, AIAgent)
        self.assertEqual(agent.model, 'test-model')
    
    @patch('agents.OllamaClient')
    def test_agent_factory_ai_default_model(self, mock_ollama_client):
        """Test AgentFactory creates AI agents with default model"""
        mock_client = MagicMock()
        mock_client.get_move.return_value = 0
        mock_ollama_client.return_value = mock_client
        
        agent = AgentFactory.create_agent('ai')
        self.assertIsInstance(agent, AIAgent)
        self.assertEqual(agent.model, 'llama3.2:1b')
    
    def test_agent_factory_invalid_type(self):
        """Test AgentFactory raises error for invalid agent type"""
        with self.assertRaises(ValueError) as context:
            AgentFactory.create_agent('invalid')
        
        self.assertIn('Unknown agent type', str(context.exception))
    
    @patch('agents.OllamaClient')
    def test_ai_agent_move_failure(self, mock_ollama_client):
        """Test AIAgent handles move failure gracefully"""
        mock_client = MagicMock()
        mock_client.get_move.return_value = None  # Simulate failure
        mock_ollama_client.return_value = mock_client
        
        agent = AIAgent('test-model')
        result = agent.get_move([' '] * 9, 'X')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()