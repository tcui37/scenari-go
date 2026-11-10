import { lazy, Suspense, useState } from 'react'
import { Link, Navigate, Route, Routes, useNavigate } from 'react-router'
import CreateScenario from './pages/CreateScenario.tsx'
import Landing from './pages/Landing.tsx'
import ScenarioInfo from './pages/ScenarioInfo.tsx'
import Summary from './pages/Summary.tsx'
import { EMPTY_SCENARIO } from './scenario/scenario.ts'
import type { GameSummary, Scenario } from './scenario/types.ts'

// PixiJS is large, so the game page loads only when someone plays.
const Play = lazy(() => import('./pages/Play.tsx'))

export default function App() {
  // App never unmounts, so state kept here survives moving between pages.
  const [scenario, setScenario] = useState<Scenario>(EMPTY_SCENARIO)
  const [summary, setSummary] = useState<GameSummary | null>(null) // the last finished game's results
  const navigate = useNavigate()

  // Saving the form: keep generated checklists only if nothing the teacher entered changed.
  function saveScenario(next: Scenario) {
    const withoutChecklists = (s: Scenario) => JSON.stringify({ ...s, checklists: [] })
    const changed = withoutChecklists(next) !== withoutChecklists(scenario)
    setScenario({ ...next, checklists: changed ? [] : scenario.checklists })
  }

  function reset() {
    setScenario(EMPTY_SCENARIO)
    setSummary(null)
  }

  function showSummary(next: GameSummary) {
    setSummary(next)
    navigate('/summary')
  }

  return (
    <>
      <header className="app-header">
        <Link to="/" className="wordmark">
          scenarigo
        </Link>
      </header>

      <main className="page">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/create" element={<CreateScenario scenario={scenario} onSave={saveScenario} />} />
          <Route
            path="/scenario"
            element={<ScenarioInfo scenario={scenario} setScenario={setScenario} />}
          />
          <Route
            path="/play"
            element={
              <Suspense fallback={<p className="muted">Loading game...</p>}>
                <Play scenario={scenario} onFinish={showSummary} />
              </Suspense>
            }
          />
          <Route path="/summary" element={<Summary scenario={scenario} summary={summary} onReset={reset} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}
