# ai_chess_backend.py

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Protocol, Union

import chess
import chess.engine
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. CORE ARCHITECTURAL PRINCIPLES ---

# This defines the uniform interface for all AI players.
# This is crucial for a modular and expandable design.
class AIPlayer(Protocol):
    """
    Protocol for a chess AI player. All AI adapters must conform to this interface.
    """
    name: str
    async def get_move(self, board: chess.Board, time_limit: float) -> str:
        """
        Requests a move from the AI.
        
        Args:
            board (chess.Board): The current state of the game board.
            time_limit (float): The maximum time in seconds the AI has to think.

        Returns:
            str: The move in UCI format (e.g., 'e2e4').
        """
        ...

# --- 2. GAME MODULE (Chess Logic) ---
# We'll use the 'chess' library as our game logic module.
# This keeps the game rules separate from the orchestration.

# --- 3. AI PLAYER ADAPTERS (The AI Connectors) ---

class UCIAdapter(AIPlayer):
    """
    Adapter for a Universal Chess Interface (UCI) engine like Stockfish.
    This adapter runs the engine as a subprocess.
    """
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.engine: Optional[chess.engine.Engine] = None
    
    async def connect(self):
        """Initializes and connects to the UCI engine subprocess."""
        try:
            self.engine = await chess.engine.popen_uci(self.path)
            logger.info(f"Connected to UCI engine: {self.name}")
        except FileNotFoundError:
            logger.error(f"Engine executable not found at: {self.path}")
            self.engine = None
    
    async def disconnect(self):
        """Closes the connection to the engine."""
        if self.engine:
            await self.engine.quit()
            logger.info(f"Disconnected from UCI engine: {self.name}")

    async def get_move(self, board: chess.Board, time_limit: float) -> str:
        """
        Gets a move from the UCI engine.
        
        This method sends the board state and receives the best move.
        """
        if not self.engine:
            raise RuntimeError(f"Engine {self.name} is not connected.")
        
        try:
            # We use `with_asyncio` to run the engine in a non-blocking way
            result = await self.engine.play(board, chess.engine.Limit(time=time_limit))
            return result.move.uci()
        except Exception as e:
            logger.error(f"Error with engine {self.name}: {e}")
            raise

class LLMAPIAdapter(AIPlayer):
    """
    Placeholder for the LLM API Adapter. 
    This is where we'll implement the logic to call a large language model API.
    
    The actual implementation will be added in a future step.
    """
    def __init__(self, name: str):
        self.name = name

    async def get_move(self, board: chess.Board, time_limit: float) -> str:
        """
        Simulates an LLM's move generation.
        
        In a real scenario, this would craft a prompt with FEN and PGN,
        call an API like Gemini, and parse the structured output for the move.
        
        For now, it's just a simple mock.
        """
        logger.info(f"LLM {self.name} is 'thinking' for {time_limit} seconds...")
        await asyncio.sleep(1) # Simulate API latency

        # This part would be the actual logic to prompt the LLM and get a response.
        # For the sake of this example, we'll just have it play a very simple,
        # non-optimal move to demonstrate the turn-based system.
        
        # Example: Just get a random legal move for demonstration
        legal_moves = list(board.legal_moves)
        if legal_moves:
            move = legal_moves[0].uci()
            # In a real scenario, you'd parse the LLM's structured response here.
            # E.g., json_response = {"move": "e2e4", "reasoning": "I chose this move to control the center."}
            # move = json_response["move"]
            
            return move
        else:
            raise RuntimeError("No legal moves available for LLM.")

# --- 4. ORCHESTRATION LAYER (FastAPI Backend) ---

app = FastAPI()

# A simple in-memory store for game state, keyed by game ID
games: Dict[str, Dict] = {}

# We'll use the players list to easily add new AIs
players: List[AIPlayer] = [
    LLMAPIAdapter(name="Gemini"),
    UCIAdapter(name="Stockfish", path="stockfish")  # Replace "stockfish" with the actual path to your engine
]

# A dictionary to hold WebSocket connections for each game
websocket_connections: Dict[str, List[WebSocket]] = {}

@app.on_event("startup")
async def startup_event():
    """
    This function runs once when the application starts.
    It connects to all UCI engines.
    """
    for player in players:
        if isinstance(player, UCIAdapter):
            await player.connect()
    logger.info("Application started. All AI players are connected.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    This function runs when the application shuts down.
    It disconnects all UCI engines.
    """
    for player in players:
        if isinstance(player, UCIAdapter):
            await player.disconnect()
    logger.info("Application shut down. All AI players are disconnected.")


async def broadcast(game_id: str, message: Dict):
    """
    Broadcasts a message to all connected clients for a specific game.
    """
    if game_id in websocket_connections:
        dead_connections = []
        for connection in websocket_connections[game_id]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                dead_connections.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                dead_connections.append(connection)
        for connection in dead_connections:
            websocket_connections[game_id].remove(connection)

async def game_loop(game_id: str):
    """
    The main game loop that manages turns and game state.
    """
    game_state = games[game_id]
    game_board = game_state["board"]
    player1 = game_state["players"][0]
    player2 = game_state["players"][1]
    turn_number = 0
    
    while not game_board.is_game_over():
        current_player_idx = turn_number % 2
        current_player = game_state["players"][current_player_idx]
        opponent = game_state["players"][(current_player_idx + 1) % 2]

        logger.info(f"Game {game_id} - Turn {turn_number+1}: {current_player.name}'s turn")
        
        try:
            # Get the move from the current AI player
            move_uci = await current_player.get_move(game_board, time_limit=5)
            move = chess.Move.from_uci(move_uci)

            # Check for illegal moves before applying
            if move not in game_board.legal_moves:
                logger.error(f"Illegal move received from {current_player.name}: {move_uci}")
                game_board.set_result("1-0" if current_player_idx == 1 else "0-1")
                break
                
            game_board.push(move)
            
            logger.info(f"Game {game_id}: {current_player.name} played {move.san()} | FEN: {game_board.fen()}")

            # In a real scenario, we'd get reasoning from the LLM adapter here
            ai_reasoning = f"{current_player.name} thinking process: This is a placeholder for the AI's reasoning text."
            
            # --- COMMENTATOR AI (Simulated) ---
            # This is where we would call the commentator AI and TTS.
            # For now, we'll just have a placeholder message.
            commentary = f"Commentator: {current_player.name} made a move. Awaiting analysis..."
            
            # Broadcast the game state update to all clients
            await broadcast(game_id, {
                "type": "game_update",
                "fen": game_board.fen(),
                "last_move": move_uci,
                "turn": game_board.turn,
                "ai_reasoning": ai_reasoning,
                "commentary_text": commentary,
                "players": {
                    "white": player1.name,
                    "black": player2.name
                },
                "status": "in_progress"
            })

            # Simulate the commentator generating and playing its output
            # In a real app, this would be an async call
            await asyncio.sleep(2) 
            
        except Exception as e:
            logger.error(f"An error occurred in game loop: {e}")
            game_board.set_result("1-0" if current_player_idx == 1 else "0-1")
            break

        turn_number += 1

    # After the game is over, broadcast the final result
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
        "players": {
            "white": player1.name,
            "black": player2.name
        }
    })
    
@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """
    WebSocket endpoint for real-time game communication.
    """
    await websocket.accept()
    if game_id not in websocket_connections:
        websocket_connections[game_id] = []
    websocket_connections[game_id].append(websocket)
    logger.info(f"Client connected to game {game_id}. Total connections: {len(websocket_connections[game_id])}")

    try:
        # A simple loop to keep the connection open
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections[game_id].remove(websocket)
        logger.info(f"Client disconnected from game {game_id}. Remaining: {len(websocket_connections[game_id])}")


@app.post("/start_game")
async def start_new_game(white_player: str, black_player: str):
    """
    API endpoint to start a new game between two AI players.
    
    This function initializes the game state and starts the game loop.
    """
    game_id = f"game_{len(games)}"
    
    white_ai = next((p for p in players if p.name.lower() == white_player.lower()), None)
    black_ai = next((p for p in players if p.name.lower() == black_player.lower()), None)
    
    if not white_ai or not black_ai:
        return {"error": "One or more players not found."}

    games[game_id] = {
        "board": chess.Board(),
        "players": [white_ai, black_ai]
    }
    
    logger.info(f"New game started with ID: {game_id}")

    # Broadcast the initial game state
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
    
    # Start the game loop in a separate task
    asyncio.create_task(game_loop(game_id))
    
    return {"message": "Game started", "game_id": game_id}
