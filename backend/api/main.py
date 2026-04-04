import asyncio
import sys
import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # ← NEW IMPORT

# ============================================
# LOAD ENVIRONMENT VARIABLES FROM .env FILE
# ============================================
from pathlib import Path

# Get the backend directory (parent of api/)
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Standard logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Loading .env from: {env_path}")
logger.info(f"GEMINI_API_KEY loaded: {bool(os.getenv('GEMINI_API_KEY'))}")
# ============================================

# The '..' indicates a relative import
from ..game_orchestrator import start_game_instance, add_websocket_connection, remove_websocket_connection, get_players_list

# --- ASYNCIO POLICY FIX FOR WINDOWS ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



# --- FASTAPI APPLICATION DEFINITION ---
app = FastAPI()

# CORS MIDDLEWARE - FIXES FRONTEND CONNECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", ""),  # Set this in Render environment variables
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# REQUEST MODEL FOR START GAME
# ============================================
class StartGameRequest(BaseModel):
    white_player: str
    black_player: str
# ============================================

@app.on_event("startup")
async def startup_event():
    """
    This function runs once when the FastAPI application starts.
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
    """
    await websocket.accept()
    add_websocket_connection(game_id, websocket)
    logger.info(f"Client connected to game {game_id}.")
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        remove_websocket_connection(game_id, websocket)
        logger.info(f"Client disconnected from game {game_id}.")

@app.post("/start_game")
async def start_new_game_endpoint(request: StartGameRequest):
    """
    This is the API endpoint that the frontend calls when the "Start Game" button is clicked.
    Expected JSON payload:
    {
        "white_player": "Stockfish",
        "black_player": "Gemini"
    }
    """
    logger.info(f"Starting game: {request.white_player} vs {request.black_player}")
    return await start_game_instance(request.white_player, request.black_player)
