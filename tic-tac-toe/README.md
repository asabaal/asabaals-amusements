# Tic-Tac-Toe AI Arena

A web-based Tic-Tac-Toe game where you can play against local AI models via Ollama, or watch AI models play against each other.

## Features

- **Human vs AI**: Play against local AI models
- **AI vs AI**: Watch different AI models compete
- **Multiple AI Models**: Support for llama3, mistral, qwen, mixtral
- **Clean Web UI**: Simple, responsive interface
- **Real-time Updates**: Watch AI games unfold in real-time

## Prerequisites

1. **Ollama**: Install and run Ollama locally
   ```bash
   # Install Ollama (follow instructions at https://ollama.ai)
   # Pull at least one model:
   ollama pull llama3
   ollama pull mistral
   ```

2. **Python 3.8+**

## Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start the backend server**:
   ```bash
   cd backend
   python main.py
   ```

3. **Open the web interface**:
   Open your browser and go to `http://localhost:8000/static/`

## Usage

1. **Configure Players**:
   - Choose "Human" or "AI" for each player (X and O)
   - If AI is selected, choose which model to use

2. **Start a Game**:
   - Click "New Game" to begin
   - If it's your turn, click any empty cell to make your move
   - AI moves will be made automatically

3. **Game Modes**:
   - **Human vs Human**: Classic two-player game
   - **Human vs AI**: Test your skills against AI
   - **AI vs AI**: Watch different models compete

## API Endpoints

- `POST /new_game`: Start a new game with player configuration
- `POST /move`: Make a move (for human players)
- `GET /state`: Get current game state

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI server
│   ├── game.py              # Game engine
│   ├── agents.py            # Player agents (Human/AI)
│   ├── ollama_client.py     # Ollama integration
│   ├── models.py            # Pydantic models
│   └── requirements.txt     # Python dependencies
└── frontend/
    └── index.html           # Web interface
```

## How It Works

1. **Game Engine**: Manages board state, validates moves, detects wins/draws
2. **Agents**: 
   - Human agents receive moves via the web interface
   - AI agents use Ollama to generate moves based on the current board
3. **Ollama Integration**: Sends structured prompts to local AI models
4. **Web UI**: Clean interface for game interaction and configuration

## AI Prompting

The AI agents use a simple, structured prompt:
```
You are playing Tic-Tac-Toe as player X.

Rules:
- Board positions are numbered 0 to 8
- Only choose empty positions
- Only respond with a single integer

Current board: ["X"," ","O"," ","X"," "," "," ","O"]

Your move:
```

This ensures consistent, legal moves from the AI models.

## Troubleshooting

- **Ollama not running**: Make sure Ollama is installed and running locally
- **Model not found**: Pull the required models with `ollama pull <model_name>`
- **Port already in use**: Change the port in `main.py` or stop conflicting services
- **CORS issues**: The backend allows all origins for development

## Future Enhancements

- Tournament mode with multiple games
- Move history and replay
- Performance statistics for different AI models
- More sophisticated prompting strategies
- Additional game variants