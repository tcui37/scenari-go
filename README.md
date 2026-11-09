# scenari-go

A simple 2D grid game. React + Vite + React Router frontend, FastAPI backend.

```
backend/    FastAPI app (main.py)
frontend/   React + TypeScript app created with Vite
```

## Prerequisites

- Conda env `scenari-go` (Python 3.15)
- Node LTS (`nvm use --lts`)

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

## Endpoints

| Path         | Type      | Purpose                                  |
| ------------ | --------- | ---------------------------------------- |
| `/api/hello` | GET       | Test REST call, shown on the Home page   |
| `/ws`        | WebSocket | Echo test, used on the Game page         |

## Voice (Guava)

Browser voice calls to a Guava AI agent over WebRTC ([docs](https://docs.goguava.ai/guides/webrtc-calls)).
The browser connects straight to Guava. `backend/agent.py` is a separate process that steers the call.

1. Create a WebRTC code: `guava webrtc create-code` (run `guava login` first if needed).
2. Put it in `backend/.env` as `GUAVA_WEBRTC_CODE=grtc-...` (next to `GUAVA_API_KEY`),
   and in `frontend/.env.local` as `VITE_GUAVA_WEBRTC_CODE=grtc-...`.
3. Run the agent: `cd backend && python agent.py`
4. Run the frontend, open http://localhost:5173/voice, and click **Start call**.

The API key stays in `backend/.env` and never goes to the browser.
