<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { gameStore } from '$lib/stores/gameStore';
  import { wsStore } from '$lib/stores/wsStore';
  import { websocketService } from '$lib/services/websocket';
  import { startNewGame } from '$lib/services/api';
  
  // Components
  import ChessBoard from '$lib/components/game/ChessBoard.svelte';
  import MoveHistory from '$lib/components/game/MoveHistory.svelte';
  import PlayerCard from '$lib/components/players/PlayerCard.svelte';
  import PlayerSelector from '$lib/components/players/PlayerSelector.svelte';
  import GameControls from '$lib/components/match/GameControls.svelte';
  import Commentary from '$lib/components/match/Commentary.svelte';
  import GameStatus from '$lib/components/match/GameStatus.svelte';

  // Available AI players
  const availablePlayers = ['Stockfish', 'Gemini'];
  
  // Selected players for new game
  let whitePlayer = 'Stockfish';
  let blackPlayer = 'Gemini';
  
  // Reactive subscriptions
  $: game = $gameStore;
  $: ws = $wsStore;
  
  // Derived state
  $: lastMove = game.moveHistory.length > 0 
    ? game.moveHistory[game.moveHistory.length - 1]
    : null;
  
  $: isWhiteTurn = game.turn === 'white';
  $: currentPlayerReasoning = isWhiteTurn ? game.aiReasoning.white : game.aiReasoning.black;

  async function handleStartGame(event: CustomEvent) {
    try {
      gameStore.reset();
      const { whitePlayer: white, blackPlayer: black } = event.detail;
      
      console.log(`🎮 Starting game: ${white} vs ${black}`);
      
      // Call backend to start game
      const response = await startNewGame(white, black);
      console.log('✅ Game started:', response);
      
      // Connect WebSocket
      websocketService.connect(response.game_id);
      
    } catch (error) {
      console.error('❌ Failed to start game:', error);
      alert('Failed to start game. Please check backend connection.');
    }
  }

  function handleResetGame() {
    websocketService.disconnect();
    gameStore.reset();
  }

  onDestroy(() => {
    websocketService.disconnect();
  });
</script>

<svelte:head>
  <title>AI Chess Championship</title>
</svelte:head>

<main class="app-container">
  <!-- Header -->
  <header class="app-header">
    <h1>🏆 AI Chess Championship</h1>
    <p class="subtitle">Watch AI models battle in real-time chess matches</p>
  </header>

  <!-- Game Status Bar -->
  <GameStatus 
    gameStatus={game.status} 
    wsStatus={ws.status}
    result={game.result}
  />

  <!-- Main Game Area -->
  <div class="game-layout">
    
    <!-- Left Sidebar: Player Setup & Info -->
    <aside class="sidebar sidebar-left">
      {#if game.status === 'idle'}
        <div class="setup-section">
          <h2>🎮 Setup Match</h2>
          <PlayerSelector 
            bind:selectedPlayer={whitePlayer}
            {availablePlayers}
            label="White Player"
            color="white"
          />
          <PlayerSelector 
            bind:selectedPlayer={blackPlayer}
            {availablePlayers}
            label="Black Player"
            color="black"
          />
        </div>
      {:else}
        <PlayerCard 
          player={game.players.white}
          isActive={game.status === 'playing' && isWhiteTurn}
          reasoning={game.aiReasoning.white}
        />
        <PlayerCard 
          player={game.players.black}
          isActive={game.status === 'playing' && !isWhiteTurn}
          reasoning={game.aiReasoning.black}
        />
      {/if}
    </aside>

    <!-- Center: Chessboard -->
    <section class="board-section">
      <ChessBoard 
        fen={game.fen}
        lastMove={lastMove ? { from: lastMove.from, to: lastMove.to } : null}
        orientation="white"
      />
      
      <GameControls 
        gameStatus={game.status}
        {whitePlayer}
        {blackPlayer}
        on:start={handleStartGame}
        on:reset={handleResetGame}
      />
    </section>

    <!-- Right Sidebar: Game Info -->
    <aside class="sidebar sidebar-right">
      <Commentary commentary={game.commentary} />
      <MoveHistory moves={game.moveHistory} />
    </aside>
    
  </div>

  <!-- Footer -->
  <footer class="app-footer">
    <p>Built with SvelteKit • WebSocket-powered real-time updates</p>
  </footer>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
  }

  .app-container {
    max-width: 1600px;
    margin: 0 auto;
    padding: 1rem;
  }

  .app-header {
    text-align: center;
    color: white;
    margin-bottom: 2rem;
  }

  .app-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .subtitle {
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
    opacity: 0.9;
  }

  .game-layout {
    display: grid;
    grid-template-columns: 300px 1fr 300px;
    gap: 1.5rem;
    margin-top: 1.5rem;
  }

  .sidebar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .setup-section {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .setup-section h2 {
    margin: 0 0 1.5rem 0;
    font-size: 1.3rem;
    color: #333;
  }

  .board-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .app-footer {
    text-align: center;
    color: white;
    margin-top: 2rem;
    padding: 1rem;
    opacity: 0.8;
    font-size: 0.9rem;
  }

  /* Responsive Design */
  @media (max-width: 1200px) {
    .game-layout {
      grid-template-columns: 1fr;
      grid-template-areas:
        "setup"
        "board"
        "info";
    }

    .sidebar-left {
      grid-area: setup;
    }

    .board-section {
      grid-area: board;
    }

    .sidebar-right {
      grid-area: info;
    }
  }

  @media (max-width: 768px) {
    .app-header h1 {
      font-size: 1.8rem;
    }

    .subtitle {
      font-size: 0.95rem;
    }

    .game-layout {
      gap: 1rem;
    }
  }
</style>
