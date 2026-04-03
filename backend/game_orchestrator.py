# backend/game_orchestrator.py

import asyncio
import logging
import chess
import os
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect

# Import AI Player Adapters
from .players.uci_adapter import UCIAdapter
from .players.llm_adapter import LLMAPIAdapter
from .players.base_player import AIPlayer

logger = logging.getLogger(__name__)

# --- ROBUST PATHING FOR STOCKFISH ---
current_file_path = os.path.abspath(__file__)
backend_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(backend_dir)
stockfish_path = os.path.join(project_root, "stockfish.exe")

logger.info(f"Attempting to locate Stockfish at: {stockfish_path}")

if not os.path.exists(stockfish_path):
    logger.error(f"Stockfish not found at {stockfish_path}")
else:
    logger.info(f"Stockfish found at {stockfish_path}")

# --- PLAYER REGISTRY ---
# Initialize all available AI players
PLAYERS = {
    "Stockfish": UCIAdapter(name="Stockfish", path=stockfish_path),
    "Gemini": LLMAPIAdapter(name="Gemini", provider_type="gemini", model_name="gemini-pro-latest"),
    "GPT4": LLMAPIAdapter(name="GPT4", provider_type="gpt4"),
    "Claude": LLMAPIAdapter(name="Claude", provider_type="claude"),
}

# --- GAME STATE MANAGEMENT ---
games: Dict[str, dict] = {}
websocket_connections: Dict[str, List[WebSocket]] = {}

def get_players_list():
    """Returns list of all available AI players"""
    return list(PLAYERS.values())

def add_websocket_connection(game_id: str, websocket: WebSocket):
    """Add a WebSocket connection for a specific game"""
    if game_id not in websocket_connections:
        websocket_connections[game_id] = []
    websocket_connections[game_id].append(websocket)
    logger.info(f"WebSocket added for game {game_id}. Total: {len(websocket_connections[game_id])}")

def remove_websocket_connection(game_id: str, websocket: WebSocket):
    """Remove a WebSocket connection"""
    if game_id in websocket_connections:
        websocket_connections[game_id].remove(websocket)
        logger.info(f"WebSocket removed for game {game_id}")

async def broadcast(game_id: str, message: dict):
    """Broadcast a message to all connected WebSocket clients for a game"""
    if game_id in websocket_connections:
        for websocket in websocket_connections[game_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")

async def start_game_instance(white_player_name: str, black_player_name: str) -> dict:
    """
    Starts a new game instance with the specified players.
    """
    game_id = f"game_{len(games)}"
    
    # Get player instances
    white_player = PLAYERS.get(white_player_name)
    black_player = PLAYERS.get(black_player_name)
    
    if not white_player or not black_player:
        return {"error": f"Invalid player names: {white_player_name}, {black_player_name}"}
    
    # Initialize game state
    games[game_id] = {
        "board": chess.Board(),
        "white": white_player,
        "black": black_player,
        "white_reasoning": "",  # ← ADDED: Store reasoning
        "black_reasoning": "",  # ← ADDED: Store reasoning
    }
    
    logger.info(f"Game {game_id} created: {white_player.name} (White) vs {black_player.name} (Black)")
    
    # Start the game loop in the background
    asyncio.create_task(game_loop(game_id))
    
    # Send initial game state to frontend
    await broadcast(game_id, {
        "type": "game_start",
        "game_id": game_id,
        "fen": games[game_id]["board"].fen(),
        "players": {
            "white": white_player.name,
            "black": black_player.name
        },
        "status": "game_initialized"
    })
    
    return {
        "game_id": game_id,
        "status": "started",
        "players": {
            "white": white_player.name,
            "black": black_player.name
        }
    }

async def game_loop(game_id: str):
    """
    Main game loop - handles turn-by-turn gameplay
    """
    game_data = games[game_id]
    game_board = game_data["board"]
    white_player = game_data["white"]
    black_player = game_data["black"]
    
    logger.info(f"Game {game_id}: Starting game loop")
    
    while not game_board.is_game_over():
        # Determine current player
        current_player = white_player if game_board.turn == chess.WHITE else black_player
        current_color = "white" if game_board.turn == chess.WHITE else "black"
        
        try:
            logger.info(f"Game {game_id}: {current_player.name}'s turn ({current_color})")
            
            # Get move from player (returns UCI string or dict with move + reasoning)
            move_result = await current_player.get_move(game_board, time_limit=30.0)
            
            # ============================================
            # HANDLE BOTH OLD (UCI string) AND NEW (dict with reasoning) FORMAT
            # ============================================
            if isinstance(move_result, dict):
                # New LLM format: {"move": "e2e4", "reasoning": "..."}
                move_uci = move_result.get('move')
                reasoning = move_result.get('reasoning', 'No reasoning provided')
            else:
                # Old format: Just UCI string (from Stockfish)
                move_uci = move_result
                reasoning = f"{current_player.name} is analyzing the position..."
            
            # Store reasoning in game state
            if current_color == "white":
                game_data["white_reasoning"] = reasoning
            else:
                game_data["black_reasoning"] = reasoning
            # ============================================
            
            # Convert to chess.Move object
            move = chess.Move.from_uci(move_uci)
            
            # Validate move
            if move not in game_board.legal_moves:
                logger.error(f"Game {game_id}: Illegal move {move_uci} by {current_player.name}")
                await broadcast(game_id, {
                    "type": "game_over",
                    "result": "forfeit",
                    "winner": black_player.name if current_color == "white" else white_player.name,
                    "reason": f"Illegal move by {current_player.name}"
                })
                break
            
            # Apply move to board
            game_board.push(move)
            logger.info(f"Game {game_id}: {current_player.name} played {move.uci()} | FEN: {game_board.fen()}")
            
            # Broadcast updated game state with reasoning
            await broadcast(game_id, {
                "type": "game_update",
                "fen": game_board.fen(),
                "last_move": move.uci(),
                "turn": "white" if game_board.turn == chess.WHITE else "black",
                "ai_reasoning": reasoning,  # ← Send reasoning to frontend
                "commentary_text": f"Commentator: {current_player.name} plays {move.uci()}. {reasoning[:100]}..."
            })
            
            # Small delay between moves
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Game {game_id}: Error during {current_player.name}'s turn: {str(e)}")
            await broadcast(game_id, {
                "type": "game_over",
                "result": "error",
                "winner": black_player.name if current_color == "white" else white_player.name,
                "reason": f"Error: {str(e)}"
            })
            break
    
    # Game ended
    result = game_board.result()
    winner = "Draw"
    
    if result == "1-0":
        winner = white_player.name
    elif result == "0-1":
        winner = black_player.name
    
    logger.info(f"Game {game_id}: Game Over | Result: {result} | Winner: {winner}")
    
    await broadcast(game_id, {
        "type": "game_over",
        "result": result,
        "winner": winner,
        "fen": game_board.fen()
    })
