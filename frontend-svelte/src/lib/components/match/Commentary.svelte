<script lang="ts">
  export let commentary: string = '';
</script>

<div class="commentary-panel">
  <div class="header">
    <span class="icon">🎙️</span>
    <h3>AI Commentary</h3>
  </div>
  
  <div class="commentary-content">
    {#if commentary}
      <p>{commentary}</p>
    {:else}
      <p class="empty-state">Waiting for game to start...</p>
    {/if}
  </div>
</div>

<style>
  .commentary-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .icon {
    font-size: 1.5rem;
  }

  h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .commentary-content {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    padding: 1rem;
    min-height: 80px;
  }

  .commentary-content p {
    margin: 0;
    line-height: 1.6;
    font-size: 0.95rem;
  }

  .empty-state {
    color: rgba(255, 255, 255, 0.7);
    font-style: italic;
  }
</style>
