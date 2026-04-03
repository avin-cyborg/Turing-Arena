import { writable } from 'svelte/store';

export type WSStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

interface WSState {
  status: WSStatus;
  error: string | null;
}

function createWSStore() {
  const { subscribe, set, update } = writable<WSState>({
    status: 'disconnected',
    error: null
  });

  return {
    subscribe,
    setStatus: (status: WSStatus) => update(state => ({ ...state, status })),
    setError: (error: string) => update(state => ({ status: 'error', error })),
    clearError: () => update(state => ({ ...state, error: null }))
  };
}

export const wsStore = createWSStore();
