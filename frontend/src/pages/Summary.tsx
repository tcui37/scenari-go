import { Link, Navigate, useNavigate } from 'react-router'
import { hasChecklists } from '../scenario/scenario.ts'
import type { GameSummary, Scenario } from '../scenario/types.ts'

type Props = {
  scenario: Scenario
  summary: GameSummary | null // scored by "Finish scenario" on the Play page
  onReset: () => void
}

export default function Summary({ scenario, summary, onReset }: Props) {
  const navigate = useNavigate()

  if (!hasChecklists(scenario)) return <Navigate to="/scenario" replace />
  if (!summary) return <Navigate to="/play" replace />

  function startOver() {
    onReset()
    navigate('/')
  }

  return (
    <div className="stack">
      <h1>Scenario summary</h1>

      <section className="card">
        <div className="score">{summary.evaluation.overall_score}/100</div>
        <p>{summary.evaluation.summary}</p>
      </section>

      {summary.evaluation.objectives.map((objective, index) => (
        <div key={index} className={`result ${objective.met ? 'met' : 'not-met'}`}>
          <strong>
            {objective.met ? '✓' : '✗'} {objective.objective}
          </strong>
          <p>{objective.feedback}</p>
        </div>
      ))}

      <details className="card transcript">
        <summary>Transcript ({summary.transcript.length} lines)</summary>
        {summary.transcript.length === 0 ? (
          <p className="muted">No conversation was recorded.</p>
        ) : (
          <ol>
            {summary.transcript.map((line, index) => (
              <li key={index}>
                <strong>{line.speaker === 'student' ? 'You' : scenario.partner.name}:</strong> {line.text}
              </li>
            ))}
          </ol>
        )}
      </details>

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
