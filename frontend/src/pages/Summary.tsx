import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router'
import { scoreScenario } from '../api.ts'
import type { ObjectiveScript, Scenario, ScoreResponse } from '../scenario/types.ts'

type Props = {
  scenario: Scenario
  scripts: ObjectiveScript[] | null
  onReset: () => void
}

export default function Summary({ scenario, scripts, onReset }: Props) {
  const navigate = useNavigate()
  const [result, setResult] = useState<ScoreResponse | null>(null)
  const [error, setError] = useState('')
  const requested = useRef(false)

  const loadScore = useCallback(async () => {
    if (!scripts) return
    setError('')
    try {
      // No conversation is recorded yet; the transcript will come from voice / the game engine.
      setResult(await scoreScenario({ scenario, scripts, transcript: [] }))
    } catch (e) {
      setError((e as Error).message)
    }
  }, [scenario, scripts])

  useEffect(() => {
    if (requested.current) return
    requested.current = true
    loadScore()
  }, [loadScore])

  if (!scripts) return <Navigate to="/scenario" replace />

  function startOver() {
    onReset()
    navigate('/')
  }

  return (
    <div className="stack">
      <h1>Scenario summary</h1>

      {error && (
        <div className="row">
          <p className="error grow">{error}</p>
          <button type="button" className="btn-link" onClick={loadScore}>
            Try again
          </button>
        </div>
      )}

      {!result && !error && <p className="muted">Scoring your conversation...</p>}

      {result && (
        <>
          <section className="card">
            <div className="score">{result.overall_score}/100</div>
            <p>{result.summary}</p>
          </section>

          {result.objectives.map((objective, index) => (
            <div key={index} className={`result ${objective.met ? 'met' : 'not-met'}`}>
              <strong>
                {objective.met ? '✓' : '✗'} {objective.objective}
              </strong>
              <p>{objective.feedback}</p>
            </div>
          ))}
        </>
      )}

      <div className="actions">
        <Link to="/play" className="btn">
          Play again
        </Link>
        <button type="button" className="btn btn-primary" onClick={startOver}>
          New scenario
        </button>
      </div>
    </div>
  )
}
