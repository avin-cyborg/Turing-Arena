# backend/players/llm_providers/gemini_provider.py

import asyncio
import logging
import os
from typing import Dict, List
import chess
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .base_llm import BaseLLMProvider

logger = logging.getLogger(__name__)

# Gemini finish_reason codes
# 1 = STOP        — normal completion
# 2 = MAX_TOKENS  — output truncated (NOT a safety block)
# 3 = SAFETY      — actually blocked by safety filters
# 4 = RECITATION  — blocked for copyright reasons
# 5 = OTHER       — catch-all
_FINISH_REASON_NAMES = {
    1: "STOP",
    2: "MAX_TOKENS",
    3: "SAFETY",
    4: "RECITATION",
    5: "OTHER",
}

_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]


class GeminiProvider(BaseLLMProvider):
    """Google Gemini AI provider"""

    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash"):
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        super().__init__(model_name, api_key)

        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                # Prompt now enforces ≤15-word reasoning, so the full
                # JSON response is ~50 tokens. 256 is the safe floor;
                # 512 gives comfortable headroom for longer UCI moves
                # (e.g. promotion) and any model verbosity drift.
                "max_output_tokens": 512,
                "response_mime_type": "text/plain",
            },
            safety_settings=_SAFETY_SETTINGS,
        )

        logger.info(f"Gemini provider initialized with model: {model_name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # Only retry on genuine errors, not on our own ValueErrors for bad moves.
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def generate_move(
        self,
        board: chess.Board,
        move_history: List[str],
        thinking_time: float,
    ) -> Dict[str, str]:
        """Generate a move using Gemini API with retry logic."""
        self.request_count += 1

        try:
            prompt = self.create_chess_prompt(board, move_history)
            logger.info(f"Gemini: Requesting move for position {board.fen()[:30]}...")

            # FIX: generate_content() is synchronous. Calling it directly inside
            # an async function blocks the entire FastAPI event loop until Gemini
            # responds. asyncio.to_thread() runs it in a thread pool instead,
            # keeping the event loop free for other games/WebSocket messages.
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                # Safety settings passed here override model-level defaults;
                # keeping both ensures they apply regardless of SDK version.
                safety_settings=_SAFETY_SETTINGS,
            )

            # --- Response validation ---

            if not response.candidates:
                # This is a true hard block (e.g. prompt-level safety rejection).
                raise ValueError("Gemini returned no candidates — prompt may have been blocked")

            candidate = response.candidates[0]
            finish_reason = candidate.finish_reason
            finish_name = _FINISH_REASON_NAMES.get(finish_reason, f"UNKNOWN({finish_reason})")

            logger.debug(f"Gemini finish_reason: {finish_reason} ({finish_name})")

            if finish_reason == 3:
                # Actual safety block. Retrying won't help — raise clearly.
                logger.error(f"Gemini SAFETY block. Ratings: {candidate.safety_ratings}")
                raise ValueError(f"Gemini response blocked by safety filters (finish_reason=SAFETY)")

            if finish_reason == 2:
                # MAX_TOKENS — output was truncated, NOT a safety block.
                # The JSON may be incomplete, but validate_and_extract_move has
                # a regex fallback that can recover a UCI move from partial text.
                logger.warning(
                    "Gemini hit MAX_TOKENS — response truncated. "
                    "Attempting to extract move from partial output. "
                    "If this happens often, increase max_output_tokens further."
                )

            if finish_reason not in (1, 2):
                # RECITATION (4) or OTHER (5) — neither retriable nor recoverable.
                raise ValueError(
                    f"Gemini response ended with unrecoverable reason: {finish_name}"
                )

            # Extract text
            if not candidate.content or not candidate.content.parts:
                raise ValueError("Gemini response has no content parts")

            response_text = candidate.content.parts[0].text.strip()
            logger.debug(f"Gemini raw response: {response_text}")

            # validate_and_extract_move handles both clean JSON and partial/truncated
            # output via its regex fallback — see base_llm.py
            result = self.validate_and_extract_move(response_text, board)
            logger.info(f"Gemini chose: {result['move']} — {result['reasoning'][:80]}...")

            return result

        except Exception as e:
            self.error_count += 1
            logger.error(f"Gemini API error: {str(e)}")
            raise
