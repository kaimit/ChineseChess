import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { PieceType, Side, GameState, Piece, Move } from '../types';

interface ChessBoardProps {
  gameState: GameState | null;
  onMove: (move: Move) => void;
  onNewGame: () => void;
}

export const ChessBoard = ({ gameState, onMove, onNewGame }: ChessBoardProps) => {
  const [selectedPiece, setSelectedPiece] = useState<number | null>(null);

  const handleSquareClick = (x: number, y: number) => {
    if (!gameState) return;

    if (selectedPiece === null) {
      // Select piece if it's the player's turn
      const pieceIndex = gameState.pieces.findIndex(
        (p) => p.x === x && p.y === y && p.side === Side.RED
      );
      if (pieceIndex !== -1 && gameState.current_turn === Side.RED) {
        setSelectedPiece(pieceIndex);
        console.log('Selected piece:', gameState.pieces[pieceIndex]);
      }
    } else {
      // Try to move the selected piece
      const selectedPieceData = gameState.pieces[selectedPiece];
      if (selectedPieceData && (selectedPieceData.x !== x || selectedPieceData.y !== (9 - y))) {
        // Transform coordinates: flip y-coordinate since backend uses bottom-left origin
        const transformedY = 9 - y;  // Transform y-coordinate (0-9 -> 9-0)
        console.log('Attempting move:', { 
          piece_id: selectedPiece, 
          from: { x: selectedPieceData.x, y: selectedPieceData.y },
          to: { x, y: transformedY }
        });
        
        // Validate basic soldier movement (can only move forward)
        const isRedPiece = selectedPieceData.side === Side.RED;
        const isForwardMove = isRedPiece ? 
          (transformedY > selectedPieceData.y) : 
          (transformedY < selectedPieceData.y);
        
        if (selectedPieceData.type === PieceType.SOLDIER && !isForwardMove) {
          console.log('Invalid move: Soldiers can only move forward');
          setSelectedPiece(null);
          return;
        }
        
        onMove({ piece_id: selectedPiece, to_x: x, to_y: transformedY });
      } else {
        console.log('Invalid move: Cannot move to the same position');
      }
      setSelectedPiece(null);
    }
  };

  const getPieceSymbol = (piece: Piece): string => {
    const symbols: Record<PieceType, { [key in Side]: string }> = {
      general: { red: '帥', black: '將' },
      advisor: { red: '仕', black: '士' },
      elephant: { red: '相', black: '象' },
      horse: { red: '馬', black: '馬' },
      chariot: { red: '車', black: '車' },
      cannon: { red: '炮', black: '砲' },
      soldier: { red: '兵', black: '卒' },
    };
    return symbols[piece.type][piece.side];
  };

  const renderSquare = (x: number, y: number) => {
    // Transform y-coordinate when finding pieces (backend uses bottom-left origin)
    const piece = gameState?.pieces.find((p) => p.x === x && p.y === (9 - y));
    const isSelected = piece && selectedPiece !== null && gameState?.pieces.findIndex(
      (p) => p.x === piece.x && p.y === piece.y
    ) === selectedPiece;

    return (
      <div
        key={`${x}-${y}`}
        data-testid={`square-${x}-${y}`}
        id={`square-${x}-${y}`}
        data-x={x}
        data-y={y}
        onClick={() => handleSquareClick(x, y)}
        className={`w-12 h-12 border border-gray-400 flex items-center justify-center cursor-pointer
          ${isSelected ? 'bg-blue-300 ring-2 ring-blue-500' : piece ? 'bg-amber-50' : 'bg-amber-100'}
          ${piece?.side === Side.RED ? 'text-red-600' : 'text-gray-800'}
          text-2xl font-bold hover:bg-blue-100 relative transition-all duration-200`}
      >
        {piece && getPieceSymbol(piece)}
        {!piece && <div className="absolute inset-0 hover:bg-blue-50" />}
      </div>
    );
  };

  return (
    <Card className="p-6 bg-amber-100">
      {gameState?.game_over && (
        <Alert className="mb-4">
          <AlertDescription>
            Game Over! Winner: {gameState.winner === Side.RED ? 'Red' : 'Black'}
          </AlertDescription>
        </Alert>
      )}
      
      <div className="grid grid-cols-9 gap-0 border border-gray-400">
        {Array.from({ length: 10 }, (_, y) => (
          <div key={y} className="contents">
            {Array.from({ length: 9 }, (_, x) => renderSquare(x, y))}
          </div>
        ))}
      </div>

      <div className="mt-4 flex justify-between items-center">
        <Button onClick={onNewGame} variant="outline">
          New Game
        </Button>
        <div className="text-lg font-semibold">
          {gameState ? `Current Turn: ${gameState.current_turn === Side.RED ? 'Red' : 'Black'}` : 'Start a new game'}
        </div>
      </div>
    </Card>
  );
};
