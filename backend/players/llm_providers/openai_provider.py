# backend/players/llm_providers/openai_provider.py

import logging
import os
from typing import Dict, List
import chess
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .base_llm import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4 provider"""
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4o-mini"):
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        super().__init__(model_name, api_key)
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        logger.info(f"OpenAI provider initialized with model: {model_name}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def generate_move(
        self,
        board: chess.Board,
        move_history: List[str],
        thinking_time: float
    ) -> Dict[str, str]:
        """Generate a move using OpenAI API with retry logic."""
        self.request_count += 1
        
        try:
            prompt = self.create_chess_prompt(board, move_history)
            logger.info(f"OpenAI: Requesting move for position {board.fen()[:20]}...")
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a world-class chess grandmaster. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=256,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI raw response: {response_text}")
            
            result = self.validate_and_extract_move(response_text, board)
            logger.info(f"OpenAI chose move: {result['move']} - {result['reasoning'][:50]}...")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"OpenAI API error: {str(e)}")
            raise
