<script lang="ts">
  export let commentary: string = '';
</script>

<div class="commentary-panel">
  <div class="header">
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
    background: #1f2937;
    color: #f9fafb;
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #374151;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  }

  .header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #f9fafb;
  }

  .commentary-content {
    background: #111827;
    border-radius: 6px;
    padding: 1rem;
    min-height: 80px;
    border: 1px solid #374151;
  }

  .commentary-content p {
    margin: 0;
    line-height: 1.6;
    font-size: 0.95rem;
    color: #e5e7eb;
  }

  .empty-state {
    color: #6b7280;
    font-style: italic;
  }
</style>
