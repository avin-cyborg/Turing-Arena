import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

type PlayerCardProps = {
  playerColor: 'White' | 'Black';
  playerName: string;
  reasoning: string;
  isTurn: boolean;
};

export function PlayerCard({ playerColor, playerName, reasoning, isTurn }: PlayerCardProps) {
  return (
    <Card className={cn(
      "flex-1 w-full lg:max-w-sm bg-gray-800 border-gray-700 shadow-lg h-full flex flex-col transition-all duration-300",
      isTurn ? "border-blue-500 shadow-blue-500/20" : "border-gray-700"
    )}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {playerColor} Player
          {isTurn && <span className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></span>}
        </CardTitle>
        <CardDescription>{playerName}</CardDescription>
      </CardHeader>
      <CardContent className="flex-grow flex flex-col">
        <h3 className="text-lg font-semibold mb-2 text-gray-300">AI Reasoning:</h3>
        <div className="p-4 bg-gray-900/50 rounded-md overflow-y-auto h-48 flex-grow text-gray-400 text-sm">
          {reasoning || 'Waiting for move...'}
        </div>
      </CardContent>
    </Card>
  );
}
