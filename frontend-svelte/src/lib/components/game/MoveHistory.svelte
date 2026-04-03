<script lang="ts">
  import type { Move } from '$lib/types/game';
  
  export let moves: Move[] = [];
  
  // Group moves into pairs (white, black)
  $: movePairs = moves.reduce((pairs, move, idx) => {
    const pairIdx = Math.floor(idx / 2);
    if (!pairs[pairIdx]) pairs[pairIdx] = { num: pairIdx + 1, white: null, black: null };
    
    if (idx % 2 === 0) {
      pairs[pairIdx].white = move;
    } else {
      pairs[pairIdx].black = move;
    }
    return pairs;
  }, [] as Array<{ num: number; white: Move | null; black: Move | null }>);
</script>

<div class="move-history">
  <h3>Move History</h3>
  <div class="moves-container">
    {#if moves.length === 0}
      <p class="empty-state">No moves yet</p>
    {:else}
      <div class="moves-list">
        {#each movePairs as pair}
          <div class="move-pair">
            <span class="move-number">{pair.num}.</span>
            {#if pair.white}
              <span class="move white-move">{pair.white.san}</span>
            {/if}
            {#if pair.black}
              <span class="move black-move">{pair.black.san}</span>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .move-history {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  h3 {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    color: #333;
  }

  .moves-container {
    max-height: 400px;
    overflow-y: auto;
  }

  .empty-state {
    color: #999;
    font-style: italic;
    text-align: center;
    padding: 2rem 0;
  }

  .moves-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .move-pair {
    display: grid;
    grid-template-columns: 40px 1fr 1fr;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 4px;
    transition: background 0.2s;
  }

  .move-pair:hover {
    background: #f5f5f5;
  }

  .move-number {
    color: #666;
    font-weight: bold;
  }

  .move {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-weight: 500;
  }

  .white-move {
    background: #f0f0f0;
    color: #333;
  }

  .black-move {
    background: #444;
    color: #fff;
  }
</style>
