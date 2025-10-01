import React, { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

// This could be fetched from an API in the future
const availablePlayers = [
  { name: 'Gemini', value: 'gemini' },
  { name: 'Stockfish', value: 'stockfish' },
];

type GameControlsProps = {
  status: 'idle' | 'loading' | 'playing' | 'over';
  turn: 'w' | 'b';
  commentary: string;
  onStartGame: (white: string, black: string) => void;
  isLoading: boolean;
};

export function GameControls({ status, turn, commentary, onStartGame, isLoading }: GameControlsProps) {
  const [whitePlayer, setWhitePlayer] = useState('gemini');
  const [blackPlayer, setBlackPlayer] = useState('stockfish');

  const handleStartClick = () => {
    onStartGame(whitePlayer, blackPlayer);
  };

  return (
    <Card className="w-full max-w-2xl bg-gray-800 border-gray-700 shadow-lg">
      <CardHeader>
        <CardTitle>Tournament Controls</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          <div className="space-y-2">
            <Label htmlFor="white-select">White Player</Label>
            <Select onValueChange={setWhitePlayer} defaultValue={whitePlayer} disabled={status === 'playing'}>
              <SelectTrigger id="white-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                {availablePlayers.map((p) => <SelectItem key={p.value} value={p.value}>{p.name}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="black-select">Black Player</Label>
            <Select onValueChange={setBlackPlayer} defaultValue={blackPlayer} disabled={status === 'playing'}>
              <SelectTrigger id="black-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                {availablePlayers.map((p) => <SelectItem key={p.value} value={p.value}>{p.name}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="flex justify-center">
          <Button
            onClick={handleStartClick}
            disabled={status === 'playing' || isLoading}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-md text-lg"
            size="lg"
          >
            {isLoading ? <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Starting...</> : 'Start New Game'}
          </Button>
        </div>
        <div className="text-center text-sm text-gray-400 pt-4 border-t border-gray-700">
          <p><strong>Status:</strong> <span className="capitalize">{status}</span></p>
          {status === 'playing' && <p><strong>Turn:</strong> {turn === 'w' ? 'White' : 'Black'}</p>}
        </div>
      </CardContent>
      <CardFooter className="bg-gray-900/50 p-4 rounded-b-lg">
        <p className="text-sm italic text-center text-gray-400 w-full">{commentary}</p>
      </CardFooter>
    </Card>
  );
}
