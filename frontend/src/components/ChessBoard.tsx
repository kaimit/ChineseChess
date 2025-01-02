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

    console.log(`Square clicked: x=${x}, y=${y}`);

    if (selectedPiece === null) {
      // Select piece if it's the player's turn
      const pieceIndex = gameState.pieces.findIndex(
        (p) => p.x === x && p.y === y && p.side === Side.RED
      );
      if (pieceIndex !== -1 && gameState.current_turn === Side.RED) {
        setSelectedPiece(pieceIndex);
        console.log('Selected piece:', gameState.pieces[pieceIndex]);
      } else {
        console.log('No valid piece found at position:', { x, y });
      }
    } else {
      // Try to move the selected piece
      const selectedPieceData = gameState.pieces[selectedPiece];
      if (selectedPieceData && (selectedPieceData.x !== x || selectedPieceData.y !== y)) {
        console.log('Attempting move:', { 
          piece_id: selectedPiece, 
          from: { x: selectedPieceData.x, y: selectedPieceData.y },
          to: { x, y }
        });
        
        // Let backend handle all move validation
        
        onMove({ piece_id: selectedPiece, to_x: x, to_y: y });
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
        {Array.from({ length: 10 }, (_, i) => {
          const y = 9 - i;  // y=9 at bottom (Red), y=0 at top (Black)
          return (
            <div key={y} className="contents">
              {Array.from({ length: 9 }, (_, x) => {
                const piece = gameState?.pieces.find(p => p.x === x && p.y === y);
                return (
                  <button
                    key={`${x}-${y}`}
                    data-devinid={`square-${x}-${y}`}
                    onClick={() => handleSquareClick(x, y)}
                    className={`w-12 h-12 border border-gray-400 flex items-center justify-center cursor-pointer
                      ${selectedPiece !== null && gameState?.pieces[selectedPiece]?.x === x && gameState?.pieces[selectedPiece]?.y === y ? 'bg-blue-300 ring-2 ring-blue-500' : 'bg-amber-50'}
                      hover:bg-blue-100 relative transition-all duration-200`}
                  >
                    {piece && (
                      <span className={`text-2xl font-bold ${piece.side === Side.RED ? 'text-red-600' : 'text-gray-800'}`}>
                        {getPieceSymbol(piece)}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          );
        })}
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
