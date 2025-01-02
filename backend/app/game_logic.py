from typing import List, Tuple, Optional
from .models import GameState, Move, Piece, PieceType, Side

def is_valid_move(game_state: GameState, move: Move) -> bool:
    """Validate if a move is legal according to Chinese Chess rules"""
    print(f"\n=== Validating move ===")
    print(f"Piece ID: {move.piece_id}, Destination: ({move.to_x}, {move.to_y})")
    
    if move.piece_id >= len(game_state.pieces):
        print(f"Invalid move: piece_id {move.piece_id} out of range")
        return False
        
    piece = game_state.pieces[move.piece_id]
    print(f"Selected piece: {piece.type} ({piece.side}) at ({piece.x}, {piece.y})")
    print(f"Current turn: {game_state.current_turn}")
    
    # Basic boundary checks
    if not (0 <= move.to_x <= 8 and 0 <= move.to_y <= 9):
        print(f"Invalid move: destination ({move.to_x}, {move.to_y}) out of bounds")
        return False
        
    # Check if it's the correct player's turn
    if piece.side != game_state.current_turn:
        print(f"Invalid move: wrong turn (piece side: {piece.side}, current turn: {game_state.current_turn})")
        return False
        
    # Check if trying to move to current position
    if piece.x == move.to_x and piece.y == move.to_y:
        print("Invalid move: piece cannot stay in the same position")
        return False
        
    # Check if destination has a friendly piece
    for p in game_state.pieces: 
        if p.x == move.to_x and p.y == move.to_y and p.side == piece.side:
            print(f"Invalid move: destination occupied by friendly piece at ({move.to_x}, {move.to_y})")
            return False
            
    # Piece-specific movement rules
    if piece.type == PieceType.GENERAL:
        # General can only move within palace (3x3 grid)
        palace_x = [3, 4, 5]
        palace_y = [0, 1, 2] if piece.side == Side.BLACK else [7, 8, 9]
        if move.to_x not in palace_x or move.to_y not in palace_y:
            return False
        # Can only move one step orthogonally
        if abs(move.to_x - piece.x) + abs(move.to_y - piece.y) != 1:
            return False
            
    elif piece.type == PieceType.ADVISOR:
        # Advisor can only move diagonally within palace
        palace_x = [3, 4, 5]
        palace_y = [0, 1, 2] if piece.side == Side.BLACK else [7, 8, 9]
        if move.to_x not in palace_x or move.to_y not in palace_y:
            return False
        if abs(move.to_x - piece.x) != 1 or abs(move.to_y - piece.y) != 1:
            return False
            
    elif piece.type == PieceType.ELEPHANT:
        # Elephant moves exactly two points diagonally
        if abs(move.to_x - piece.x) != 2 or abs(move.to_y - piece.y) != 2:
            return False
        # Cannot cross river
        if (piece.side == Side.RED and move.to_y < 5) or \
           (piece.side == Side.BLACK and move.to_y > 4):
            return False
            
    elif piece.type == PieceType.HORSE:
        print(f"DEBUG: Validating horse move from ({piece.x}, {piece.y}) to ({move.to_x}, {move.to_y})")
        # Horse moves in L shape (2+1)
        dx = abs(move.to_x - piece.x)
        dy = abs(move.to_y - piece.y)
        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
            print("DEBUG: Invalid horse move pattern")
            return False
            
        # Check for blocking pieces
        # For horizontal movement (2 steps), check the adjacent square
        if dx == 2:
            blocking_x = piece.x + (1 if move.to_x > piece.x else -1)
            blocking_y = piece.y
        # For vertical movement (2 steps), check the adjacent square
        else:  # dy == 2
            blocking_x = piece.x
            blocking_y = piece.y + (1 if move.to_y > piece.y else -1)
            
        # Check if there's a piece blocking the horse's path
        for p in game_state.pieces:
            if p.x == blocking_x and p.y == blocking_y:
                print(f"DEBUG: Horse move blocked at ({blocking_x}, {blocking_y})")
                return False
                
        print("DEBUG: Valid horse move")
        return True
            
    elif piece.type == PieceType.CHARIOT:
        # Chariot moves horizontally or vertically
        if piece.x != move.to_x and piece.y != move.to_y:
            print("DEBUG: Invalid chariot move - must move horizontally or vertically")
            return False
            
        # Check for blocking pieces along the path
        if piece.x == move.to_x:  # Vertical move
            start_y = min(piece.y, move.to_y)
            end_y = max(piece.y, move.to_y)
            for p in game_state.pieces:
                if p.x == piece.x and start_y < p.y < end_y:
                    print(f"DEBUG: Chariot path blocked at ({p.x}, {p.y})")
                    return False
        else:  # Horizontal move
            start_x = min(piece.x, move.to_x)
            end_x = max(piece.x, move.to_x)
            for p in game_state.pieces:
                if p.y == piece.y and start_x < p.x < end_x:
                    print(f"DEBUG: Chariot path blocked at ({p.x}, {p.y})")
                    return False
                    
        print("DEBUG: Valid chariot move")
        return True
    elif piece.type == PieceType.CANNON:
        print(f"DEBUG: Validating cannon move from ({piece.x}, {piece.y}) to ({move.to_x}, {move.to_y})")
        
        # Cannon must move horizontally or vertically
        if piece.x != move.to_x and piece.y != move.to_y:
            print("DEBUG: Invalid cannon move - must move horizontally or vertically")
            return False
            
        # Check if this is a capture move
        target_piece = None
        for p in game_state.pieces:
            if p.x == move.to_x and p.y == move.to_y:
                target_piece = p
                break
                
        capturing = target_piece is not None and target_piece.side != piece.side
        print(f"DEBUG: Move is{' ' if capturing else ' not '}a capture move")
        
        if piece.x == move.to_x:  # Vertical move
            print("DEBUG: Vertical move")
            start_y = min(piece.y, move.to_y)
            end_y = max(piece.y, move.to_y)
            # Count pieces between start and end positions
            pieces_between = [
                p for p in game_state.pieces
                if p.x == piece.x 
                and start_y < p.y < end_y
            ]
            print(f"DEBUG: Found {len(pieces_between)} pieces between")
            
            if capturing:
                if len(pieces_between) != 1:
                    print(f"DEBUG: Invalid cannon capture - need exactly one piece between, found {len(pieces_between)}")
                    return False
            else:
                if len(pieces_between) > 0:
                    print("DEBUG: Invalid cannon move - path must be clear for non-capture moves")
                    return False
        else:  # Horizontal move
            print("DEBUG: Horizontal move")
            start_x = min(piece.x, move.to_x)
            end_x = max(piece.x, move.to_x)
            # Count pieces between start and end positions
            pieces_between = [
                p for p in game_state.pieces
                if p.y == piece.y 
                and start_x < p.x < end_x
            ]
            print(f"DEBUG: Found {len(pieces_between)} pieces between")
            
            if capturing:
                if len(pieces_between) != 1:
                    print(f"DEBUG: Invalid cannon capture - need exactly one piece between, found {len(pieces_between)}")
                    return False
            else:
                if len(pieces_between) > 0:
                    print("DEBUG: Invalid cannon move - path must be clear for non-capture moves")
                    return False
                    
        print("DEBUG: Cannon move validation successful!")
        return True
            
    elif piece.type == PieceType.SOLDIER:
        # Soldier moves forward one step (or sideways after crossing river)
        print(f"DEBUG: Validating soldier move for {piece.side} from ({piece.x}, {piece.y}) to ({move.to_x}, {move.to_y})")
        
        # Can only move one step at a time
        if abs(move.to_x - piece.x) + abs(move.to_y - piece.y) != 1:
            print(f"DEBUG: Invalid soldier move - attempted to move {abs(move.to_x - piece.x) + abs(move.to_y - piece.y)} steps")
            return False
            
        # Check if the soldier has crossed the river
        crossed_river = False
        if piece.side == Side.RED and piece.y < 5:  # Red crosses at y=4
            crossed_river = True
        elif piece.side == Side.BLACK and piece.y > 4:  # Black crosses at y=5
            crossed_river = True
            
        # Movement rules based on position
        if piece.side == Side.RED:
            # Red moves up (decreasing y)
            if move.to_y >= piece.y:  # Cannot move backwards
                print("DEBUG: Invalid move - RED soldier cannot move backwards")
                return False
            if not crossed_river and move.to_x != piece.x:  # Can only move forward before crossing
                print("DEBUG: Invalid move - RED soldier hasn't crossed river, can only move forward")
                return False
        else:  # BLACK
            # Black moves down (increasing y)
            if move.to_y <= piece.y:  # Cannot move backwards
                print("DEBUG: Invalid move - BLACK soldier cannot move backwards")
                return False
            if not crossed_river and move.to_x != piece.x:  # Can only move forward before crossing
                print("DEBUG: Invalid move - BLACK soldier hasn't crossed river, can only move forward")
                return False
                
        print("DEBUG: Valid soldier move")
        return True
            
    return True

def make_move(game_state: GameState, move: Move) -> GameState:
    """Apply a move to the game state and return the new state"""
    print(f"\nMaking move: piece_id={move.piece_id}, to=({move.to_x}, {move.to_y})")
    print(f"Current turn before move: {game_state.current_turn}")
    
    if not game_state:
        raise ValueError("Game state cannot be None")
    
    # Create new game state with deep copy of all pieces first
    new_pieces = [p.copy() for p in game_state.pieces]
    moved_piece = None
    captured_piece = None
    
    # Find the piece being moved and any piece being captured
    for i, p in enumerate(new_pieces):
        if i == move.piece_id:
            moved_piece = p
        elif p.x == move.to_x and p.y == move.to_y:
            captured_piece = p
    
    if moved_piece is None:
        raise ValueError("Invalid piece_id")
        
    # Verify it's the correct player's turn
    if moved_piece.side != game_state.current_turn:
        raise ValueError(f"Wrong turn: piece side {moved_piece.side} != current turn {game_state.current_turn}")
        
    # Store original position for logging
    orig_x, orig_y = moved_piece.x, moved_piece.y
    
    # Update moved piece position
    moved_piece.x = move.to_x
    moved_piece.y = move.to_y
    
    # Remove captured piece if any
    if captured_piece:
        new_pieces.remove(captured_piece)
        print(f"Captured {captured_piece.type} at ({move.to_x}, {move.to_y})")
    
    print(f"Moving {moved_piece.type} from ({orig_x}, {orig_y}) to ({move.to_x}, {move.to_y})")
    
    # Check for game over (general captured)
    game_over = False
    winner = None
    generals = [p for p in new_pieces if p.type == PieceType.GENERAL]
    if len(generals) < 2:
        game_over = True
        winner = generals[0].side if generals else None
        print(f"Game over! Winner: {winner}")
    
    # Switch turns
    next_turn = Side.BLACK if game_state.current_turn == Side.RED else Side.RED
    print(f"Switching turn from {game_state.current_turn} to {next_turn}")
    
    # Create new game state with switched turn
    new_state = GameState(
        pieces=new_pieces,
        current_turn=next_turn,  # Ensure turn is switched
        game_over=game_over,
        winner=winner
    )
    
    print(f"New game state - pieces: {len(new_state.pieces)}, turn: {new_state.current_turn}")
    return new_state

def evaluate_move(game_state: GameState, move: Move) -> int:
    """Evaluate a move's strategic value"""
    piece = game_state.pieces[move.piece_id]
    score = 0
    
    # Piece values for capturing and protection
    piece_values = {
        PieceType.GENERAL: 1000,
        PieceType.CHARIOT: 90,
        PieceType.CANNON: 45,
        PieceType.HORSE: 40,
        PieceType.ADVISOR: 20,
        PieceType.ELEPHANT: 20,
        PieceType.SOLDIER: 10
    }
    
    # Check if move captures an opponent's piece
    for p in game_state.pieces:
        if p.x == move.to_x and p.y == move.to_y and p.side != piece.side:
            score += piece_values[p.type] * 2  # Double value for captures
    
    # Find opponent's general
    opponent_general = None
    for p in game_state.pieces:
        if p.type == PieceType.GENERAL and p.side != piece.side:
            opponent_general = p
            break
    
    if opponent_general:
        # Encourage moving toward opponent's general
        current_dist = abs(piece.x - opponent_general.x) + abs(piece.y - opponent_general.y)
        new_dist = abs(move.to_x - opponent_general.x) + abs(move.to_y - opponent_general.y)
        if new_dist < current_dist:
            score += 15
        
        # Extra points for moves that could lead to checkmate
        if piece.type in [PieceType.CHARIOT, PieceType.CANNON, PieceType.HORSE]:
            if move.to_x == opponent_general.x or move.to_y == opponent_general.y:
                score += 25
    
    # Protect valuable pieces
    for p in game_state.pieces:
        if p.side == piece.side and p.type in [PieceType.GENERAL, PieceType.CHARIOT]:
            dist_to_friendly = abs(move.to_x - p.x) + abs(move.to_y - p.y)
            if dist_to_friendly <= 2:  # Stay close to protect valuable pieces
                score += 10
    
    # Control center (middle columns)
    if 3 <= move.to_x <= 5:
        score += 5
    
    # Advance soldiers across river
    if piece.type == PieceType.SOLDIER:
        if (piece.side == Side.RED and move.to_y < 5) or \
           (piece.side == Side.BLACK and move.to_y > 4):
            score += 20
    
    print(f"Move evaluation: piece={piece.type}, from=({piece.x},{piece.y}), to=({move.to_x},{move.to_y}), score={score}")
    return score

def get_ai_move(game_state: GameState) -> Optional[Move]:
    """Generate a strategic move for the AI player"""
    import random
    print("AI is thinking...")
    
    move_scores = {}
    
    # Generate all possible valid moves
    for i, piece in enumerate(game_state.pieces):
        if piece.side != game_state.current_turn:
            continue
            
        # Try moves in the entire board
        for x in range(9):
            for y in range(10):
                move = Move(piece_id=i, to_x=x, to_y=y)
                if is_valid_move(game_state, move):
                    score = evaluate_move(game_state, move)
                    # Always use tuple as dictionary key
                    move_key = (move.piece_id, move.to_x, move.to_y)
                    move_scores[move_key] = (score, move)
    
    if not move_scores:
        print("No valid moves available for AI")
        return None
    
    # Select one of the top 3 moves randomly to add variety
    sorted_moves = sorted(move_scores.items(), key=lambda x: x[1][0], reverse=True)
    top_moves = sorted_moves[:3]
    # Get the Move object from the score-move tuple
    selected_move = random.choice(top_moves)[1][1]
    
    print(f"AI chose move: piece_id={selected_move.piece_id}, to=({selected_move.to_x}, {selected_move.to_y})")
    return selected_move
