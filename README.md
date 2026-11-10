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
| `/api/score`   | POST      | Gemini scores the conversation against the objectives          |
| `/api/games`   | POST      | Starts a new, isolated game; returns its `game_id` and state    |
| `/ws/games/{game_id}` | WebSocket | Send `{"type": "move", "direction": "up"}`; receive the new state |

Gemini needs `GEMINI_API_KEY` in `backend/.env`. The model is set in `backend/gemini.py`.

## Styling

All colors, fonts and sizes are CSS variables in `frontend/src/styles/tokens.css`, a placeholder
palette based on Duolingo's brand colors with Nunito as the font. Components use only these variables.
