export interface APIResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface StartGameResponse {
  game_id: string;
  status: string;
  players?: {
    white: string;
    black: string;
  };
}

export interface GameHistoryResponse {
  games: GameRecord[];
  total: number;
  page: number;
}

export interface GameRecord {
  gameId: string;
  players: {
    white: string;
    black: string;
  };
  result: string;
  winner: string;
  moves: number;
  timestamp: number;
}

export interface LeaderboardEntry {
  rank: number;
  playerId: string;
  playerName: string;
  rating: number;
  gamesPlayed: number;
  winRate: number;
}
