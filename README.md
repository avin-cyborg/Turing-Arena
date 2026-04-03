# ♟️ Turing Arena

> *Can AI think strategically — or is it just pattern matching?*

**Turing Arena** is an open platform for benchmarking AI models through competitive gameplay. We pit LLMs (Gemini, GPT-4, Claude) against each other and against classical engines (Stockfish) across strategy games, measuring not just wins and losses, but *how* they think — move quality, illegal move rates, reasoning coherence, and deviation from optimal play.

The goal isn't to crown a winner. It's to build a rigorous, reproducible framework for understanding the gap between AI pattern recognition and genuine strategic reasoning.

---

## 🎯 What This Is

Most AI benchmarks test knowledge retrieval or instruction following. Turing Arena tests **in-context strategic decision-making** under adversarial pressure — a meaningfully different capability.

Chess is the starting point. Multi-game support is on the roadmap.

---

## ✅ What's Working Right Now

- **AI vs AI gameplay** — any combination of Gemini, GPT-4, Claude, and Stockfish
- **Modular adapter architecture** — adding a new AI model requires writing one file, touching nothing else
- **Real-time WebSocket communication** — live game state broadcast to connected frontends
- **Structured LLM move generation** — JSON-formatted prompts with legal move validation, retry logic, and graceful fallback
- **Multi-provider support** — `GeminiProvider`, `OpenAIProvider`, `ClaudeProvider` all implement a shared `BaseLLMProvider` interface
- **Illegal move handling** — invalid moves are caught, logged, and attributed correctly
- **FastAPI backend** with CORS, WebSocket endpoints, and startup/shutdown lifecycle management

---

## 📊 Early Benchmark Results

We've run **100 games of Gemini 2.5 Flash vs Stockfish (default settings)**.

**Result: Stockfish wins 100/100.**

This is expected — Stockfish at default settings plays at ~3500 ELO, well beyond any human or LLM. But the *interesting* data is in the details we're now instrumented to capture:

| Metric | Status |
|---|---|
| Win/Loss tracking | ✅ Live |
| Illegal move rate per model | 🔧 In progress |
| Average centipawn loss per move | 🔧 In progress |
| Move quality vs engine depth | 📋 Planned |
| Reasoning coherence scoring | 📋 Planned |

The next benchmark set will run LLMs against **Stockfish Skill Level 1–5**, where the ELO gap is meaningful enough to reveal real differences between models.

---

## 🏗️ Architecture

The platform is built around four decoupled layers:

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI Backend                    │
│              (Orchestration Layer)                   │
│   Manages game lifecycle, turn order, broadcasting  │
└─────────┬───────────────────────────────┬───────────┘
          │                               │
┌─────────▼──────────┐       ┌────────────▼───────────┐
│   Game Module      │       │   AI Player Adapters   │
│   (python-chess)   │       │                        │
│                    │       │  UCIAdapter (Stockfish) │
│  - Legal move gen  │       │  LLMAPIAdapter          │
│  - Move validation │       │    ├── GeminiProvider   │
│  - Game over check │       │    ├── OpenAIProvider   │
└────────────────────┘       │    └── ClaudeProvider  │
                             └────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────┐
│              WebSocket → Frontend GUI                │
│         (SvelteKit — in active development)         │
└─────────────────────────────────────────────────────┘
```

Every AI player, whether Stockfish or an LLM, implements the same `AIPlayer` protocol. The orchestrator is entirely AI-agnostic.

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, WebSockets |
| Game Logic | `python-chess` |
| Classical Engine | Stockfish (via UCI protocol) |
| LLM Providers | Google Gemini, OpenAI GPT-4, Anthropic Claude |
| Frontend | SvelteKit, TypeScript *(in progress)* |
| Retry / Resilience | `tenacity` |

---

## 🚧 Current Development Focus

These are the active workstreams right now, in priority order:

1. **AI reasoning pipeline** — LLMs generate reasoning with every move; surfacing this to the frontend is the next UI milestone
2. **Post-game analysis** — Stockfish evaluation of every move (centipawn loss) for benchmark data
3. **Frontend board + panels** — Chessboard rendering, real-time move display, AI reasoning side panels
4. **Commentator AI** — Live game commentary via Gemini, with TTS audio output

See [`ROADMAP.md`](./ROADMAP.md) for the full phased plan.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Stockfish](https://stockfishchess.org/download/) binary in the project root
- API keys for whichever LLM providers you want to use

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/turing-arena.git
cd turing-arena

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in your API keys in .env

# Run the backend
uvicorn api.main:app --reload
```

### Environment Variables

```env
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Note: Ensure you have your respective API keys (OpenAI, Gemini) configured in your backend .env file before initiating a match.
Backend runs on `http://localhost:8000`. Frontend on `http://localhost:5173`.

---

## 📁 Project Structure

```
turing-arena/
├── backend/
│   ├── api/
│   │   └── main.py              # FastAPI app, endpoints, WebSocket handler
│   ├── game_orchestrator.py     # Game lifecycle, turn management, broadcasting
│   └── players/
│       ├── base_player.py       # AIPlayer protocol (the uniform interface)
│       ├── uci_adapter.py       # Stockfish / UCI engine adapter
│       ├── llm_adapter.py       # Unified LLM adapter with fallback logic
│       └── llm_providers/
│           ├── base_llm.py      # Abstract base + shared prompt engineering
│           ├── gemini_provider.py
│           ├── openai_provider.py
│           └── claude_provider.py
├── frontend/                    # SvelteKit app (in active development)
├── stockfish.exe                # Engine binary (not committed, see setup)
├── main.py                      # Uvicorn entry point
├── ROADMAP.md                   # Phased development plan
└── README.md
```

---

## 🤝 Contributing

The project is in early development. If you want to contribute:

- Adding a new AI provider → implement `BaseLLMProvider`, wire it in `llm_adapter.py`
- Adding a new game → the game module interface is designed to be pluggable (see `ROADMAP.md` Phase 4)
- Frontend → SvelteKit, TypeScript, open issues for specific components

Open an issue before starting large PRs so we can align on approach.

---

## 📄 License

MIT

---

*Built to answer a simple question: when an AI makes a move, does it know why?*
