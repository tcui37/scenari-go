import { useCallback, useEffect, useRef, useState, type Dispatch, type SetStateAction } from 'react'
import { Link, Navigate } from 'react-router'
import { generateChecklists } from '../api.ts'
import ChecklistEditor from '../components/ChecklistEditor.tsx'
import { findLanguage } from '../data/languages.ts'
import { hasChecklists, isComplete } from '../scenario/scenario.ts'
import type { ChecklistItem, Scenario } from '../scenario/types.ts'

type Props = {
  scenario: Scenario
  setScenario: Dispatch<SetStateAction<Scenario>>
}

export default function ScenarioInfo({ scenario, setScenario }: Props) {
  const [error, setError] = useState('')
  const [regenerating, setRegenerating] = useState<number | null>(null)
  const requested = useRef(false)
  const ready = hasChecklists(scenario)

  const loadChecklists = useCallback(async () => {
    setError('')
    try {
      setScenario(await generateChecklists(scenario))
    } catch (e) {
      setError((e as Error).message)
    }
  }, [scenario, setScenario])

  // Generate once on arrival if there are no checklists yet (the ref avoids a double call in StrictMode).
  useEffect(() => {
    if (ready || requested.current || !isComplete(scenario)) return
    requested.current = true
    loadChecklists()
  }, [ready, scenario, loadChecklists])

  if (!isComplete(scenario)) return <Navigate to="/create" replace />

  // Uses the updater form so edits made while a regenerate is in flight aren't lost.
  function updateChecklist(index: number, checklist: ChecklistItem[]) {
    setScenario((current) => ({
      ...current,
      checklists: current.checklists.map((c, i) => (i === index ? checklist : c)),
    }))
  }

  async function regenerate(index: number) {
    setRegenerating(index)
    try {
      const single = await generateChecklists({ ...scenario, objectives: [scenario.objectives[index]], checklists: [] })
      updateChecklist(index, single.checklists[0])
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setRegenerating(null)
    }
  }

  const { partner } = scenario
  const language = findLanguage(partner.language)

  return (
    <div className="stack">
      <h1>Dialogue info</h1>

      <section className="card">
        <h2>{partner.name}</h2>
        <p>{partner.bio}</p>
        <p className="muted">
          {language?.label} · {partner.level} · {scenario.setting}
        </p>
      </section>

      {error && (
        <div className="row">
          <p className="error grow">{error}</p>
          <button type="button" className="btn-link" onClick={loadChecklists}>
            Try again
          </button>
        </div>
      )}

      {!ready && !error && <p className="muted">Writing prompts for each objective...</p>}

      {ready &&
        scenario.objectives.map((objective, index) => (
          <ChecklistEditor
            key={index}
            index={index}
            objective={objective}
            checklist={scenario.checklists[index]}
            onChange={(checklist) => updateChecklist(index, checklist)}
            onRegenerate={() => regenerate(index)}
            regenerating={regenerating === index}
          />
        ))}

      <div className="actions">
        <Link to="/create" className="btn">
          Back
        </Link>
        {ready ? (
          <Link to="/play" className="btn btn-primary">
            Play scenario!
          </Link>
        ) : (
          <button type="button" className="btn btn-primary" disabled>
            Play scenario!
          </button>
        )}
      </div>
    </div>
  )
}
