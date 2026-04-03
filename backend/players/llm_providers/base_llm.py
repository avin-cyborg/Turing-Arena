# backend/players/llm_providers/base_llm.py

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
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
        thinking_time: float
    ) -> Dict[str, str]:
        """
        Generate a chess move using the LLM.
        
        Args:
            board: Current chess board state
            move_history: List of moves in SAN notation
            thinking_time: Time limit for the move
            
        Returns:
            Dict with 'move' (UCI format) and 'reasoning' (explanation)
        """
        pass
    
    def create_chess_prompt(
        self, 
        board: chess.Board, 
        move_history: List[str]
    ) -> str:
        """
        Creates a detailed prompt for the LLM with board state and context.
        """
        # Determine player color
        color = "White" if board.turn else "Black"
        
        # Get legal moves in UCI format
        legal_moves = [move.uci() for move in board.legal_moves]
        
        # Create move history string
        history_str = " ".join(move_history) if move_history else "Starting position"
        
        # Check for check/checkmate/stalemate
        status = ""
        if board.is_checkmate():
            status = "CHECKMATE - Game Over!"
        elif board.is_check():
            status = "You are in CHECK!"
        elif board.is_stalemate():
            status = "STALEMATE - Game Over!"
        
        prompt = f"""You are an expert chess player playing as {color}.

**Current Position (FEN):** {board.fen()}

**Move History:** {history_str}

**Game Status:** {status if status else "Normal play"}

**Your Legal Moves (UCI format):** {', '.join(legal_moves[:20])}{'...' if len(legal_moves) > 20 else ''}

**Instructions:**
1. Analyze the position carefully
2. Consider tactical and strategic elements
3. Choose the BEST move from the legal moves list
4. Respond with ONLY valid JSON in this exact format:

{{
    "move": "your_move_in_uci_format",
    "reasoning": "brief explanation of your choice"
}}

**Example Response:**
{{
    "move": "e2e4",
    "reasoning": "Opening with the King's Pawn to control the center"
}}

**CRITICAL RULES:**
- Your move MUST be from the legal moves list above
- Use lowercase UCI notation (e.g., e2e4, not E2E4)
- Respond ONLY with the JSON object, no other text
- For pawn promotion, add the piece code (e.g., e7e8q for queen promotion)

Now, what is your move?"""
        
        return prompt
    
    def validate_and_extract_move(
        self, 
        response: str, 
        board: chess.Board
    ) -> Dict[str, str]:
        """
        Validates LLM response and extracts the move.
        
        Returns:
            Dict with 'move' (UCI) and 'reasoning'
        
        Raises:
            ValueError: If response is invalid
        """
        import json
        import re
        
        try:
            # Try to parse as JSON first
            data = json.loads(response)
            move_uci = data.get('move', '').strip().lower()
            reasoning = data.get('reasoning', 'No reasoning provided')
            
        except json.JSONDecodeError:
            # Fallback: Extract move using regex
            logger.warning(f"JSON parse failed. Raw response: {response}")
            
            # Look for UCI move pattern (e.g., e2e4, g1f3, e7e8q)
            match = re.search(r'\b([a-h][1-8][a-h][1-8][qrbn]?)\b', response.lower())
            
            if not match:
                raise ValueError(f"No valid UCI move found in response: {response}")
            
            move_uci = match.group(1)
            reasoning = "Extracted from non-JSON response"
        
        # Validate move is legal
        try:
            move = chess.Move.from_uci(move_uci)
            if move not in board.legal_moves:
                raise ValueError(f"Move {move_uci} is not legal in current position")
        except ValueError as e:
            raise ValueError(f"Invalid move format '{move_uci}': {str(e)}")
        
        return {
            'move': move_uci,
            'reasoning': reasoning
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Returns provider statistics"""
        return {
            'requests': self.request_count,
            'errors': self.error_count,
            'success_rate': ((self.request_count - self.error_count) / max(self.request_count, 1)) * 100
        }
