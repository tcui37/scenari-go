import type { ChecklistItem, ObjectiveScript } from '../scenario/types.ts'

type Props = {
  index: number
  script: ObjectiveScript
  onChange: (script: ObjectiveScript) => void
  onRegenerate: () => void
  regenerating: boolean
}

const KINDS: { value: ChecklistItem['kind']; label: string }[] = [
  { value: 'instruction', label: 'Instruction' },
  { value: 'say', label: 'Say' },
]

// Editable list of prompts the conversation partner follows for one objective.
export default function ScriptEditor({ index, script, onChange, onRegenerate, regenerating }: Props) {
  const { checklist } = script

  function setChecklist(next: ChecklistItem[]) {
    onChange({ ...script, checklist: next })
  }

  function updateItem(itemIndex: number, changes: Partial<ChecklistItem>) {
    setChecklist(checklist.map((item, i) => (i === itemIndex ? { ...item, ...changes } : item)))
  }

  return (
    <section className="card stack">
      <div className="row">
        <h2 className="grow">Objective {index + 1}</h2>
        <button type="button" className="btn-link" onClick={onRegenerate} disabled={regenerating}>
          {regenerating ? 'Regenerating...' : 'Regenerate'}
        </button>
      </div>
      <p>{script.objective}</p>

      {checklist.map((item, itemIndex) => (
        <div key={itemIndex} className="checklist-item">
          <div className="row">
            <div className="kind-toggle" role="group" aria-label="Prompt type">
              {KINDS.map((kind) => (
                <button
                  key={kind.value}
                  type="button"
                  aria-pressed={item.kind === kind.value}
                  onClick={() => updateItem(itemIndex, { kind: kind.value })}
                >
                  {kind.label}
                </button>
              ))}
            </div>
            <span className="grow" />
            <button
              type="button"
              className="btn-link danger"
              onClick={() => setChecklist(checklist.filter((_, i) => i !== itemIndex))}
            >
              Remove
            </button>
          </div>
          <textarea
            className="input"
            rows={2}
            value={item.text}
            aria-label={`Prompt ${itemIndex + 1}`}
            onChange={(event) => updateItem(itemIndex, { text: event.target.value })}
          />
        </div>
      ))}

      <button
        type="button"
        className="btn-link align-start"
        onClick={() => setChecklist([...checklist, { kind: 'instruction', text: '' }])}
      >
        + Add prompt
      </button>
    </section>
  )
}
