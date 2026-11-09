import { lazy, Suspense, useState } from 'react'
import { Link, Navigate, Route, Routes } from 'react-router'
import CreateScenario from './pages/CreateScenario.tsx'
import Landing from './pages/Landing.tsx'
import ScenarioInfo from './pages/ScenarioInfo.tsx'
import Summary from './pages/Summary.tsx'
import { EMPTY_SCENARIO } from './scenario/scenario.ts'
import type { ObjectiveScript, Scenario } from './scenario/types.ts'

// PixiJS is large, so the game page loads only when someone plays.
const Play = lazy(() => import('./pages/Play.tsx'))

export default function App() {
  // App never unmounts, so state kept here survives moving between pages.
  const [scenario, setScenario] = useState<Scenario>(EMPTY_SCENARIO)
  const [scripts, setScripts] = useState<ObjectiveScript[] | null>(null)

  // Saving the form: only drop generated scripts if the scenario changed.
  function saveScenario(next: Scenario) {
    if (JSON.stringify(next) !== JSON.stringify(scenario)) setScripts(null)
    setScenario(next)
  }

  function reset() {
    setScenario(EMPTY_SCENARIO)
    setScripts(null)
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
            element={<ScenarioInfo scenario={scenario} scripts={scripts} setScripts={setScripts} />}
          />
          <Route
            path="/play"
            element={
              <Suspense fallback={<p className="muted">Loading game...</p>}>
                <Play scripts={scripts} />
              </Suspense>
            }
          />
          <Route path="/summary" element={<Summary scenario={scenario} scripts={scripts} onReset={reset} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}
