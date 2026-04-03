<script lang="ts">
  import type { Player, PlayerColor } from '$lib/types/game';
  
  export let player: Player;
  export let isActive: boolean = false;
  export let reasoning: string = '';
  
  const colorEmoji = player.color === 'white' ? '⚪' : '⚫';
  const aiTypeIcon = player.type === 'ai' ? '🤖' : '👤';
</script>

<div class="player-card" class:active={isActive}>
  <div class="player-header">
    <div class="player-info">
      <span class="color-indicator">{colorEmoji}</span>
      <h3>{player.name}</h3>
      <span class="ai-badge">{aiTypeIcon}</span>
    </div>
    {#if isActive}
      <div class="thinking-indicator">
        <span class="pulse"></span>
        <span>Thinking...</span>
      </div>
    {/if}
  </div>
  
  {#if reasoning}
    <div class="reasoning-section">
      <h4>AI Reasoning</h4>
      <p>{reasoning}</p>
    </div>
  {/if}
</div>

<style>
  .player-card {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    border: 2px solid transparent;
  }

  .player-card.active {
    border-color: #4CAF50;
    box-shadow: 0 4px 16px rgba(76, 175, 80, 0.3);
  }

  .player-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .player-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .color-indicator {
    font-size: 1.5rem;
  }

  h3 {
    margin: 0;
    font-size: 1.2rem;
    color: #333;
  }

  .ai-badge {
    font-size: 1rem;
  }

  .thinking-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #4CAF50;
    font-size: 0.9rem;
    font-weight: 500;
  }

  .pulse {
    width: 8px;
    height: 8px;
    background: #4CAF50;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.2); }
  }

  .reasoning-section {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
  }

  .reasoning-section h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .reasoning-section p {
    margin: 0;
    font-size: 0.9rem;
    color: #555;
    line-height: 1.5;
  }
</style>
