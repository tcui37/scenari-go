// Calls to the FastAPI backend. Vite proxies /api to localhost:8000 in dev.
import type { GameSummary, Scenario } from './scenario/types.ts'

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

// Scores the game's conversation with Gemini; returns the per-objective results and the transcript.
export function summarizeGame(gameId: string): Promise<GameSummary> {
  return post<GameSummary>(`/api/games/${gameId}/summary`, {})
}
