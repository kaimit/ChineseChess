from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel

class PieceType(str, Enum):
    GENERAL = "general"  # 将/帅
    ADVISOR = "advisor"  # 士/仕
    ELEPHANT = "elephant"  # 象/相
    HORSE = "horse"  # 马
    CHARIOT = "chariot"  # 车
    CANNON = "cannon"  # 炮
    SOLDIER = "soldier"  # 兵/卒

class Side(str, Enum):
    RED = "red"
    BLACK = "black"

class Piece(BaseModel):
    type: PieceType
    side: Side
    x: int  # 0-8 (9 columns)
    y: int  # 0-9 (10 rows)

class GameState(BaseModel):
    pieces: List[Piece]
    current_turn: Side
    game_over: bool = False
    winner: Optional[Side] = None

    @classmethod
    def new_game(cls) -> "GameState":
        """Create a new game with pieces in their initial positions"""
        pieces = []
        
        # Initialize pieces for both sides
        def add_piece(piece_type: PieceType, side: Side, x: int, y: int):
            pieces.append(Piece(type=piece_type, side=side, x=x, y=y))

        # Red side (bottom)
        add_piece(PieceType.GENERAL, Side.RED, 4, 9)
        add_piece(PieceType.ADVISOR, Side.RED, 3, 9)
        add_piece(PieceType.ADVISOR, Side.RED, 5, 9)
        add_piece(PieceType.ELEPHANT, Side.RED, 2, 9)
        add_piece(PieceType.ELEPHANT, Side.RED, 6, 9)
        add_piece(PieceType.HORSE, Side.RED, 1, 9)
        add_piece(PieceType.HORSE, Side.RED, 7, 9)
        add_piece(PieceType.CHARIOT, Side.RED, 0, 9)
        add_piece(PieceType.CHARIOT, Side.RED, 8, 9)
        add_piece(PieceType.CANNON, Side.RED, 1, 7)
        add_piece(PieceType.CANNON, Side.RED, 7, 7)
        for x in [0, 2, 4, 6, 8]:
            add_piece(PieceType.SOLDIER, Side.RED, x, 6)

        # Black side (top)
        add_piece(PieceType.GENERAL, Side.BLACK, 4, 0)
        add_piece(PieceType.ADVISOR, Side.BLACK, 3, 0)
        add_piece(PieceType.ADVISOR, Side.BLACK, 5, 0)
        add_piece(PieceType.ELEPHANT, Side.BLACK, 2, 0)
        add_piece(PieceType.ELEPHANT, Side.BLACK, 6, 0)
        add_piece(PieceType.HORSE, Side.BLACK, 1, 0)
        add_piece(PieceType.HORSE, Side.BLACK, 7, 0)
        add_piece(PieceType.CHARIOT, Side.BLACK, 0, 0)
        add_piece(PieceType.CHARIOT, Side.BLACK, 8, 0)
        add_piece(PieceType.CANNON, Side.BLACK, 1, 2)
        add_piece(PieceType.CANNON, Side.BLACK, 7, 2)
        for x in [0, 2, 4, 6, 8]:
            add_piece(PieceType.SOLDIER, Side.BLACK, x, 3)

        return cls(pieces=pieces, current_turn=Side.RED)

class Move(BaseModel):
    piece_id: int  # Index in the pieces list
    to_x: int
    to_y: int
