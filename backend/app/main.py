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
        print(f"Before AI move - current turn: {current_game.current_turn}")
        print(f"Game state before AI move: {len(current_game.pieces)} pieces")
        
        # Verify it's black's turn before AI moves
        if current_game.current_turn != Side.BLACK:
            print(f"ERROR: Wrong turn for AI move: {current_game.current_turn}")
            return current_game
            
        ai_move = get_ai_move(current_game)
        if ai_move:
            print(f"AI selected move: piece_id={ai_move.piece_id}, to=({ai_move.to_x}, {ai_move.to_y})")
            # Get the piece that AI is trying to move
            if ai_move.piece_id < len(current_game.pieces):
                piece = current_game.pieces[ai_move.piece_id]
                print(f"AI attempting to move {piece.type} at ({piece.x}, {piece.y})")
            
            if not is_valid_move(current_game, ai_move):
                print("AI generated an invalid move!")
                return current_game
                
            try:
                ai_game_state = make_move(current_game, ai_move)
                if ai_game_state:
                    print(f"AI move successful - new turn: {ai_game_state.current_turn}")
                    current_game = ai_game_state  # Update the global state
                    print(f"Updated game state - current turn: {current_game.current_turn}")
                    print(f"Game state after AI move: {len(current_game.pieces)} pieces")
                else:
                    print("AI move failed to generate new game state")
            except ValueError as ve:
                print(f"Error making AI move: {str(ve)}")
                return current_game
        else:
            print("No AI move generated")
            
        # Return the updated game state after AI move
        return current_game
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
