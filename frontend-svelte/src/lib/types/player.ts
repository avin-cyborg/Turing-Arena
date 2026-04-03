export type PlayerType = 'ai' | 'human';
export type PlayerColor = 'white' | 'black';
export type AIModel = 'Stockfish' | 'Gemini' | 'GPT-4' | 'Claude' | 'AlphaZero';

export interface Player {
  id?: string;
  name: string;
  type: PlayerType;
  color?: PlayerColor;
  avatar?: string;
  rating?: number;
  model?: AIModel;
}

export interface PlayerStats {
  playerId: string;
  gamesPlayed: number;
  wins: number;
  losses: number;
  draws: number;
  rating: number;
  winRate: number;
}

export interface AIConfig {
  name: string;
  model: AIModel;
  thinkingTime: number; // seconds
  difficulty?: 'easy' | 'medium' | 'hard';
}
