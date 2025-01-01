from typing import List, Tuple, Optional
from .models import GameState, Move, Piece, PieceType, Side

def is_valid_move(game_state: GameState, move: Move) -> bool:
    """Validate if a move is legal according to Chinese Chess rules"""
    print(f"Validating move: piece_id={move.piece_id}, to=({move.to_x}, {move.to_y})")
    
    if move.piece_id >= len(game_state.pieces):
        print(f"Invalid move: piece_id {move.piece_id} out of range")
        return False
        
    piece = game_state.pieces[move.piece_id]
    print(f"Selected piece: type={piece.type}, side={piece.side}, pos=({piece.x}, {piece.y})")
    
    # Basic boundary checks
    if not (0 <= move.to_x <= 8 and 0 <= move.to_y <= 9):
        print(f"Invalid move: destination ({move.to_x}, {move.to_y}) out of bounds")
        return False
        
    # Check if it's the correct player's turn
    if piece.side != game_state.current_turn:
        print(f"Invalid move: wrong turn (piece side: {piece.side}, current turn: {game_state.current_turn})")
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
        # Horse moves in L shape (2+1)
        dx = abs(move.to_x - piece.x)
        dy = abs(move.to_y - piece.y)
        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
            return False
            
    elif piece.type == PieceType.CHARIOT:
        # Chariot moves horizontally or vertically
        if piece.x != move.to_x and piece.y != move.to_y:
            return False
            
    elif piece.type == PieceType.CANNON:
        # Cannon moves like chariot but must jump exactly one piece to capture
        if piece.x != move.to_x and piece.y != move.to_y:
            return False
            
        # Check if this is a capture move
        capturing = any(
            p.x == move.to_x and p.y == move.to_y and p.side != piece.side
            for p in game_state.pieces
        )
        
        if piece.x == move.to_x:  # Vertical move
            start_y = min(piece.y, move.to_y)
            end_y = max(piece.y, move.to_y)
            # Count pieces between start and end positions
            pieces_between = [
                p for p in game_state.pieces
                if p.x == piece.x 
                and start_y < p.y < end_y
                and (p.x != move.to_x or p.y != move.to_y)  # Exclude target position
            ]
            if capturing and len(pieces_between) != 1:
                print(f"Invalid cannon capture: need exactly one piece between, found {len(pieces_between)}")
                return False
            if not capturing and len(pieces_between) > 0:
                print(f"Invalid cannon move: path must be clear for non-capture moves")
                return False
        else:  # Horizontal move
            start_x = min(piece.x, move.to_x)
            end_x = max(piece.x, move.to_x)
            # Count pieces between start and end positions
            pieces_between = [
                p for p in game_state.pieces
                if p.y == piece.y 
                and start_x < p.x < end_x
                and (p.x != move.to_x or p.y != move.to_y)  # Exclude target position
            ]
            if capturing and len(pieces_between) != 1:
                print(f"Invalid cannon capture: need exactly one piece between, found {len(pieces_between)}")
                return False
            if not capturing and len(pieces_between) > 0:
                print(f"Invalid cannon move: path must be clear for non-capture moves")
                return False
            
    elif piece.type == PieceType.SOLDIER:
        # Soldier moves forward one step (or sideways after crossing river)
        print(f"Validating soldier move: from ({piece.x}, {piece.y}) to ({move.to_x}, {move.to_y})")
        
        # Can only move one step
        if abs(move.to_x - piece.x) + abs(move.to_y - piece.y) != 1:
            print("Invalid soldier move: can only move one step")
            return False
            
        if piece.side == Side.RED:
            if move.to_y >= piece.y:  # Must move forward (upward)
                print("Invalid soldier move: RED must move upward (y should decrease)")
                return False
            if piece.y < 5:  # Haven't crossed river
                if move.to_x != piece.x:  # Can only move forward
                    print("Invalid soldier move: RED hasn't crossed river, can only move forward")
                    return False
        else:  # BLACK
            if move.to_y <= piece.y:  # Must move forward (downward)
                print("Invalid soldier move: BLACK must move downward (y should increase)")
                return False
            if piece.y > 4:  # Haven't crossed river
                if move.to_x != piece.x:  # Can only move forward
                    print("Invalid soldier move: BLACK hasn't crossed river, can only move forward")
                    return False
            
    return True

def make_move(game_state: GameState, move: Move) -> GameState:
    """Apply a move to the game state and return the new state"""
    if not game_state:
        raise ValueError("Game state cannot be None")
        
    if not is_valid_move(game_state, move):
        raise ValueError("Invalid move")
        
    try:
        # Create new game state with moved piece
        new_pieces = [p.copy() for p in game_state.pieces]
        new_pieces[move.piece_id].x = move.to_x
        new_pieces[move.piece_id].y = move.to_y
        
        # Remove captured piece if any
        new_pieces = [p for p in new_pieces if not (p.x == move.to_x and p.y == move.to_y) or p == new_pieces[move.piece_id]]
        
        # Check for game over (general captured)
        game_over = False
        winner = None
        generals = [p for p in new_pieces if p.type == PieceType.GENERAL]
        if len(generals) < 2:
            game_over = True
            winner = generals[0].side if generals else None
        
        # Create and return new game state
        return GameState(
            pieces=new_pieces,
            current_turn=Side.BLACK if game_state.current_turn == Side.RED else Side.RED,
            game_over=game_over,
            winner=winner
        )
    except Exception as e:
        raise ValueError(f"Failed to create new game state: {str(e)}")

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
    
    valid_moves = []
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
                    # Use tuple as dictionary key instead of Move object
                    move_key = (move.piece_id, move.to_x, move.to_y)
                    move_scores[move_key] = (score, move)
                    valid_moves.append(move)
    
    if not valid_moves:
        print("No valid moves available for AI")
        return None
    
    
    # Select one of the top 3 moves randomly to add variety
    sorted_moves = sorted(move_scores.items(), key=lambda x: x[1][0], reverse=True)
    top_moves = sorted_moves[:3]
    selected_move = random.choice(top_moves)[1][1]  # Get the Move object from the tuple
    
    print(f"AI chose move: piece_id={selected_move.piece_id}, to=({selected_move.to_x}, {selected_move.to_y})")
    return selected_move
