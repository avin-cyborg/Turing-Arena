<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  
  export let fen: string = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
  export let lastMove: { from: string; to: string } | null = null;
  export let orientation: 'white' | 'black' = 'white';
  
  let boardElement: HTMLDivElement;
  let chessground: any = null;

  // Chess piece symbols (Unicode)
  const pieces: Record<string, string> = {
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'
  };

  // Parse FEN to board representation
  function fenToBoard(fen: string): string[][] {
    const position = fen.split(' ')[0];
    const ranks = position.split('/');
    
    return ranks.map(rank => {
      const squares: string[] = [];
      for (const char of rank) {
        if (isNaN(parseInt(char))) {
          squares.push(char);
        } else {
          squares.push(...Array(parseInt(char)).fill(''));
        }
      }
      return squares;
    });
  }

  $: board = fenToBoard(fen);
  $: files = orientation === 'white' ? ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] : ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a'];
  $: ranks = orientation === 'white' ? ['8', '7', '6', '5', '4', '3', '2', '1'] : ['1', '2', '3', '4', '5', '6', '7', '8'];

  function getSquareId(file: number, rank: number): string {
    return files[file] + ranks[rank];
  }

  function isHighlighted(file: number, rank: number): boolean {
    if (!lastMove) return false;
    const square = getSquareId(file, rank);
    return square === lastMove.from || square === lastMove.to;
  }

  function isLightSquare(file: number, rank: number): boolean {
    return (file + rank) % 2 === 0;
  }
</script>

<div class="chessboard-container">
  <div class="chessboard" bind:this={boardElement}>
    {#each ranks as rank, rankIdx}
      <div class="rank">
        {#each files as file, fileIdx}
          {@const piece = board[rankIdx][fileIdx]}
          {@const squareId = getSquareId(fileIdx, rankIdx)}
          <div
            class="square"
            class:light={isLightSquare(fileIdx, rankIdx)}
            class:dark={!isLightSquare(fileIdx, rankIdx)}
            class:highlighted={isHighlighted(fileIdx, rankIdx)}
            data-square={squareId}
          >
            {#if piece}
              <div class="piece">
                {pieces[piece]}
              </div>
            {/if}
            
            {#if fileIdx === 0}
              <span class="rank-label">{rank}</span>
            {/if}
            {#if rankIdx === 7}
              <span class="file-label">{file}</span>
            {/if}
          </div>
        {/each}
      </div>
    {/each}
  </div>
</div>

<style>
  .chessboard-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
  }

  .chessboard {
    display: flex;
    flex-direction: column;
    border: 2px solid #333;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    background: #312e2b;
  }

  .rank {
    display: flex;
  }

  .square {
    width: 70px;
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    transition: background-color 0.2s ease;
  }

  .square.light {
    background-color: #f0d9b5;
  }

  .square.dark {
    background-color: #b58863;
  }

  .square.highlighted {
    background-color: #cdd26a !important;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.3);
  }

  .piece {
    font-size: 3.5rem;
    line-height: 1;
    user-select: none;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .rank-label,
  .file-label {
    position: absolute;
    font-size: 0.7rem;
    font-weight: bold;
    color: rgba(0, 0, 0, 0.4);
    user-select: none;
  }

  .rank-label {
    top: 2px;
    left: 3px;
  }

  .file-label {
    bottom: 2px;
    right: 3px;
  }

  .square.dark .rank-label,
  .square.dark .file-label {
    color: rgba(255, 255, 255, 0.5);
  }

  /* Responsive sizing */
  @media (max-width: 768px) {
    .square {
      width: 45px;
      height: 45px;
    }
    
    .piece {
      font-size: 2.2rem;
    }
  }
</style>
