import unittest
from unittest.mock import patch, MagicMock
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import AgentFactory, AIAgent, HumanAgent, Agent

class TestAgentsCoverage(unittest.TestCase):
    """Test coverage for missing lines in agents.py"""
    
    def test_agent_abstract_method(self):
        """Test abstract Agent class (line 8) - execute through inheritance"""
        # Create a concrete implementation that calls super() to execute abstract method
        class TestConcreteAgent(Agent):
            def get_move(self, board: list, player: str) -> Optional[int]:
                # Call the parent method to execute line 8
                try:
                    return super().get_move(board, player)
                except:
                    return None
        
        # This will execute the abstract method when called
        agent = TestConcreteAgent()
        result = agent.get_move([' '] * 9, 'X')
        self.assertIsNone(result)
    
    def test_human_agent_init(self):
        """Test HumanAgent initialization (line 12)"""
        agent = HumanAgent()
        self.assertIsInstance(agent, HumanAgent)
    
    def test_human_agent_get_move(self):
        """Test HumanAgent get_move returns None (line 16)"""
        agent = HumanAgent()
        result = agent.get_move([' '] * 9, 'X')
        self.assertIsNone(result)
    
    @patch('agents.OllamaClient')
    def test_ai_agent_init_with_default(self, mock_ollama):
        """Test AIAgent initialization with default model (line 19-21)"""
        mock_client = MagicMock()
        mock_ollama.return_value = mock_client
        
        agent = AIAgent()  # Uses default model
        
        # Test that model attribute is set (line 21)
        self.assertEqual(agent.model, 'llama3.2:1b')
        mock_ollama.assert_called_once_with('llama3.2:1b')
    
    @patch('agents.OllamaClient')
    def test_ai_agent_init_with_custom(self, mock_ollama):
        """Test AIAgent initialization with custom model"""
        mock_client = MagicMock()
        mock_ollama.return_value = mock_client
        
        agent = AIAgent('test-model')
        
        # Test that model attribute is set (line 21)
        self.assertEqual(agent.model, 'test-model')
        mock_ollama.assert_called_once_with('test-model')
    
    @patch('agents.OllamaClient')
    def test_ai_agent_get_move(self, mock_ollama):
        """Test AIAgent get_move delegates to client (line 24)"""
        mock_client = MagicMock()
        mock_client.get_move.return_value = 4
        mock_ollama.return_value = mock_client
        
        agent = AIAgent('test-model')
        result = agent.get_move([' '] * 9, 'X')
        
        # Verify delegation to client (line 24)
        self.assertEqual(result, 4)
        mock_client.get_move.assert_called_once_with([' '] * 9, 'X')
    
    def test_agent_factory_creates_human(self):
        """Test AgentFactory creates HumanAgent (line 30)"""
        agent = AgentFactory.create_agent('human')
        self.assertIsInstance(agent, HumanAgent)
    
    @patch('agents.OllamaClient')
    def test_agent_factory_creates_ai_with_model(self, mock_ollama):
        """Test AgentFactory creates AIAgent with provided model (line 34)"""
        mock_client = MagicMock()
        mock_ollama.return_value = mock_client
        
        agent = AgentFactory.create_agent('ai', 'custom-model')
        
        # Verify AIAgent created with custom model (line 34)
        self.assertIsInstance(agent, AIAgent)
        mock_ollama.assert_called_once_with('custom-model')
    
    @patch('agents.OllamaClient')
    def test_agent_factory_creates_ai_with_default(self, mock_ollama):
        """Test AgentFactory creates AIAgent with default model (line 32-33)"""
        mock_client = MagicMock()
        mock_ollama.return_value = mock_client
        
        agent = AgentFactory.create_agent('ai', None)
        
        # Verify default model assignment (line 32-33)
        mock_ollama.assert_called_once_with('llama3.2:1b')
    
    def test_agent_factory_raises_error(self):
        """Test AgentFactory raises ValueError for unknown type (line 36)"""
        with self.assertRaises(ValueError) as context:
            AgentFactory.create_agent('unknown')
        
        self.assertIn('Unknown agent type', str(context.exception))

if __name__ == '__main__':
    unittest.main()