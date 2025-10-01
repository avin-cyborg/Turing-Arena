import React, { useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

// Define the structure of a single move object from chess.js history
type Move = {
  color: 'w' | 'b';
  from: string;
  to: string;
  flags: string;
  piece: string;
  san: string;
};

// Define the props for the GameLog component
type GameLogProps = {
  history: Move[];
};

export function GameLog({ history }: GameLogProps) {
  const viewportRef = useRef<HTMLDivElement>(null);

  // Effect to scroll to the bottom whenever the history updates
  useEffect(() => {
    // We need to find the actual viewport element rendered by the ScrollArea component
    const viewport = viewportRef.current?.querySelector('[data-radix-scroll-area-viewport]');
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight;
    }
  }, [history]);

  return (
    <Card className="w-full max-w-2xl bg-gray-800 border-gray-700 shadow-lg mt-4">
      <CardHeader>
        <CardTitle>Game Log (PGN)</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea ref={viewportRef} className="h-40 w-full rounded-md border border-gray-600 bg-gray-900/50 p-4">
          <div className="text-sm font-mono text-gray-300">
            {history.reduce((acc: JSX.Element[], move, index) => {
              if (index % 2 === 0) {
                const moveNumber = Math.floor(index / 2) + 1;
                const blackMove = history[index + 1];
                acc.push(
                  <div key={moveNumber} className="flex mb-1">
                    <span className="w-8 text-gray-500">{moveNumber}.</span>
                    <span className="w-20">{move.san}</span>
                    {blackMove && <span className="w-20">{blackMove.san}</span>}
                  </div>
                );
              }
              return acc;
            }, [])}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
