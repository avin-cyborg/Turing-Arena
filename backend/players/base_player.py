# backend/players/base_player.py
from typing import Protocol
import chess

class AIPlayer(Protocol):
    """
    Protocol for a chess AI player. All AI adapters must conform to this interface.
    This is the key to our modular, "pluggable" AI architecture.
    """
    name: str

    async def get_move(self, board: chess.Board, time_limit: float) -> str:
        """
        Requests a move from the AI.

        Args:
            board (chess.Board): The current state of the game board.
            time_limit (float): The maximum time in seconds the AI has to think.

        Returns:
            str: The move in UCI format (e.g., 'e2e4').
        """
        ...
