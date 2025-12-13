from typing import List, Optional, Tuple
from enum import Enum

class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    WIN = "win"
    DRAW = "draw"

class TicTacToeGame:
    WIN_LINES = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
        (0, 4, 8), (2, 4, 6)              # diagonals
    ]
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.board: List[str] = [" "] * 9
        self.current_player: str = "X"
        self.status: GameStatus = GameStatus.IN_PROGRESS
        self.winner: Optional[str] = None
    
    def is_valid_move(self, position: int) -> bool:
        return (0 <= position <= 8 and 
                self.board[position] == " " and 
                self.status == GameStatus.IN_PROGRESS)
    
    def make_move(self, position: int) -> bool:
        if not self.is_valid_move(position):
            return False
        
        self.board[position] = self.current_player
        
        if self._check_win(self.current_player):
            self.status = GameStatus.WIN
            self.winner = self.current_player
        elif self._is_draw():
            self.status = GameStatus.DRAW
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
        
        return True
    
    def _check_win(self, player: str) -> bool:
        for line in self.WIN_LINES:
            if all(self.board[pos] == player for pos in line):
                return True
        return False
    
    def _is_draw(self) -> bool:
        return all(cell != " " for cell in self.board)
    
    def get_state(self) -> dict:
        return {
            "board": self.board.copy(),
            "current_player": self.current_player,
            "status": self.status.value,
            "winner": self.winner
        }
    
    def get_empty_positions(self) -> List[int]:
        return [i for i, cell in enumerate(self.board) if cell == " "]