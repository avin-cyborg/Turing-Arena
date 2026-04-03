# backend/players/llm_providers/gemini_provider.py

import logging
import os
from typing import Dict, List
import chess
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .base_llm import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini AI provider"""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-pro-latest"):
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        super().__init__(model_name, api_key)
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
       
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
         # Initialize model with safety settings
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 512,
                "response_mime_type": "text/plain",
            },
            safety_settings=safety_settings
        )
        
        logger.info(f"Gemini provider initialized with model: {model_name}")
    
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
        """Generate a move using Gemini API with retry logic."""
        self.request_count += 1
        
        try:
            prompt = self.create_chess_prompt(board, move_history)
            logger.info(f"Gemini: Requesting move for position {board.fen()[:20]}...")
            
            # Generate content with explicit safety settings
            response = self.model.generate_content(
                prompt,
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                   
                ]
            )
            
            # ============================================
            # ROBUST RESPONSE HANDLING
            # ============================================
            # Check if response was blocked by safety filters
            if not response.candidates:
                raise ValueError("Response blocked by safety filters (no candidates)")
            
            candidate = response.candidates[0]
            
            # Check finish reason
            if candidate.finish_reason != 1:  # 1 = STOP (normal completion)
                logger.error(f"Gemini finish_reason: {candidate.finish_reason}")
                logger.error(f"Safety ratings: {candidate.safety_ratings}")
                raise ValueError(f"Response blocked: finish_reason = {candidate.finish_reason}")
            
            # Extract text safely
            if not candidate.content or not candidate.content.parts:
                raise ValueError("No content in response")
            
            response_text = candidate.content.parts[0].text.strip()
            # ============================================
            
            logger.debug(f"Gemini raw response: {response_text}")
            
            result = self.validate_and_extract_move(response_text, board)
            logger.info(f"Gemini chose move: {result['move']} - {result['reasoning'][:50]}...")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Gemini API error: {str(e)}")
            raise
