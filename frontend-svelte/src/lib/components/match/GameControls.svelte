<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { GameStatus } from '$lib/types/game';
  
  export let gameStatus: GameStatus = 'idle';
  export let whitePlayer: string = 'Stockfish';
  export let blackPlayer: string = 'Gemini';
  
  const dispatch = createEventDispatcher();
  
  let isStarting = false;
  
  async function handleStartGame() {
    isStarting = true;
    dispatch('start', { whitePlayer, blackPlayer });
    // Reset after a delay to prevent spam
    setTimeout(() => isStarting = false, 2000);
  }
  
  function handleResetGame() {
    dispatch('reset');
  }
  
  $: canStart = gameStatus === 'idle' && !isStarting;
  $: canReset = gameStatus === 'playing' || gameStatus === 'finished';
</script>

<div class="game-controls">
  {#if canStart}
    <button class="btn btn-primary" on:click={handleStartGame} disabled={isStarting}>
      {isStarting ? '🎮 Starting...' : '▶️ Start Game'}
    </button>
  {/if}
  
  {#if canReset}
    <button class="btn btn-secondary" on:click={handleResetGame}>
      🔄 Reset Game
    </button>
  {/if}
</div>

<style>
  .game-controls {
    display: flex;
    gap: 1rem;
    justify-content: center;
    padding: 1rem;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }

  .btn:active:not(:disabled) {
    transform: translateY(0);
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-primary {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
  }

  .btn-secondary {
    background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
    color: white;
  }

  .btn-secondary:hover:not(:disabled) {
    background: linear-gradient(135deg, #f57c00 0%, #e65100 100%);
  }
</style>
