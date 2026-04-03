/**
 * Chess utility functions for FEN parsing, move validation, and board manipulation
 */

export interface Square {
  file: string;
  rank: string;
}

export interface ParsedMove {
  from: Square;
  to: Square;
  piece: string;
  capture: boolean;
  promotion?: string;
}

/**
 * Convert UCI move format (e.g., "e2e4") to readable format
 */
export function uciToReadable(uci: string): string {
  if (!uci || uci.length < 4) return uci;
  
  const from = uci.substring(0, 2);
  const to = uci.substring(2, 4);
  const promotion = uci.length > 4 ? uci[4].toUpperCase() : '';
  
  return `${from}-${to}${promotion}`;
}

/**
 * Parse FEN string into components
 */
export function parseFEN(fen: string): {
  position: string;
  turn: 'white' | 'black';
  castling: string;
  enPassant: string;
  halfmove: number;
  fullmove: number;
} {
  const parts = fen.split(' ');
  
  return {
    position: parts[0] || '',
    turn: parts[1] === 'b' ? 'black' : 'white',
    castling: parts[2] || '-',
    enPassant: parts[3] || '-',
    halfmove: parseInt(parts[4] || '0'),
    fullmove: parseInt(parts[5] || '1')
  };
}

/**
 * Convert algebraic notation to board coordinates
 * e.g., "e4" -> { file: 4, rank: 3 } (0-indexed)
 */
export function algebraicToCoords(square: string): { file: number; rank: number } {
  const file = square.charCodeAt(0) - 97; // 'a' = 0, 'b' = 1, etc.
  const rank = 8 - parseInt(square[1]); // '8' = 0, '7' = 1, etc.
  
  return { file, rank };
}

/**
 * Convert board coordinates to algebraic notation
 * e.g., { file: 4, rank: 3 } -> "e4"
 */
export function coordsToAlgebraic(file: number, rank: number): string {
  const fileChar = String.fromCharCode(97 + file);
  const rankChar = (8 - rank).toString();
  
  return fileChar + rankChar;
}

/**
 * Get piece symbol from FEN character
 */
export function getPieceSymbol(fenChar: string): string {
  const symbols: Record<string, string> = {
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'
  };
  
  return symbols[fenChar] || '';
}

/**
 * Get piece name from FEN character
 */
export function getPieceName(fenChar: string): string {
  const names: Record<string, string> = {
    'p': 'pawn', 'r': 'rook', 'n': 'knight', 
    'b': 'bishop', 'q': 'queen', 'k': 'king',
    'P': 'pawn', 'R': 'rook', 'N': 'knight',
    'B': 'bishop', 'Q': 'queen', 'K': 'king'
  };
  
  return names[fenChar] || 'unknown';
}

/**
 * Check if a piece is white
 */
export function isWhitePiece(fenChar: string): boolean {
  return fenChar === fenChar.toUpperCase();
}

/**
 * Format move for display (convert UCI to SAN-like format)
 */
export function formatMove(uci: string, piece?: string): string {
  if (!uci) return '';
  
  const from = uci.substring(0, 2);
  const to = uci.substring(2, 4);
  const promotion = uci.length > 4 ? `=${uci[4].toUpperCase()}` : '';
  
  if (piece) {
    const pieceName = getPieceName(piece);
    return `${pieceName[0].toUpperCase()}${to}${promotion}`;
  }
  
  return `${to}${promotion}`;
}

/**
 * Calculate elapsed time between moves
 */
export function getElapsedTime(startTime: number, endTime: number): string {
  const elapsed = Math.floor((endTime - startTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  
  return minutes > 0 
    ? `${minutes}m ${seconds}s`
    : `${seconds}s`;
}

/**
 * Validate square notation
 */
export function isValidSquare(square: string): boolean {
  return /^[a-h][1-8]$/.test(square);
}

/**
 * Validate UCI move format
 */
export function isValidUCI(uci: string): boolean {
  return /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(uci);
}
