from pydantic import BaseModel
from typing import Optional

class NewGameRequest(BaseModel):
    player_x_type: str  # "human" or "ai"
    player_o_type: str  # "human" or "ai"
    player_x_model: Optional[str] = None
    player_o_model: Optional[str] = None

class MoveRequest(BaseModel):
    position: int

class GameState(BaseModel):
    board: list
    current_player: str
    status: str
    winner: Optional[str]
    player_x_type: str
    player_o_type: str
    player_x_model: Optional[str]
    player_o_model: Optional[str]