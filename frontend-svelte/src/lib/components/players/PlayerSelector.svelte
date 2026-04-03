<script lang="ts">
  export let selectedPlayer: string = 'Stockfish';
  export let availablePlayers: string[] = ['Stockfish', 'Gemini'];
  export let label: string = 'Select Player';
  export let color: 'white' | 'black' = 'white';
</script>

<div class="player-selector">
  <label for="player-{color}">
    {label}
    <span class="color-badge" class:white={color === 'white'} class:black={color === 'black'}>
      {color === 'white' ? '⚪' : '⚫'}
    </span>
  </label>
  <select id="player-{color}" bind:value={selectedPlayer}>
    {#each availablePlayers as player}
      <option value={player}>{player}</option>
    {/each}
  </select>
</div>

<style>
  .player-selector {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    color: #333;
    font-size: 0.9rem;
  }

  .color-badge {
    font-size: 1.2rem;
  }

  select {
    padding: 0.75rem;
    border: 2px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
    background: white;
    cursor: pointer;
    transition: border-color 0.2s;
  }

  select:hover {
    border-color: #999;
  }

  select:focus {
    outline: none;
    border-color: #4CAF50;
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
  }
</style>
