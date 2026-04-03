const API_BASE = 'http://localhost:8000';

export interface StartGameRequest {
  white_player: string;
  black_player: string;
}

export interface StartGameResponse {
  game_id: string;
  status: string;
}

export async function startNewGame(
  whitePlayer: string,
  blackPlayer: string
): Promise<StartGameResponse> {
  const response = await fetch(`${API_BASE}/start_game`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      white_player: whitePlayer,
      black_player: blackPlayer
    })
  });

  if (!response.ok) {
    throw new Error(`Failed to start game: ${response.statusText}`);
  }

  return response.json();
}

// Future: Leaderboard API calls
export async function getLeaderboard() {
  // Placeholder for future implementation
  return [];
}

// Future: Match history
export async function getMatchHistory(playerId: string) {
  // Placeholder for future implementation
  return [];
}

