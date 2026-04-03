# backend/players/llm_adapter.py

import asyncio
import logging
import chess
import random
from typing import Optional, List
from .base_player import AIPlayer
from .llm_providers.gemini_provider import GeminiProvider
from .llm_providers.openai_provider import OpenAIProvider
from .llm_providers.claude_provider import ClaudeProvider

logger = logging.getLogger(__name__)


class LLMAPIAdapter(AIPlayer):
    """
    Unified adapter for multiple LLM providers.
    Supports Gemini, GPT-4, Claude, and fallback to random moves.
    """
    
    def __init__(self, name: str, provider_type: str = "gemini", model_name: str = None):
        """
        Initialize LLM adapter with specific provider.
        
        Args:
            name: Display name for the player
            provider_type: One of "gemini", "gpt4", "claude"
            model_name: Optional specific model name
        """
        self.name = name
        self.provider_type = provider_type.lower()
        self.provider = None
        self.move_history = []
        self.use_fallback = False
        
        # Initialize the appropriate provider
        try:
            if self.provider_type == "gemini":
                self.provider = GeminiProvider(model_name=model_name or "gemini-1.5-flash")
            elif self.provider_type in ["gpt4", "openai"]:
                self.provider = OpenAIProvider(model_name=model_name or "gpt-4o-mini")
            elif self.provider_type == "claude":
                self.provider = ClaudeProvider(model_name=model_name or "claude-3-5-sonnet-20241022")
            else:
                raise ValueError(f"Unknown provider type: {provider_type}")
            
            logger.info(f"✅ LLM '{self.name}' initialized with {self.provider_type} provider")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.provider_type} provider: {str(e)}")
            logger.warning(f"⚠️  '{self.name}' will use fallback (random legal moves)")
            self.use_fallback = True
    
    async def get_move(self, board: chess.Board, time_limit: float) -> str:
        """
        Get a move from the LLM or fallback to random move.
        """
        if self.use_fallback or not self.provider:
            return await self._fallback_move(board)
        
        try:
            logger.info(f"🤔 {self.name} ({self.provider_type}) is thinking...")
            
            result = await asyncio.wait_for(
                self.provider.generate_move(board, self.move_history, time_limit),
                timeout=time_limit
            )
            
            move_uci = result['move']
            reasoning = result['reasoning']
            
            move = chess.Move.from_uci(move_uci)
            san_move = board.san(move)
            self.move_history.append(san_move)
            
            logger.info(f"✅ {self.name} chose {move_uci}: {reasoning}")
            
            return move_uci
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ {self.name} timed out after {time_limit}s")
            return await self._fallback_move(board)
            
        except Exception as e:
            logger.error(f"❌ {self.name} error: {str(e)}")
            logger.warning(f"⚠️  Using fallback move")
            return await self._fallback_move(board)
    
    async def _fallback_move(self, board: chess.Board) -> str:
        """Fallback to random legal move if LLM fails."""
        logger.info(f"🎲 {self.name} using random fallback move")
        await asyncio.sleep(0.5)
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            raise RuntimeError("No legal moves available")
        
        move = random.choice(legal_moves)
        san_move = board.san(move)
        self.move_history.append(san_move)
        
        return move.uci()
    
    def get_stats(self):
        """Get provider statistics"""
        if self.provider:
            return self.provider.get_stats()
        return {'requests': 0, 'errors': 0, 'success_rate': 0}
