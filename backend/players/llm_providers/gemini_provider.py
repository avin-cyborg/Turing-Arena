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

_FINISH_REASON_NAMES = {
    "STOP": "STOP",
    "MAX_TOKENS": "MAX_TOKENS",
    "SAFETY": "SAFETY",
    "RECITATION": "RECITATION",
    "OTHER": "OTHER",
}

class GeminiProvider(BaseLLMProvider):
    """Google Gemini AI provider — uses google-genai SDK"""

    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash"):
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        super().__init__(model_name, api_key)
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
        """Generate a move using the new google-genai SDK."""
        self.request_count += 1

        try:
            prompt = self.create_chess_prompt(board, move_history)
            logger.info(f"Gemini: Requesting move for position {board.fen()[:30]}...")

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
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

            # Check finish reason
            candidate = response.candidates[0]
            finish_reason = str(candidate.finish_reason.name) if candidate.finish_reason else "UNKNOWN"

            if finish_reason == "SAFETY":
                raise ValueError("Gemini response blocked by safety filters")

            if finish_reason == "MAX_TOKENS":
                logger.warning("Gemini hit MAX_TOKENS — attempting to extract from partial output")

            response_text = response.text.strip()
            logger.debug(f"Gemini raw response: {response_text}")

            result = self.validate_and_extract_move(response_text, board)
            logger.info(f"Gemini chose: {result['move']} — {result['reasoning'][:80]}...")

            return result

        except Exception as e:
            self.error_count += 1
            logger.error(f"Gemini API error: {str(e)}")
            raise
