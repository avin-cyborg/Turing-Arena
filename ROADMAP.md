# 🗺️ Turing Arena — Roadmap & Vision

This document outlines the current roadmap, priorities, and design decisions for Turing Arena.

Status markers: ✅ Done · 🔧 In Progress · 📋 Planned · 💡 Considering

---

## The Vision

Strategy games have historically been used to evaluate decision-making systems under structured constraints, since the beginning of AI research. Deep Blue beating Kasparov was a milestone. AlphaGo beating Lee Sedol was another.

But those were *narrow* AIs — built for one game, one task.

Large language models differ in that they are trained as general-purpose systems rather than task-specific engines. They generate reasoning-like text alongside their actions. This text may appear coherent, but it is not a reliable indicator of the actual decision process. 
The question Turing Arena is trying to answer is:
> **To what extent do general-purpose models maintain decision quality when operating in structured, rule-based, adversarial environments?**

We build infrastructure to evaluate this using measurable signals such as decision quality, rule compliance, and behavioral consistency across games.

## Phase 1 — Core Platform *(Active)*

### 1.1 AI Integration ✅
- [x] Modular adapter architecture (`AIPlayer` protocol)
- [x] Stockfish via UCI adapter
- [x] Gemini, GPT-4, Claude providers with shared base class
- [x] Structured JSON move + reasoning output from LLMs
- [x] Retry logic with exponential backoff (`tenacity`)
- [x] Fallback interventions (e.g., random legal move substitution after API failure) are explicitly logged and tracked as a separate metric (“fallback intervention rate”) to avoid contaminating model performance evaluation.
- [x] FastAPI backend with WebSocket broadcasting

### 1.2 Benchmark Infrastructure 🔧
- [x] 100-game Gemini 2.5 Flash vs Stockfish test suite completed. Note: current sample size is preliminary and not sufficient for statistically robust conclusions.
- [ ] Illegal move rate tracking per model per game
- [ ] Post-game Stockfish evaluation (centipawn loss per move)
- [ ] PGN export for every completed game
- [ ] Structured benchmark result storage (JSON → later database)
- [ ] Stockfish skill level configuration (0–20) for calibrated difficulty

### 1.3 AI Reasoning Pipeline 🔧
- [ ] Surface LLM reasoning text through to frontend (currently generated but dropped before broadcast — known bug being fixed)

### 1.4 Frontend — Core Views 📋
- [ ] Chessboard rendering with real-time move updates completed
- [ ] WebSocket client (game state subscription)
- [ ] AI reasoning side panels (one per player)
- [ ] Commentary text display + audio playback
- [ ] Move history list
- [ ] Game status / result display

### 1.5 Optional UX Enhancements 💡
- [ ] Animated piece movement
- [ ] Last move highlight
- [ ] Captured pieces display
- [ ] Move sound effects
- [ ] Board flip (view from Black's perspective)
- [ ] Responsive layout (mobile-friendly)
- [ ] Commentary layer for move explanations (non-evaluative, for visualization only)

---

## Phase 2 — Game Management & User Features

### 2.1 Game Controls 📋
- [ ] Pause / resume game
- [ ] Adjustable time controls (blitz, rapid, classical)
- [ ] Multiple concurrent games
- [ ] Game replay from PGN
- [ ] Move-by-move step through replay

### 2.2 Database Layer 📋
PostgreSQL with SQLAlchemy. This unlocks everything in Phase 3.

demo schema:
```sql
moves (
    id SERIAL PRIMARY KEY,
    game_id INT REFERENCES games(id),

    move_number INT,
    uci VARCHAR(10),
    san VARCHAR(10),

    -- Raw output (for full traceability)
    reasoning_text TEXT,

    -- Parsed / structured metadata (for analysis)
    reasoning_intent VARCHAR(50),        -- e.g., "attack", "defend", "develop"
    reasoning_confidence FLOAT,          -- optional confidence score
    reasoning_alignment_score FLOAT,     -- EAAS score per move

    -- Evaluation metrics
    engine_eval FLOAT,                   -- centipawn evaluation
    evaluation_depth INT,                -- depth used for evaluation

    -- Model reproducibility
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    provider VARCHAR(50),

    -- Prompt reproducibility
    prompt_version VARCHAR(50),
    temperature FLOAT,
    top_p FLOAT,

    -- System behavior tracking
    retry_count INT,
    fallback_used BOOLEAN,

    -- Timing
    time_taken_ms INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Note: this schema is just a demo and the actual one is yet to be built.
```

### 2.3 User System 📋
- [ ] Authentication (email/password + OAuth)
- [ ] User profiles
- [ ] Personal game history
- [ ] Board theme / piece set preferences

### 2.4 Human vs AI Mode 📋
- [ ] Human move input with legal move validation
- [ ] Hint system (Stockfish suggested move)
- [ ] Clock with time pressure
- [ ] Play against any registered AI player

---

## Phase 3 — Tournament & Leaderboards

### 3.1 Rating System 📋
- [ ] ELO implementation for all players (human + AI)
- [ ] Separate rating tracks: LLM-only, Engine-only, Open
- [ ] Rating history graphs per player
- [ ] Confidence intervals on AI ratings (sample size matters)

### 3.2 Leaderboards 📋
- [ ] Global leaderboard (all player types)
- [ ] LLM-only leaderboard (the core benchmark)
- [ ] Filterable by game, time period, model family

### 3.3 Tournament System 📋
- [ ] Round-robin format
- [ ] Swiss system
- [ ] Automated scheduling and pairing
- [ ] Tournament brackets / standings page

### 3.4 League System 💡
- [ ] Seasonal divisions (Bronze → Diamond)
- [ ] Promotion / relegation
- [ ] Scheduled league events

---

## Phase 4 — Multi-Game Support

This is the phase that makes Turing Arena a platform rather than a chess site.

### 4.1 Game Abstraction Layer 📋

The current orchestrator has `python-chess` types baked in directly. Before adding new games, we'll extract a `GameState` protocol that the orchestrator talks to — mirroring how `AIPlayer` abstracts the AI side. Target interface:

```python
class GameModule(Protocol):
    def initialize() -> GameState
    def get_legal_moves(state: GameState) -> List[Move]
    def apply_move(state: GameState, move: Move) -> GameState
    def is_game_over(state: GameState) -> bool
    def get_result(state: GameState) -> str
```

### 4.2 Game Roadmap 📋

Adding new games is not a simple extension. Each game introduces changes across multiple layers of the system, including state representation, prompt design, and evaluation methodology.

Key challenges per game include:

- **State Representation**  
  Each game requires a different encoding of game state, which affects both backend logic and model input formatting.

- **Prompt Structure**  
  Move generation prompts must be redesigned per game to reflect valid actions and constraints.

- **Evaluation Metrics**  
  Not all games support engine-based evaluation (e.g., centipawn loss in chess). Alternative metrics may be required depending on the game.

- **Comparability**  
  Performance across different games may not be directly comparable due to differences in complexity and search space.

Planned progression:

| Game | Complexity | Notes |
|---|---|---|
| Chess | ✅ Live | Baseline with strong engine support |
| Checkers | Low | Useful for validating abstraction layer |
| Connect Four | Low | Smaller state space, useful for prompt testing |
| Othello / Reversi | Medium | Requires positional reasoning |
| Go (9×9) | High | Large state space, limited evaluation tools |


### 4.3 Universal Board Renderer 📋
A frontend component that renders any game's board state given a generic representation. Avoids duplicating UI work per game.

Design goal: introduce a game abstraction layer that isolates game-specific logic while preserving a consistent interface for AI agents and evaluation pipelines.
---

## Phase 5 — Analytics & Insights

### 5.1 Post-Game Analysis 📋
- [ ] Full Stockfish depth analysis of every completed game
- [ ] Move evaluation graph (position score over time)
- [ ] Blunder / mistake / inaccuracy detection and highlighting
- [ ] Opening classification and book deviation point
- [ ] Endgame accuracy score

### 5.2 LLM-Specific Metrics 📋

These are the metrics that matter for our actual research question:

Note: All metrics are computed under controlled conditions with fixed model configuration, prompt version, and evaluation depth unless otherwise specified.

| Metric | What it tells us |
|---|---|
| Illegal move rate | Does the model understand game rules? |
| Centipawn Loss (CPL) | Average deviation in centipawn evaluation from a reference engine at a fixed evaluation depth (e.g., depth = 12) |
| Explanation–Action Alignment (EAAS) | Does the generated explanation align with the observed outcome of the move? |
| Re-prompt rate (after illegal move) | How often does the LLM need correction? |
| Blunder Rate (Equal Positions) | Frequency of moves that result in a ≥100 centipawn loss when the position evaluation is within ±50 centipawns prior to the move |
| Opening Consistency | Percentage of games in which the model repeats the same move sequence (or stays within top-K engine-recommended moves) for the first N moves under identical initial conditions |
| fallbacks | fallback interventions are tracked separately |

### 5.3 Social / Spectator Features 💡
- [ ] Live game spectator mode
- [ ] Game sharing (link to a completed game with replay)
- [ ] Follow specific AI models or players
- [ ] Community commentary

---

## Phase 6 — Scale & Infrastructure

### 6.1 Performance 📋
- [ ] Redis for game state caching
- [ ] WebSocket connection pooling
- [ ] Load balancing for concurrent game support
- [ ] CDN for static assets

### 6.2 Mobile 💡
- [ ] Progressive Web App (PWA) support
- [ ] Push notifications for live game events

---

## What We're Not Building (Right Now)

Being explicit about scope is part of honest roadmapping:

- **AI training / fine-tuning** — we evaluate models, we don't train them
- **Real-money tournaments** — out of scope for the foreseeable future
- **Custom AI uploads** — user-submitted models introduce trust and security complexity we're not ready for

---

## Benchmark Philosophy

All benchmark results are reported with full configuration details to ensure reproducibility and transparency.

Each experiment includes:

- **Model configuration**
  - Model name and version
  - Provider

- **Prompt configuration**
  - Prompt template (versioned)
  - Input formatting strategy

- **Sampling parameters**
  - Temperature
  - Top-p (nucleus sampling)
  - Random seed (where applicable)

- **Evaluation setup**
  - Opponent configuration (e.g., Stockfish skill level)
  - Engine evaluation depth (fixed across experiments)

- **Execution details**
  - Number of games (sample size)
  - Retry policy and fallback behavior

- **Data outputs**
  - Full game logs (PGN)
  - Move-level metadata (including evaluations and model outputs)

Note:
Where strict determinism is not possible (e.g., due to API constraints), experiments are repeated across multiple runs to estimate variability.
Where applicable, multiple runs are aggregated to report mean and variance of metrics.
---

*Last updated: April 2026*
*This document is updated with each significant development milestone.*
