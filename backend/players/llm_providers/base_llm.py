# backend/players/llm_providers/base_llm.py

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import chess

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    Ensures consistent interface across different AI models.
    """

    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        self.request_count = 0
        self.error_count = 0

    @abstractmethod
    async def generate_move(
        self,
        board: chess.Board,
        move_history: List[str],
        thinking_time: float,
    ) -> Dict[str, str]:
        """
        Generate a chess move using the LLM.

        Returns:
            Dict with 'move' (UCI format) and 'reasoning' (explanation)
        """
        pass

    def create_chess_prompt(
        self,
        board: chess.Board,
        move_history: List[str],
    ) -> str:
        """
        Creates a prompt for the LLM with board state and strict output rules.
        """
        color = "White" if board.turn else "Black"
        legal_moves = [move.uci() for move in board.legal_moves]
        history_str = " ".join(move_history) if move_history else "Starting position"

        status = ""
        if board.is_checkmate():
            status = "CHECKMATE - Game Over!"
        elif board.is_check():
            status = "You are in CHECK!"
        elif board.is_stalemate():
            status = "STALEMATE - Game Over!"

        prompt = f"""You are an expert chess player playing as {color}.

Current Position (FEN): {board.fen()}
Move History: {history_str}
Game Status: {status if status else "Normal play"}
Your Legal Moves (UCI): {', '.join(legal_moves[:20])}{'...' if len(legal_moves) > 20 else ''}

Respond with ONLY a JSON object. Follow these rules exactly:
- No markdown, no code fences, no backticks, no extra text before or after
- reasoning must be 15 words or fewer
- move must be from the legal moves list above, in lowercase UCI format

{{"move": "e2e4", "reasoning": "Controls the center and opens lines for bishops."}}

Your move:"""

        return prompt

    @staticmethod
    def _strip_fences(text: str) -> str:
        """
        Removes markdown code fences that models add despite being told not to.

        Handles all of:
          ```json { ... } ```
          ``` { ... } ```
          `{ ... }`
        """
        # Strip triple-backtick fences with optional language tag
        text = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.IGNORECASE)
        text = re.sub(r'\s*```$', '', text.strip())
        # Strip single backticks
        text = text.strip('`').strip()
        return text

    @staticmethod
    def _extract_reasoning_from_partial(text: str) -> Optional[str]:
        """
        Tries to recover the reasoning string from a truncated JSON response.

        Example truncated input:
            {"move": "c7c5", "reasoning": "The Sicilian Defense is one of the most

        Returns the partial reasoning string, or None if it can't be found.
        """
        match = re.search(r'"reasoning"\s*:\s*"([^"]*)', text)
        if match:
            partial = match.group(1).strip()
            if partial:
                # Signal that this was truncated
                return partial + "…" if not partial.endswith("…") else partial
        return None

    def validate_and_extract_move(
        self,
        response: str,
        board: chess.Board,
    ) -> Dict[str, str]:
        """
        Validates LLM response and extracts the move.

        Handles:
          - Clean JSON responses
          - JSON wrapped in markdown code fences (```json ... ```)
          - Truncated JSON (MAX_TOKENS cutoff mid-reasoning)
          - Completely non-JSON responses (last-resort regex)

        Returns:
            Dict with 'move' (UCI) and 'reasoning'

        Raises:
            ValueError: If no valid legal move can be extracted
        """
        move_uci: Optional[str] = None
        reasoning: Optional[str] = None

        # ----------------------------------------------------------------
        # Pass 1: Try JSON parsing, with and without fence stripping
        # ----------------------------------------------------------------
        for candidate_text in (response, self._strip_fences(response)):
            try:
                data = json.loads(candidate_text)
                move_uci = data.get('move', '').strip().lower()
                reasoning = data.get('reasoning', 'No reasoning provided')
                break
            except json.JSONDecodeError:
                continue

        # ----------------------------------------------------------------
        # Pass 2: Truncated JSON — model wrote valid JSON but it was cut off
        # mid-reasoning. The move field is usually emitted before reasoning,
        # so we can still recover it via regex.
        # ----------------------------------------------------------------
        if move_uci is None:
            logger.warning(f"JSON parse failed. Raw response: {response!r}")

            uci_pattern = r'"move"\s*:\s*"([a-h][1-8][a-h][1-8][qrbn]?)"'
            match = re.search(uci_pattern, response.lower())
            if match:
                move_uci = match.group(1)
                # Try to salvage whatever reasoning was generated before the cutoff
                reasoning = self._extract_reasoning_from_partial(response) or "Reasoning truncated"
                logger.warning(f"Recovered move '{move_uci}' from truncated JSON")

        # ----------------------------------------------------------------
        # Pass 3: No JSON structure at all — bare UCI move anywhere in text
        # ----------------------------------------------------------------
        if move_uci is None:
            match = re.search(r'\b([a-h][1-8][a-h][1-8][qrbn]?)\b', response.lower())
            if match:
                move_uci = match.group(1)
                reasoning = "Extracted from unstructured response"
                logger.warning(f"Last-resort UCI extraction: '{move_uci}'")

        if move_uci is None:
            raise ValueError(f"No valid UCI move found in response: {response!r}")

        # ----------------------------------------------------------------
        # Legality check
        # ----------------------------------------------------------------
        try:
            move = chess.Move.from_uci(move_uci)
            if move not in board.legal_moves:
                raise ValueError(f"Move {move_uci} is not legal in current position")
        except ValueError as e:
            raise ValueError(f"Invalid move '{move_uci}': {e}") from e

        return {
            'move': move_uci,
            'reasoning': reasoning or 'No reasoning provided',
        }

    def get_stats(self) -> Dict[str, int]:
        """Returns provider statistics"""
        return {
            'requests': self.request_count,
            'errors': self.error_count,
            'success_rate': (
                (self.request_count - self.error_count) / max(self.request_count, 1)
            ) * 100,
        }
