// Calls to the FastAPI backend. Vite proxies /api to localhost:8000 in dev.
import type { ObjectiveScript, Scenario, ScoreResponse, TranscriptLine } from './scenario/types.ts'

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

export async function generateScripts(scenario: Scenario): Promise<ObjectiveScript[]> {
  const data = await post<{ scripts: ObjectiveScript[] }>('/api/scripts', scenario)
  return data.scripts
}

export function scoreScenario(req: {
  scenario: Scenario
  scripts: ObjectiveScript[]
  transcript: TranscriptLine[]
}): Promise<ScoreResponse> {
  return post<ScoreResponse>('/api/score', req)
}
