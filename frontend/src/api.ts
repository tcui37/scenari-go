// Calls to the FastAPI backend. Vite proxies /api to localhost:8000 in dev.
import type { GameState } from './game/types.ts'
import type { Scenario, ScoreResponse, TranscriptLine } from './scenario/types.ts'

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => null)
    throw new Error(typeof error?.detail === 'string' ? error.detail : `Request failed (${response.status})`)
  }
  return response.json()
}

// Returns the same scenario with `checklists` filled in, one per objective.
export function generateChecklists(scenario: Scenario): Promise<Scenario> {
  return post<Scenario>('/api/checklists', scenario)
}

export function scoreScenario(req: { scenario: Scenario; transcript: TranscriptLine[] }): Promise<ScoreResponse> {
  return post<ScoreResponse>('/api/score', req)
}

// Starts a new, isolated game for `scenario`. Play it over the WebSocket at /ws/games/{game_id}.
export function newGame(scenario: Scenario): Promise<{ game_id: string; state: GameState }> {
  return post('/api/games', scenario)
}
