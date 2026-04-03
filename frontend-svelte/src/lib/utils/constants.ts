/**
 * Application-wide constants
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  WS_URL: 'ws://localhost:8000',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3
} as const;

// Game Configuration
export const GAME_CONFIG = {
  INITIAL_FEN: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
  MOVE_ANIMATION_DURATION: 300, // ms
  THINKING_INDICATOR_DELAY: 500 // ms
} as const;

// Available AI Players
export const AI_PLAYERS = [
  'Stockfish',
  'Gemini',
  'GPT-4',
  'Claude',
  'AlphaZero'
] as const;

// Game Status Messages
export const STATUS_MESSAGES = {
  IDLE: 'Ready to start',
  LOADING: 'Initializing game...',
  PLAYING: 'Game in progress',
  FINISHED: 'Game finished',
  ERROR: 'An error occurred'
} as const;

// WebSocket Event Types
export const WS_EVENTS = {
  GAME_START: 'game_start',
  GAME_UPDATE: 'game_update',
  GAME_OVER: 'game_over',
  ERROR: 'error'
} as const;

// Local Storage Keys (for future features)
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'chess_user_preferences',
  GAME_HISTORY: 'chess_game_history',
  THEME: 'chess_theme'
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  CONNECTION_FAILED: 'Failed to connect to server',
  GAME_START_FAILED: 'Failed to start game',
  INVALID_MOVE: 'Invalid move',
  NETWORK_ERROR: 'Network error occurred'
} as const;

// Future: Rating Tiers for Leaderboard
export const RATING_TIERS = [
  { min: 0, max: 1199, name: 'Beginner', color: '#8B4513' },
  { min: 1200, max: 1599, name: 'Intermediate', color: '#CD7F32' },
  { min: 1600, max: 1999, name: 'Advanced', color: '#C0C0C0' },
  { min: 2000, max: 2399, name: 'Expert', color: '#FFD700' },
  { min: 2400, max: 9999, name: 'Master', color: '#E5E4E2' }
] as const;
