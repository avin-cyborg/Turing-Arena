# backend/players/uci_adapter.py

import asyncio
import logging
import os
import shutil
import chess
import chess.engine
from typing import Optional
from .base_player import AIPlayer

logger = logging.getLogger(__name__)


class UCIAdapter(AIPlayer):
    """
    Adapter for a Universal Chess Interface (UCI) engine like Stockfish.
    This adapter runs the engine as a subprocess and communicates with it.
    """

    def __init__(self, name: str, path: str):
        self.name = name
        # If the given path doesn't exist (e.g. .exe on Linux),
        # fall back to searching PATH. This handles local Windows dev
        # vs Linux server (Render) transparently.
        if path and os.path.exists(path):
            self.path = path
        else:
            detected = shutil.which("stockfish")
            if detected:
                logger.info(f"UCIAdapter: '{path}' not found, using detected path: {detected}")
                self.path = detected
            else:
                logger.error(f"UCIAdapter: Stockfish not found at '{path}' or in system PATH.")
                self.path = path  # Keep original so connect() produces a clear error
        self.engine: Optional[chess.engine.SimpleEngine] = None

    async def connect(self):
        """Initializes and connects to the UCI engine subprocess."""
        try:
            transport, engine = await chess.engine.popen_uci(self.path)
            self.engine = engine
            logger.info(f"Successfully connected to UCI engine: {self.name} at {self.path}")
        except FileNotFoundError:
            # Preserved from original — specific message for missing executable
            logger.error(
                f"CRITICAL: Engine executable not found at: {self.path}. "
                f"The UCIAdapter for '{self.name}' will not work."
            )
            self.engine = None
        except Exception as e:
            # Preserved from original — separate handler for other failures
            logger.error(f"Failed to connect to UCI engine {self.name}: {e}", exc_info=True)
            self.engine = None

    async def disconnect(self):
        """Closes the connection to the engine."""
        if self.engine:
            try:
                await self.engine.quit()
                logger.info(f"Disconnected from UCI engine: {self.name}")
            except Exception as e:
                logger.error(f"Error disconnecting from engine {self.name}: {e}")

    async def get_move(self, board: chess.Board, time_limit: float) -> str:
        """
        Gets a move from the UCI engine.
        This method sends the board state and receives the best move from the engine.
        """
        if not self.engine:
            raise RuntimeError(f"Engine '{self.name}' is not connected or failed to initialize.")
        try:
            result = await self.engine.play(board, chess.engine.Limit(time=time_limit))
            if result.move is None:
                raise ValueError("Engine did not return a move.")
            return result.move.uci()
        except Exception as e:
            logger.error(f"Error getting move from engine {self.name}: {e}")
            # Preserved from original — fallback to first legal move if engine fails
            if board.legal_moves:
                return list(board.legal_moves)[0].uci()
            raise RuntimeError("Engine failed and no legal moves are available.")
