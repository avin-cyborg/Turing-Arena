import React, { useReducer, useEffect, useRef } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { Toaster, toast } from 'sonner';

import { PlayerCard } from './components/PlayerCard';
import { GameControls } from './components/GameControls';
import { GameLog } from './components/GameLog';

// --- TYPE DEFINITIONS ---
type GameMessage = {
  type: 'game_start' | 'game_update' | 'game_over';
  fen: string;
  last_move: string | null;
  turn: 'white' | 'black';
  ai_reasoning?: string;
  commentary_text?: string;
  result?: string;
  winner?: string;
  game_id?: string;
  players?: { white: string; black: string };
};

// 1. DEFINE THE SHAPE OF OUR COMBINED STATE
interface GameState {
  fen: string;
  gameStatus: 'idle' | 'loading' | 'playing' | 'over';
  gameId: string | null;
  reasoning: { white: string; black: string };
  commentary: string;
  players: { white: string; black: string };
  history: string[];
  lastMove: { from: string; to: string } | null;
}

// 2. DEFINE THE ACTIONS THAT CAN CHANGE THE STATE
type GameAction =
  | { type: 'NEW_GAME_REQUEST' }
  | { type: 'GAME_STARTED'; payload: { game_id: string; players: { white: string; black: string } } }
  | { type: 'UPDATE_GAME'; payload: GameMessage }
  | { type: 'GAME_OVER'; payload: GameMessage };

// --- INITIAL STATE ---
// All our initial states are now in one place.
const initialState: GameState = {
  fen: new Chess().fen(),
  gameStatus: 'idle',
  gameId: null,
  reasoning: { white: '', black: '' },
  commentary: '',
  players: { white: 'Gemini', black: 'Stockfish' },
  history: [],
  lastMove: null,
};

// 3. CREATE THE REDUCER FUNCTION
// This single function handles all state updates, preventing stale state.
function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'NEW_GAME_REQUEST':
      // When a new game is requested, reset everything to the initial state
      return {
        ...initialState,
        gameStatus: 'loading',
        commentary: 'Starting new game...',
      };
    case 'GAME_STARTED':
      toast.success("Game Started!", { description: "The AI tournament is underway." });
      return {
        ...state,
        gameStatus: 'playing',
        gameId: action.payload.game_id,
        players: action.payload.players,
      };
    case 'UPDATE_GAME':
      const lastTurn = action.payload.turn === 'white' ? 'black' : 'white';
      return {
        ...state,
        fen: action.payload.fen,
        commentary: action.payload.commentary_text || '',
        history: action.payload.last_move ? [...state.history, action.payload.last_move] : state.history,
        lastMove: action.payload.last_move ? { from: action.payload.last_move.slice(0, 2), to: action.payload.last_move.slice(2, 4) } : null,
        reasoning: action.payload.ai_reasoning ? { ...state.reasoning, [lastTurn]: action.payload.ai_reasoning } : state.reasoning,
      };
    case 'GAME_OVER':
      toast.info("Game Over", { description: `The match has concluded. ${action.payload.winner} wins!` });
      return {
        ...state,
        gameStatus: 'over',
        commentary: `Game Over! Result: ${action.payload.result}. Winner: ${action.payload.winner}`,
      };
    default:
      return state;
  }
}

// --- MAIN APPLICATION COMPONENT ---
export default function App() {
  // 4. REPLACE ALL 'useState' HOOKS WITH A SINGLE 'useReducer'
  const [state, dispatch] = useReducer(gameReducer, initialState);
  const ws = useRef<WebSocket | null>(null);

  // --- WEBSOCKET CONNECTION EFFECT ---
  useEffect(() => {
    if (state.gameStatus === 'playing' && state.gameId) {
      const wsUrl = `ws://${window.location.hostname}:8000/ws/${state.gameId}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => console.log(`WebSocket connection opened for game: ${state.gameId}`);

      ws.current.onmessage = (event) => {
        try {
          const message: GameMessage = JSON.parse(event.data);
          // Instead of many 'set' functions, we dispatch a single, clear action.
          if (message.type === 'game_update') {
            dispatch({ type: 'UPDATE_GAME', payload: message });
          } else if (message.type === 'game_over') {
            dispatch({ type: 'GAME_OVER', payload: message });
          }
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      ws.current.onclose = () => console.log(`WebSocket connection closed for game: ${state.gameId}`);
      ws.current.onerror = (error) => {
        console.error("WebSocket error:", error);
        toast.error("Connection Error", { description: "Lost connection to the server." });
      };

      // Cleanup function remains the same
      return () => {
        ws.current?.close();
      };
    }
  }, [state.gameId, state.gameStatus]); // Depend on gameId and status

  // --- HANDLER FOR STARTING A NEW GAME ---
  const handleStartGame = async (whitePlayer: string, blackPlayer: string) => {
    dispatch({ type: 'NEW_GAME_REQUEST' });

    try {
      const response = await fetch(`/start_game?white_player=${whitePlayer}&black_player=${blackPlayer}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to start game on the backend.');

      const data = await response.json();
      // The backend response triggers the 'GAME_STARTED' action.
      dispatch({ type: 'GAME_STARTED', payload: { game_id: data.game_id, players: { white: whitePlayer, black: blackPlayer } } });

    } catch (error) {
      console.error("Error starting game:", error);
      toast.error("Error", { description: "Failed to start a new game. Please check the backend server." });
    }
  };

  // --- RENDER THE UI ---
  // The UI now reads everything from our single 'state' object.
  return (
    <div className="flex flex-col lg:flex-row h-screen bg-gray-900 text-gray-200 p-4 lg:p-8 gap-4 lg:gap-8 justify-center items-center font-sans">
      <Toaster richColors position="top-right" />

      <div className="w-full lg:w-1/4 h-full flex flex-col gap-4">
        <PlayerCard
          playerColor="White"
          playerName={state.players.white}
          reasoning={state.reasoning.white}
        />
        <GameLog history={state.history} />
      </div>

      <div className="w-full lg:w-1/2 flex flex-col items-center gap-4">
        <div className="w-full max-w-[80vw] lg:max-w-[60vh] aspect-square">
          <Chessboard
            key={state.fen} // The key prop is still our ultimate failsafe for forcing re-renders.
            position={state.fen}
            arePiecesDraggable={false}
            customBoardStyle={{ borderRadius: '8px', boxShadow: '0 5px 15px rgba(0, 0, 0, 0.5)' }}
            customDarkSquareStyle={{ backgroundColor: '#769656' }}
            customLightSquareStyle={{ backgroundColor: '#eeeed2' }}
            customSquareStyles={state.lastMove ? { [state.lastMove.from]: { backgroundColor: 'rgba(255, 255, 0, 0.4)' }, [state.lastMove.to]: { backgroundColor: 'rgba(255, 255, 0, 0.4)' } } : {}}
          />
        </div>
        <GameControls
          gameStatus={state.gameStatus}
          onStartGame={handleStartGame}
          commentary={state.commentary}
        />
      </div>

      <div className="w-full lg:w-1/4 h-full flex flex-col">
        <PlayerCard
          playerColor="Black"
          playerName={state.players.black}
          reasoning={state.reasoning.black}
        />
      </div>
    </div>
  );
}

