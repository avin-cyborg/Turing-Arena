# backend/players/llm_providers/claude_provider.py

import logging
import os
from typing import Dict, List
import chess
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .base_llm import BaseLLMProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str = None, model_name: str = "claude-3-5-sonnet-20241022"):
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        super().__init__(model_name, api_key)
        self.client = AsyncAnthropic(api_key=self.api_key)
        
        logger.info(f"Claude provider initialized with model: {model_name}")
    
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
        """Generate a move using Claude API with retry logic."""
        self.request_count += 1
        
        try:
            prompt = self.create_chess_prompt(board, move_history)
            logger.info(f"Claude: Requesting move for position {board.fen()[:20]}...")
            
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=256,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            logger.debug(f"Claude raw response: {response_text}")
            
            result = self.validate_and_extract_move(response_text, board)
            logger.info(f"Claude chose move: {result['move']} - {result['reasoning'][:50]}...")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Claude API error: {str(e)}")
            raise
