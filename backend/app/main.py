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

import json
import os

GAME_STATE_FILE = "game_state.json"

def save_game_state(game_state: Optional[GameState]):
    """Save game state to file"""
    if game_state:
        with open(GAME_STATE_FILE, "w") as f:
            json.dump(game_state.dict(), f)
    else:
        if os.path.exists(GAME_STATE_FILE):
            os.remove(GAME_STATE_FILE)

def load_game_state() -> Optional[GameState]:
    """Load game state from file"""
    try:
        if os.path.exists(GAME_STATE_FILE):
            with open(GAME_STATE_FILE, "r") as f:
                data = json.load(f)
                return GameState(**data)
    except Exception as e:
        print(f"Error loading game state: {e}")
    return None

# Initialize game state from file
current_game = load_game_state()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/new-game")
async def new_game():
    """Start a new game"""
    global current_game
    current_game = GameState.new_game()
    save_game_state(current_game)
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
    print("\n=== Starting move processing ===")
    
    if not current_game:
        raise HTTPException(status_code=404, detail="No game in progress")
    
    print(f"Received move: piece_id={move.piece_id}, to=({move.to_x}, {move.to_y})")
    print(f"Current turn: {current_game.current_turn}")
    print(f"Piece count: {len(current_game.pieces)}")
    
    if current_game.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    try:
        # Validate player's turn
        if current_game.current_turn != Side.RED:
            raise HTTPException(status_code=400, detail="Not player's turn")
            
        # Get the piece being moved
        if move.piece_id >= len(current_game.pieces):
            raise HTTPException(status_code=400, detail="Invalid piece ID")
        piece = current_game.pieces[move.piece_id]
        if piece.side != Side.RED:
            raise HTTPException(status_code=400, detail="Cannot move opponent's piece")
            
        # Validate and make player move
        if not is_valid_move(current_game, move):
            print("Move validation failed")
            raise HTTPException(status_code=400, detail="Invalid move")
        
        # Make player move
        print("\n=== Making player move ===")
        updated_game = make_move(current_game, move)
        if not updated_game: 
            raise HTTPException(status_code=500, detail="Failed to update game state")
        
        current_game = updated_game
        save_game_state(current_game)
        print(f"Player move completed")
        print(f"Turn after player move: {current_game.current_turn}")
        
        if current_game.game_over:
            return current_game
            
        # Process AI move
        print("\n=== Processing AI move ===")
        if current_game.current_turn != Side.BLACK:
            print("Warning: Expected BLACK's turn for AI move")
            return current_game
            
        ai_move = get_ai_move(current_game)
        if not ai_move:
            print("Warning: AI could not generate a valid move")
            return current_game
            
        print(f"AI selected move: piece_id={ai_move.piece_id}, to=({ai_move.to_x}, {ai_move.to_y})")
        ai_piece = current_game.pieces[ai_move.piece_id]
        print(f"Moving {ai_piece.type} from ({ai_piece.x}, {ai_piece.y})")
        
        if not is_valid_move(current_game, ai_move):
            print("Warning: AI generated an invalid move")
            return current_game
            
        print("\n=== Making AI move ===")
        ai_game_state = make_move(current_game, ai_move)
        if not ai_game_state:
            print("Warning: AI move failed to generate new game state")
            return current_game
            
        current_game = ai_game_state
        save_game_state(current_game)
        print("AI move completed")
        print(f"Turn after AI move: {current_game.current_turn}")
        
        print("\n=== Move processing completed ===")
        print(f"Final turn: {current_game.current_turn}")
        print(f"Final piece count: {len(current_game.pieces)}")
        return current_game
        
    except ValueError as ve:
        print(f"Error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
