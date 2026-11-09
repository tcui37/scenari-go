import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, Navigate } from 'react-router'
import { generateScripts } from '../api.ts'
import ScriptEditor from '../components/ScriptEditor.tsx'
import { findLanguage } from '../data/languages.ts'
import { isComplete } from '../scenario/scenario.ts'
import type { ObjectiveScript, Scenario } from '../scenario/types.ts'

type Props = {
  scenario: Scenario
  scripts: ObjectiveScript[] | null
  setScripts: (scripts: ObjectiveScript[] | null) => void
}

export default function ScenarioInfo({ scenario, scripts, setScripts }: Props) {
  const [error, setError] = useState('')
  const [regenerating, setRegenerating] = useState<number | null>(null)
  const requested = useRef(false)

  const loadScripts = useCallback(async () => {
    setError('')
    try {
      setScripts(await generateScripts(scenario))
    } catch (e) {
      setError((e as Error).message)
    }
  }, [scenario, setScripts])

  // Generate once on arrival if there are no scripts yet (the ref avoids a double call in StrictMode).
  useEffect(() => {
    if (scripts || requested.current || !isComplete(scenario)) return
    requested.current = true
    loadScripts()
  }, [scripts, scenario, loadScripts])

  if (!isComplete(scenario)) return <Navigate to="/create" replace />

  function updateScript(index: number, script: ObjectiveScript) {
    setScripts(scripts!.map((s, i) => (i === index ? script : s)))
  }

  async function regenerate(index: number) {
    setRegenerating(index)
    try {
      const [script] = await generateScripts({ ...scenario, objectives: [scenario.objectives[index]] })
      updateScript(index, script)
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
          <button type="button" className="btn-link" onClick={loadScripts}>
            Try again
          </button>
        </div>
      )}

      {!scripts && !error && <p className="muted">Writing dialogue scripts...</p>}

      {scripts?.map((script, index) => (
        <ScriptEditor
          key={index}
          index={index}
          script={script}
          onChange={(next) => updateScript(index, next)}
          onRegenerate={() => regenerate(index)}
          regenerating={regenerating === index}
        />
      ))}

      <div className="actions">
        <Link to="/create" className="btn">
          Back
        </Link>
        {scripts ? (
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
