import { writable } from 'svelte/store';
import type { GameState, PlayerColor } from '$lib/types/game';

const initialState: GameState = {
  gameId: null,
  status: 'idle',
  fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
  turn: 'white',
  players: {
    white: { name: 'Stockfish', type: 'ai' },
    black: { name: 'Gemini', type: 'ai' }
  },
  moveHistory: [],
  commentary: '',
  aiReasoning: { white: '', black: '' }
};

function createGameStore() {
  const { subscribe, set, update } = writable<GameState>(initialState);

  return {
    subscribe,
    reset: () => set(initialState),
    
    startGame: (gameId: string, players: { white: string; black: string }) => {
      update(state => ({
        ...state,
        gameId,
        status: 'playing',
        players: {
          white: { name: players.white, type: 'ai', color: 'white' },
          black: { name: players.black, type: 'ai', color: 'black' }
        }
      }));
    },

    updateBoard: (fen: string, lastMove: string, turn: PlayerColor) => {
      update(state => {
        const newMove = lastMove ? {
          from: lastMove.substring(0, 2),
          to: lastMove.substring(2, 4),
          san: lastMove, // You can enhance this with chess.js
          timestamp: Date.now()
        } : null;

        return {
          ...state,
          fen,
          turn,
          moveHistory: newMove ? [...state.moveHistory, newMove] : state.moveHistory
        };
      });
    },

    setCommentary: (text: string) => {
      update(state => ({ ...state, commentary: text }));
    },

    setReasoning: (color: PlayerColor, reasoning: string) => {
      update(state => ({
        ...state,
        aiReasoning: { ...state.aiReasoning, [color]: reasoning }
      }));
    },

    endGame: (winner: string, outcome: string) => {
      update(state => ({
        ...state,
        status: 'finished',
        result: { winner, outcome }
      }));
    }
  };
}

export const gameStore = createGameStore();
