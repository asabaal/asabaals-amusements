import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from game import GameStatus
from fastapi import HTTPException

class TestMainCoverage(unittest.TestCase):
    
    def setUp(self):
        # Reset global state before each test
        main.game.reset()
        main.player_x_agent = None
        main.player_o_agent = None
        main.player_x_type = "human"
        main.player_o_type = "human"
        main.player_x_model = None
        main.player_o_model = None
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct message"""
        result = main.root()
        self.assertEqual(result["message"], "Tic-Tac-Toe AI Arena")
    
    @patch('main.AgentFactory')
    def test_new_game_invalid_player_type(self, mock_factory):
        """Test new game with invalid player type raises exception"""
        request = main.NewGameRequest(
            player_x_type="invalid",
            player_o_type="human"
        )
        
        with self.assertRaises(HTTPException) as context:
            main.new_game(request)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid player type", str(context.exception.detail))
    
    @patch('main.AgentFactory')
    def test_new_game_valid_setup(self, mock_factory):
        """Test new game with valid setup"""
        mock_x_agent = MagicMock()
        mock_o_agent = MagicMock()
        mock_factory.create_agent.side_effect = [mock_x_agent, mock_o_agent]
        
        request = main.NewGameRequest(
            player_x_type="human",
            player_o_type="ai",
            player_o_model="llama3.2:1b"
        )
        
        result = main.new_game(request)
        
        # Verify agents were created
        mock_factory.create_agent.assert_any_call("human", None)
        mock_factory.create_agent.assert_any_call("ai", "llama3.2:1b")
        
        # Verify game was reset
        self.assertEqual(main.game.board, [" "] * 9)
        self.assertEqual(main.game.current_player, "X")
        
        # Verify configuration stored
        self.assertEqual(main.player_x_type, "human")
        self.assertEqual(main.player_o_type, "ai")
        self.assertEqual(main.player_o_model, "llama3.2:1b")
    
    def test_move_invalid_move(self):
        """Test move with invalid position"""
        main.player_x_type = "human"
        main.player_o_type = "human"
        
        request = main.MoveRequest(position=9)  # Invalid position
        
        with self.assertRaises(HTTPException) as context:
            main.make_move(request)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid move", str(context.exception.detail))
    
    def test_move_ai_turn_error(self):
        """Test move during AI turn raises error"""
        main.player_x_type = "ai"
        main.player_o_type = "human"
        main.game.current_player = "X"  # AI's turn
        
        request = main.MoveRequest(position=0)
        
        with self.assertRaises(HTTPException) as context:
            main.make_move(request)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("AI's turn", str(context.exception.detail))
    
    @patch('main.AgentFactory')
    def test_move_successful_human_move(self, mock_factory):
        """Test successful human move"""
        mock_x_agent = MagicMock()
        mock_o_agent = MagicMock()
        mock_factory.create_agent.side_effect = [mock_x_agent, mock_o_agent]
        
        main.player_x_type = "human"
        main.player_o_type = "ai"
        
        request = main.MoveRequest(position=0)
        result = main.make_move(request)
        
        # Verify move was made
        self.assertEqual(main.game.board[0], "X")
        self.assertEqual(main.game.current_player, "O")
    
    @patch('main.AgentFactory')
    def test_make_ai_move_with_valid_agent(self, mock_factory):
        """Test make_ai_move with valid agent"""
        mock_agent = MagicMock()
        mock_agent.get_move.return_value = 4
        mock_factory.create_agent.return_value = mock_agent
        
        main.player_x_type = "ai"
        main.player_o_type = "human"
        main.game.current_player = "X"  # AI's turn
        
        # Run the async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(main.make_ai_move())
        finally:
            loop.close()
        
        # Verify AI was asked for move
        mock_agent.get_move.assert_called_once_with(main.game.board, "X")
        
        # Verify move was made
        self.assertEqual(main.game.board[4], "X")
    
    @patch('main.AgentFactory')
    def test_make_ai_move_with_retries(self, mock_factory):
        """Test make_ai_move with retries on invalid moves"""
        mock_agent = MagicMock()
        # First call returns invalid, second returns valid
        mock_agent.get_move.side_effect = [None, 4]
        mock_factory.create_agent.return_value = mock_agent
        
        main.player_x_type = "ai"
        main.player_o_type = "human"
        main.game.current_player = "X"  # AI's turn
        
        # Run the async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(main.make_ai_move())
        finally:
            loop.close()
        
        # Verify AI was called twice
        self.assertEqual(mock_agent.get_move.call_count, 2)
        
        # Verify valid move was eventually made
        self.assertEqual(main.game.board[4], "X")
    
    @patch('main.AgentFactory')
    def test_make_ai_move_fallback_to_random(self, mock_factory):
        """Test make_ai_move falls back to random when all retries fail"""
        mock_agent = MagicMock()
        mock_agent.get_move.return_value = None  # Always fails
        mock_factory.create_agent.return_value = mock_agent
        
        main.player_x_type = "ai"
        main.player_o_type = "human"
        main.game.current_player = "X"  # AI's turn
        
        # Run the async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(main.make_ai_move())
        finally:
            loop.close()
        
        # Verify AI was called max_retries times
        self.assertEqual(mock_agent.get_move.call_count, 3)
        
        # Verify fallback move was made (first empty position)
        self.assertEqual(main.game.board[0], "X")
    
    @patch('main.AgentFactory')
    def test_make_ai_move_no_agent(self, mock_factory):
        """Test make_ai_move when agent is None"""
        mock_factory.create_agent.return_value = None
        
        main.player_x_type = "ai"
        main.player_o_type = "human"
        main.game.current_player = "X"  # AI's turn
        
        # Run the async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(main.make_ai_move())
        finally:
            loop.close()
        
        # Verify no move was made
        self.assertEqual(main.game.board, [" "] * 9)
    
    def test_get_game_state(self):
        """Test get_game_state function"""
        # Set up some state
        main.player_x_type = "ai"
        main.player_o_type = "human"
        main.player_x_model = "llama3.2:1b"
        main.player_o_model = None
        main.game.board[0] = "X"
        main.game.current_player = "O"
        main.game.status = GameStatus.WIN
        main.game.winner = "X"
        
        result = main.get_game_state()
        
        self.assertEqual(result.board[0], "X")
        self.assertEqual(result.current_player, "O")
        self.assertEqual(result.status, "win")
        self.assertEqual(result.winner, "X")
        self.assertEqual(result.player_x_type, "ai")
        self.assertEqual(result.player_o_type, "human")
        self.assertEqual(result.player_x_model, "llama3.2:1b")
        self.assertIsNone(result.player_o_model)
    
    def test_state_endpoint(self):
        """Test state endpoint returns game state"""
        result = main.get_state()
        # Should be a coroutine, so we need to check it's callable
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            actual_result = loop.run_until_complete(result)
        finally:
            loop.close()
        
        self.assertIsInstance(actual_result, dict)
        self.assertIn('board', actual_result)
        self.assertIn('current_player', actual_result)
        self.assertIn('status', actual_result)
        self.assertIn('winner', actual_result)
        self.assertIn('player_x_type', actual_result)
        self.assertIn('player_o_type', actual_result)

if __name__ == '__main__':
    unittest.main()