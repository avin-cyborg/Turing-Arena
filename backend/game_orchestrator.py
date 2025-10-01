# backend/game_orchestrator.py
import asyncio
import logging
import chess
import os  # Import the 'os' module
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect

# Import AI Player Adapters
from .players.uci_adapter import UCIAdapter
from .players.llm_adapter import LLMAPIAdapter
from .players.base_player import AIPlayer

logger = logging.getLogger(__name__)

# --- ROBUST PATHING FOR STOCKFISH ---
# Get the absolute path of the current file (game_orchestrator.py)
current_file_path = os.path.abspath(__file__)
# Get the directory containing this file (/backend)
backend_dir = os.path.dirname(current_file_path)
# Get the parent directory of /backend, which is our project root (Game_environment)
project_root = os.path.dirname(backend_dir)
# Construct the full, absolute path to stockfish.exe
stockfish_path = os.path.join(project_root, "stockfish.exe")

# Log the path we constructed for debugging
logger.info(f"Attempting to locate Stockfish at: {stockfish_path}")
if not os.path.exists(stockfish_path):
    logger.error(f"CRITICAL: Stockfish executable not found at the expected path. Please ensure 'stockfish.exe' is in your root project folder.")

# --- GAME AND CONNECTION MANAGEMENT ---
games: Dict[str, Dict] = {}
websocket_connections: Dict[str, List[WebSocket]] = {}

players: List[AIPlayer] = [
    LLMAPIAdapter(name="Gemini"),
    # Use the absolute path we just created
    UCIAdapter(name="Stockfish", path=stockfish_path)
]

def get_players_list() -> List[AIPlayer]:
    return players

def add_websocket_connection(game_id: str, websocket: WebSocket):
    if game_id not in websocket_connections:
        websocket_connections[game_id] = []
    websocket_connections[game_id].append(websocket)

def remove_websocket_connection(game_id: str, websocket: WebSocket):
    if game_id in websocket_connections:
        websocket_connections[game_id].remove(websocket)

async def broadcast(game_id: str, message: Dict):
    if game_id in websocket_connections:
        for connection in list(websocket_connections[game_id]):
            try:
                await connection.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                remove_websocket_connection(game_id, connection)

async def game_loop(game_id: str):
    game_state = games[game_id]
    game_board = game_state["board"]
    player1 = game_state["players"][0]
    player2 = game_state["players"][1]
    turn_number = 0

    while not game_board.is_game_over():
        current_player_idx = turn_number % 2
        current_player = game_state["players"][current_player_idx]

        logger.info(f"Game {game_id} - Turn {turn_number+1}: {current_player.name}'s turn")

        try:
            move_uci = await current_player.get_move(game_board, time_limit=5.0)
            move = chess.Move.from_uci(move_uci)

            if move not in game_board.legal_moves:
                logger.error(f"Illegal move '{move_uci}' from {current_player.name}. Forfeiting.")
                winner_name = game_state["players"][(current_player_idx + 1) % 2].name
                result = "1-0" if winner_name == player1.name else "0-1"
                game_board.set_result(chess.Result(result))
                break

            game_board.push(move)
            logger.info(f"Game {game_id}: {current_player.name} played {move.uci()} | FEN: {game_board.fen()}")

            ai_reasoning = f"{current_player.name} thinking process: This is a placeholder for the AI's reasoning text."
            commentary = f"Commentator: {current_player.name} plays {move.uci()}. Awaiting analysis..."

            await broadcast(game_id, {
                "type": "game_update",
                "fen": game_board.fen(),
                "last_move": move_uci,
                "turn": "white" if game_board.turn == chess.WHITE else "black",
                "ai_reasoning": ai_reasoning,
                "commentary_text": commentary,
            })
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"An error occurred in game loop for {game_id}: {e}", exc_info=True)
            winner_name = game_state["players"][(current_player_idx + 1) % 2].name
            result = "1-0" if winner_name == player1.name else "0-1"
            game_board.set_result(chess.Result(result))
            break

        turn_number += 1

    result = game_board.result()
    winner = "Draw"
    if result == "1-0":
        winner = player1.name
    elif result == "0-1":
        winner = player2.name

    await broadcast(game_id, {
        "type": "game_over",
        "result": result,
        "winner": winner,
        "fen": game_board.fen(),
    })
    logger.info(f"Game {game_id} finished. Winner: {winner}")

async def start_game_instance(white_player_name: str, black_player_name: str):
    game_id = f"game_{len(games)}"
    white_ai = next((p for p in players if p.name.lower() == white_player_name.lower()), None)
    black_ai = next((p for p in players if p.name.lower() == black_player_name.lower()), None)

    if not white_ai or not black_ai:
        return {"error": "One or more players not found."}

    games[game_id] = {
        "board": chess.Board(),
        "players": [white_ai, black_ai]
    }

    logger.info(f"New game started ({game_id}): {white_ai.name} (White) vs {black_ai.name} (Black)")

    await broadcast(game_id, {
        "type": "game_start",
        "game_id": game_id,
        "fen": games[game_id]["board"].fen(),
        "players": {
            "white": white_ai.name,
            "black": black_ai.name
        },
        "status": "game_initialized"
    })

    asyncio.create_task(game_loop(game_id))
    return {"message": "Game started successfully", "game_id": game_id}
