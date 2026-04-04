# backend/players/llm_providers/gemini_provider.py

import asyncio
import logging
import os
from typing import Dict, List
import chess
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .base_llm import BaseLLMProvider

logger = logging.getLogger(__name__)

# In the new google-genai SDK, finish_reason is an enum with string names.
# Mapping them here mirrors the old numeric mapping for consistent log messages.
_ACCEPTABLE_FINISH_REASONS = {"STOP", "MAX_TOKENS"}


class GeminiProvider(BaseLLMProvider):
    """Google Gemini AI provider — uses google-genai SDK (google.generativeai is deprecated)"""

    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash"):
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        super().__init__(model_name, api_key)

        # New SDK uses a client instance instead of module-level configure()
        self.client = genai.Client(api_key=self.api_key)

        logger.info(f"Gemini provider initialized with model: {model_name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def generate_move(
        self,
        board: chess.Board,
        move_history: List[str],
        thinking_time: float,
    ) -> Dict[str, str]:
        """Generate a move using the new google-genai SDK with full finish_reason handling."""
        self.request_count += 1

        try:
            prompt = self.create_chess_prompt(board, move_history)
            logger.info(f"Gemini: Requesting move for position {board.fen()[:30]}...")

            # generate_content is synchronous — run in thread pool to avoid
            # blocking the FastAPI event loop (same fix as before, still needed)
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=512,
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_NONE"
                        ),
                    ]
                )
            )

            # --- Response validation (mirrors old logic exactly) ---

            if not response.candidates:
                raise ValueError("Gemini returned no candidates — prompt may have been blocked")

            candidate = response.candidates[0]

            # In new SDK, finish_reason is an enum — get its string name
            finish_reason = candidate.finish_reason.name if candidate.finish_reason else "UNKNOWN"
            logger.debug(f"Gemini finish_reason: {finish_reason}")

            if finish_reason == "SAFETY":
                # Actual safety block. Retrying won't help.
                logger.error(f"Gemini SAFETY block. Ratings: {candidate.safety_ratings}")
                raise ValueError("Gemini response blocked by safety filters (finish_reason=SAFETY)")

            if finish_reason == "MAX_TOKENS":
                # Output truncated — NOT a safety block.
                # validate_and_extract_move has regex fallback to recover partial JSON.
                logger.warning(
                    "Gemini hit MAX_TOKENS — response truncated. "
                    "Attempting to extract move from partial output. "
                    "If this happens often, increase max_output_tokens further."
                )

            if finish_reason not in _ACCEPTABLE_FINISH_REASONS:
                # RECITATION or OTHER — not recoverable, don't retry
                raise ValueError(
                    f"Gemini response ended with unrecoverable reason: {finish_reason}"
                )

            # Safe content extraction — check parts exist before accessing
            # (mirrors old: if not candidate.content or not candidate.content.parts)
            if not candidate.content or not candidate.content.parts:
                raise ValueError("Gemini response has no content parts")

            response_text = candidate.content.parts[0].text.strip()
            logger.debug(f"Gemini raw response: {response_text}")

            # validate_and_extract_move handles clean JSON, fenced JSON,
            # truncated JSON, and bare UCI — see base_llm.py
            result = self.validate_and_extract_move(response_text, board)
            logger.info(f"Gemini chose: {result['move']} — {result['reasoning'][:80]}...")

            return result

        except Exception as e:
            self.error_count += 1
            logger.error(f"Gemini API error: {str(e)}")
            raise
