export enum PieceType {
  GENERAL = "general",
  ADVISOR = "advisor",
  ELEPHANT = "elephant",
  HORSE = "horse",
  CHARIOT = "chariot",
  CANNON = "cannon",
  SOLDIER = "soldier"
}

export enum Side {
  RED = "red",
  BLACK = "black"
}

export interface Piece {
  type: PieceType;
  side: Side;
  x: number;
  y: number;
}

export interface GameState {
  pieces: Piece[];
  current_turn: Side;
  game_over: boolean;
  winner: Side | null;
}

export interface Move {
  piece_id: number;
  to_x: number;
  to_y: number;
}
