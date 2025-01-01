from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.models import GameState, Move, Side
from app.game_logic import is_valid_move, make_move, get_ai_move

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory game state
current_game: Optional[GameState] = None

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/new-game")
async def new_game():
    """Start a new game"""
    global current_game
    current_game = GameState.new_game()
    return current_game

@app.get("/api/game-state")
async def get_game_state():
    """Get the current game state"""
    if not current_game:
        raise HTTPException(status_code=404, detail="No game in progress")
    return current_game

@app.post("/api/move")
async def make_player_move(move: Move):
    """Make a player move and respond with AI move"""
    global current_game
    
    if not current_game:
        raise HTTPException(status_code=404, detail="No game in progress")
        
    if current_game.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")
        
    # Validate and make player's move
    if not is_valid_move(current_game, move):
        raise HTTPException(status_code=400, detail="Invalid move")
        
    try:
        # Ensure game state exists and is valid
        if not current_game:
            raise HTTPException(status_code=404, detail="No game in progress")
            
        # Make player move
        updated_game = make_move(current_game, move)
        if not updated_game:
            raise HTTPException(status_code=400, detail="Invalid move")
            
        current_game = updated_game
        
        if current_game.game_over:
            return current_game
            
        # Make AI move
        ai_move = get_ai_move(current_game)
        if ai_move:
            ai_game_state = make_move(current_game, ai_move)
            if ai_game_state:
                current_game = ai_game_state
            
        return current_game
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
