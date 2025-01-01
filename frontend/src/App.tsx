import { useState, useEffect } from 'react';
import { ChessBoard } from './components/ChessBoard';
import { GameState, Move } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);

  const handleNewGame = async () => {
    try {
      const response = await fetch(`${API_URL}/api/new-game`, {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        setGameState(data);
      }
    } catch (error) {
      console.error('Error starting new game:', error);
    }
  };

  const handleMove = async (move: Move) => {
    try {
      const response = await fetch(`${API_URL}/api/move`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(move),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        alert(data.detail || 'Invalid move');
        return;
      }
      
      setGameState(data);
      
      // Check for game over after move
      if (data.game_over) {
        const winner = data.winner ? `${data.winner.toUpperCase()} wins!` : 'Draw!';
        alert(`Game Over! ${winner}`);
      }
    } catch (error) {
      console.error('Error making move:', error);
      alert('Failed to make move. Please try again.');
    }
  };

  useEffect(() => {
    handleNewGame();
  }, []);

  // Log game state changes for debugging
  useEffect(() => {
    console.log('Game state updated:', gameState);
  }, [gameState]);

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center mb-8">Chinese Chess</h1>
        <div className="flex justify-center">
          <ChessBoard
            gameState={gameState}
            onMove={handleMove}
            onNewGame={handleNewGame}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
