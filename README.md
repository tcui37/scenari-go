# scenari-go

A simple 2D grid game. React + Vite + React Router frontend, FastAPI backend.

```
backend/    FastAPI app (main.py)
frontend/   React + TypeScript app created with Vite
```

## Prerequisites

- Conda env `scenari-go` (Python 3.15)
- Node 26 (`cd frontend && nvm use`, which reads `.nvmrc`)

## Setup

```bash
conda activate scenari-go
pip install -r backend/requirements.txt

cd frontend
npm install
```

## Run

Use two terminals:

```bash
# Terminal 1: backend on http://127.0.0.1:8000 (API docs at /docs)
conda activate scenari-go
cd backend
fastapi dev main.py
```

```bash
# Terminal 2: frontend on http://localhost:5173
cd frontend
npm run dev
```

In development, Vite forwards `/api` and `/ws` to the backend (see `frontend/vite.config.ts`). The frontend never needs the backend URL, and CORS isn't needed.

## App flow

`/` landing → `/create` scenario form → `/scenario` editable checklists → `/play` grid game → `/summary` score

## Endpoints

| Path           | Type      | Purpose                                                        |
| -------------- | --------- | -------------------------------------------------------------- |
| `/api/checklists` | POST   | Returns the scenario with a Gemini checklist per objective     |
| `/api/games/{game_id}/summary` | POST | Gemini scores the game's conversation; returns each objective (met or not) and the transcript |
| `/ws/game`     | WebSocket | One socket is one game. Send the scenario (JSON) and receive `game_created` (`game_id`, voice `webrtc_code`); then send raw key names (`ArrowUp`, `Enter`, `Escape`) and receive `state` whenever it changes |

Gemini needs `GEMINI_API_KEY` in `backend/.env`. The model is set in `backend/llm/gemini.py`.

## Voice (Guava)

Pressing Enter next to the conversation partner starts a voice call with a Guava agent
(`backend/voice/agent.py`). One agent serves every game; the browser names its game when it places
the call. For the length of the call the agent drives the game: it works through
the game's objectives and ends the conversation when the call ends. Esc hangs up early.

`backend/.env` needs `GUAVA_API_KEY` and `GUAVA_WEBRTC_CODE` (create a code with
`guava webrtc create-code`). The backend starts listening on that code when it starts.

## Styling

All colors, fonts and sizes are CSS variables in `frontend/src/styles/tokens.css`, a placeholder
palette based on Duolingo's brand colors with Nunito as the font. Components use only these variables.
