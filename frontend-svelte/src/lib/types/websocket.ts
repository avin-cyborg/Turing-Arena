// Matches your backend's message format exactly
export type GameMessageType = 'game_start' | 'game_update' | 'game_over';

export interface GameStartMessage {
  type: 'game_start';
  game_id: string;
  fen: string;
  players: {
    white: string;
    black: string;
  };
  status: string;
}

export interface GameUpdateMessage {
  type: 'game_update';
  fen: string;
  last_move: string;
  turn: 'white' | 'black';
  ai_reasoning?: string;
  commentary_text?: string;
}

export interface GameOverMessage {
  type: 'game_over';
  result: string;
  winner: string;
  fen: string;
}

export type GameMessage = GameStartMessage | GameUpdateMessage | GameOverMessage;
