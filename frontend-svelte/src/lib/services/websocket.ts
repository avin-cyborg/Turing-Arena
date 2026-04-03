import { gameStore } from '$lib/stores/gameStore';
import { wsStore } from '$lib/stores/wsStore';
import type { GameMessage } from '$lib/types/websocket';

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(gameId: string) {
    const wsUrl = `ws://localhost:8000/ws/${gameId}`;
    
    try {
      wsStore.setStatus('connecting');
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        wsStore.setStatus('connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        wsStore.setError('Connection error');
      };

      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        wsStore.setStatus('disconnected');
        this.attemptReconnect(gameId);
      };
    } catch (error) {
      console.error('Failed to connect:', error);
      wsStore.setError('Failed to establish connection');
    }
  }

  private handleMessage(message: GameMessage) {
    console.log('📨 Received:', message);

    switch (message.type) {
      case 'game_start':
        gameStore.startGame(message.game_id, message.players);
        gameStore.updateBoard(message.fen, '', 'white');
        break;

      case 'game_update':
        gameStore.updateBoard(message.fen, message.last_move, message.turn);
        if (message.commentary_text) {
          gameStore.setCommentary(message.commentary_text);
        }
        if (message.ai_reasoning) {
          const currentTurn = message.turn === 'white' ? 'black' : 'white'; // Reasoning is from last player
          gameStore.setReasoning(currentTurn, message.ai_reasoning);
        }
        break;

      case 'game_over':
        gameStore.updateBoard(message.fen, '', 'white');
        gameStore.endGame(message.winner, message.result);
        break;
    }
  }

  private attemptReconnect(gameId: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => this.connect(gameId), 2000);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

export const websocketService = new WebSocketService();
