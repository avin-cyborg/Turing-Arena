<script lang="ts">
  export let selectedPlayer: string = 'Stockfish';
  export let availablePlayers: string[] = ['Stockfish', 'Gemini'];
  export let label: string = 'Select Player';
  export let color: 'white' | 'black' = 'white';
</script>

<div class="player-selector">
  <label for="player-{color}">
    {label}
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
    color: #f9fafb;
    font-size: 0.9rem;
  }

  select {
    padding: 0.75rem;
    border: 1px solid #374151;
    border-radius: 6px;
    font-size: 1rem;
    background: #111827;
    color: #f9fafb;
    cursor: pointer;
    transition: border-color 0.2s;
  }

  select:hover {
    border-color: #6b7280;
  }

  select:focus {
    outline: none;
    border-color: #e2a64a;
    box-shadow: 0 0 0 3px rgba(226, 166, 74, 0.15);
  }
</style>
