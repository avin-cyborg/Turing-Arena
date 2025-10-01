import asyncio
import sys
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# The '..' indicates a relative import, telling Python to look one directory up
# from the current file's location to find the 'game_orchestrator' module.
from ..game_orchestrator import start_game_instance, add_websocket_connection, remove_websocket_connection, get_players_list

# --- ASYNCIO POLICY FIX FOR WINDOWS ---
# This is the critical fix for the NotImplementedError on Windows.
# It manually sets an asyncio event loop policy that supports subprocesses,
# which is required for the python-chess library to launch Stockfish.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# -----------------------------------------

# Standard logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FASTAPI APPLICATION DEFINITION ---
# This creates the main application instance that Uvicorn will run.
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    This function runs once when the FastAPI application starts.
    It iterates through our defined AI players and calls the 'connect' method
    on any that have it (like our UCIAdapter for Stockfish).
    """
    players = get_players_list()
    for player in players:
        if hasattr(player, 'connect') and asyncio.iscoroutinefunction(player.connect):
            await player.connect()
    logger.info("Application started. AI players are connected.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    This function runs once when the FastAPI application is shutting down.
    It ensures a clean disconnect from any running engine processes.
    """
    players = get_players_list()
    for player in players:
        if hasattr(player, 'disconnect') and asyncio.iscoroutinefunction(player.disconnect):
            await player.disconnect()
    logger.info("Application shut down. AI players are disconnected.")

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """
    This is the real-time communication endpoint.
    The frontend connects here to receive live updates about the game.
    """
    await websocket.accept()
    add_websocket_connection(game_id, websocket)
    logger.info(f"Client connected to game {game_id}.")
    try:
        # This loop keeps the connection alive. It waits for messages,
        # but in our case, it's mostly a one-way street from server to client.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # This block runs if the client disconnects (e.g., closes the browser tab).
        remove_websocket_connection(game_id, websocket)
        logger.info(f"Client disconnected from game {game_id}.")

@app.post("/start_game")
async def start_new_game_endpoint(white_player: str, black_player: str):
    """
    This is the API endpoint that the frontend calls when the "Start Game" button is clicked.
    It delegates the actual game creation and management to the orchestrator.
    """
    return await start_game_instance(white_player, black_player)

