from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from game import TicTacToeGame
from agents import AgentFactory
from models import NewGameRequest, MoveRequest, GameState

app = FastAPI(title="Tic-Tac-Toe AI Arena")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game state (single game instance for simplicity)
game = TicTacToeGame()
player_x_agent = None
player_o_agent = None
player_x_type = "human"
player_o_type = "human"
player_x_model = None
player_o_model = None

@app.get("/")
async def root():
    return {"message": "Tic-Tac-Toe AI Arena"}

@app.post("/new_game")
async def new_game(request: NewGameRequest):
    global game, player_x_agent, player_o_agent, player_x_type, player_o_type, player_x_model, player_o_model
    
    # Validate request
    if request.player_x_type not in ["human", "ai"] or request.player_o_type not in ["human", "ai"]:
        raise HTTPException(status_code=400, detail="Invalid player type")
    
    # Create agents
    player_x_agent = AgentFactory.create_agent(request.player_x_type, request.player_x_model)
    player_o_agent = AgentFactory.create_agent(request.player_o_type, request.player_o_model)
    
    # Store configuration
    player_x_type = request.player_x_type
    player_o_type = request.player_o_type
    player_x_model = request.player_x_model
    player_o_model = request.player_o_model
    
    # Reset game
    game.reset()
    
    # If AI vs AI, make first move
    if player_x_type == "ai" and player_o_type == "ai":
        await make_ai_move()
    
    return get_game_state()

@app.post("/move")
async def make_move(request: MoveRequest):
    global game, player_x_agent, player_o_agent, player_x_type, player_o_type
    
    # Determine if it's human's turn
    current_agent_type = player_x_type if game.current_player == "X" else player_o_type
    
    if current_agent_type == "ai":
        raise HTTPException(status_code=400, detail="It's AI's turn")
    
    # Make human move
    if not game.make_move(request.position):
        raise HTTPException(status_code=400, detail="Invalid move")
    
    # If game is still in progress and next player is AI, make AI move
    if game.status.value == "in_progress":
        next_player_type = player_x_type if game.current_player == "X" else player_o_type
        if next_player_type == "ai":
            await make_ai_move()
    
    return get_game_state()

async def make_ai_move():
    global game, player_x_agent, player_o_agent, player_x_type, player_o_type
    
    current_agent = player_x_agent if game.current_player == "X" else player_o_agent
    
    if current_agent is None:
        return
    
    # Try to get a valid move (with retries)
    max_retries = 3
    for _ in range(max_retries):
        move = current_agent.get_move(game.board, game.current_player)
        if move is not None and game.is_valid_move(move):
            game.make_move(move)
            break
    else:
        # If AI fails to make valid move, make a random valid move
        empty_positions = game.get_empty_positions()
        if empty_positions:
            game.make_move(empty_positions[0])

@app.get("/state")
async def get_state():
    return get_game_state()

def get_game_state():
    return GameState(
        board=game.board,
        current_player=game.current_player,
        status=game.status.value,
        winner=game.winner,
        player_x_type=player_x_type,
        player_o_type=player_o_type,
        player_x_model=player_x_model,
        player_o_model=player_o_model
    )

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)