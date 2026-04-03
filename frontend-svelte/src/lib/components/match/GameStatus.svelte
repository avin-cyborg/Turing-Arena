<script lang="ts">
  import type { GameStatus } from '$lib/types/game';
  import type { WSStatus } from '$lib/stores/wsStore';
  
  export let gameStatus: GameStatus = 'idle';
  export let wsStatus: WSStatus = 'disconnected';
  export let result: { winner: string; outcome: string } | undefined = undefined;
  
  $: statusText = getStatusText(gameStatus, result);
  $: statusColor = getStatusColor(gameStatus);
  $: wsColor = wsStatus === 'connected' ? '#4CAF50' : '#ff5252';
  
  function getStatusText(status: GameStatus, result: any): string {
    switch (status) {
      case 'idle': return 'Ready to Start';
      case 'loading': return 'Initializing...';
      case 'playing': return 'Game in Progress';
      case 'finished': return result ? `Game Over - ${result.winner} Wins!` : 'Game Finished';
      default: return 'Unknown';
    }
  }
  
  function getStatusColor(status: GameStatus): string {
    switch (status) {
      case 'idle': return '#9e9e9e';
      case 'loading': return '#ff9800';
      case 'playing': return '#4CAF50';
      case 'finished': return '#2196F3';
      default: return '#9e9e9e';
    }
  }
</script>

<div class="game-status">
  <div class="status-item">
    <span class="status-label">Game Status:</span>
    <span class="status-value" style="color: {statusColor}">
      {statusText}
    </span>
  </div>
  
  <div class="status-item">
    <span class="status-label">Connection:</span>
    <span class="connection-indicator" style="background: {wsColor}"></span>
    <span class="status-value">{wsStatus}</span>
  </div>
</div>

<style>
  .game-status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status-label {
    font-weight: 600;
    color: #666;
    font-size: 0.9rem;
  }

  .status-value {
    font-weight: 600;
    font-size: 1rem;
  }

  .connection-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
</style>
