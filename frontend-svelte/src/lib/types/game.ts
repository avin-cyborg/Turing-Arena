export type GameStatus = 'idle' | 'loading' | 'playing' | 'finished';
export type PlayerColor = 'white' | 'black';
export type PlayerType = 'ai' | 'human'; // For future expansion

export interface Player {
  name: string;
  type: PlayerType;
  color?: PlayerColor;
  avatar?: string; // For future UI enhancement
  rating?: number; // For future leaderboard
}

export interface Move {
  from: string;
  to: string;
  san: string; // Standard Algebraic Notation
  timestamp: number;
}

export interface GameState {
  gameId: string | null;
  status: GameStatus;
  fen: string;
  turn: PlayerColor;
  players: {
    white: Player;
    black: Player;
  };
  moveHistory: Move[];
  commentary: string;
  aiReasoning: {
    white: string;
    black: string;
  };
  result?: {
    winner: string;
    outcome: string;
  };
}
