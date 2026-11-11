import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { useNavigate } from 'react-router'
import Select from 'react-select'
import LevelDialog from '../components/LevelDialog.tsx'
import { findLanguage, LANGUAGES, type Language } from '../data/languages.ts'
import { isComplete } from '../scenario/scenario.ts'
import type { ConversationPartner, Objective, Scenario } from '../scenario/types.ts'

const BIO_MAX = 200
const SETTING_MAX = 200

type Props = {
  scenario: Scenario
  onSave: (scenario: Scenario) => void
}

// Tab in an empty field fills in its suggestion (the placeholder, without the trailing "...").
// Once the field has text, Tab moves to the next field as usual.
function fillSuggestionOnTab(fill: (value: string) => void) {
  return (event: KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const field = event.currentTarget
    if (event.key !== 'Tab' || event.shiftKey || field.value) return
    event.preventDefault()
    fill(field.placeholder.replace(/\.\.\.$/, ''))
  }
}

export default function CreateScenario({ scenario, onSave }: Props) {
  const navigate = useNavigate()
  // Edits stay local until Next; then the cleaned-up scenario is saved to App.
  const [draft, setDraft] = useState<Scenario>(scenario)
  const [levelDialogOpen, setLevelDialogOpen] = useState(false)

  const { partner, setting, objectives } = draft
  const language = findLanguage(partner.language)
  const level = language?.levels.find((l) => l.value === partner.level)

  function updatePartner(changes: Partial<ConversationPartner>) {
    setDraft({ ...draft, partner: { ...partner, ...changes } })
  }

  // Levels depend on the language, so pick a level right after choosing one.
  function chooseLanguage(option: Language | null) {
    if (!option) return
    updatePartner({ language: option.value, level: '' })
    setLevelDialogOpen(true)
  }

  function chooseLevel(value: string) {
    updatePartner({ level: value })
    setLevelDialogOpen(false)
  }

  function setObjectives(next: Objective[]) {
    setDraft({ ...draft, objectives: next })
  }

  function setObjectiveText(index: number, text: string) {
    setObjectives(objectives.map((o, i) => (i === index ? { ...o, text } : o)))
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    onSave({ ...draft, objectives: objectives.map((o) => ({ ...o, text: o.text.trim() })).filter((o) => o.text) })
    navigate('/scenario')
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <h1>Create a scenario</h1>

      {/* ---- Conversation Partner: who the student talks to ---- */}
      <section className="card stack">
        <h2>Conversation Partner</h2>

        <label className="field">
          <span className="field-label">Name</span>
          <input
            className="input"
            value={partner.name}
            maxLength={100}
            placeholder="Lucy..."
            onChange={(e) => updatePartner({ name: e.target.value })}
            onKeyDown={fillSuggestionOnTab((name) => updatePartner({ name }))}
          />
        </label>

        <label className="field">
          <span className="field-label">Biography</span>
          <input
            className="input"
            value={partner.bio}
            maxLength={BIO_MAX}
            placeholder="A friendly barista at a busy café in California..."
            onChange={(e) => updatePartner({ bio: e.target.value })}
            onKeyDown={fillSuggestionOnTab((bio) => updatePartner({ bio }))}
          />
          <span className="field-hint">
            {partner.bio.length}/{BIO_MAX}
          </span>
        </label>

        <div className="field">
          <label className="field-label" htmlFor="language">
            Language
          </label>
          <Select<Language>
            inputId="language"
            unstyled
            classNamePrefix="select"
            options={LANGUAGES}
            value={language ?? null}
            onChange={chooseLanguage}
            placeholder="Search languages..."
            menuPlacement="auto"
          />
        </div>

        {language && (
          <div className="row">
            <span className="field-label">Language level:</span>
            <button type="button" className="chip" onClick={() => setLevelDialogOpen(true)}>
              {level ? level.label : 'Choose a level...'}
            </button>
          </div>
        )}
      </section>

      {/* ---- Scenario Goals: where it happens and what the student must do ---- */}
      <section className="card stack">
        <h2>Scenario Goals</h2>

        <label className="field">
          <span className="field-label">Setting</span>
          <textarea
            className="input"
            rows={3}
            value={setting}
            maxLength={SETTING_MAX}
            placeholder="A small café on a busy Saturday morning..."
            onChange={(e) => setDraft({ ...draft, setting: e.target.value })}
            onKeyDown={fillSuggestionOnTab((value) => setDraft({ ...draft, setting: value }))}
          />
          <span className="field-hint">
            {setting.length}/{SETTING_MAX}
          </span>
        </label>

        <div className="field">
          <span className="field-label">Objectives</span>
          <p className="muted">What the student must accomplish during the conversation.</p>
          <div className="stack">
            {objectives.map((objective, index) => (
              <div key={index} className="row">
                <input
                  className="input"
                  value={objective.text}
                  placeholder={index === 0 ? 'Order a drink and a pastry...' : 'Another objective...'}
                  aria-label={`Objective ${index + 1}`}
                  onChange={(e) => setObjectiveText(index, e.target.value)}
                  // Only the first objective has a real suggestion; "Another objective..." isn't one.
                  onKeyDown={index === 0 ? fillSuggestionOnTab((value) => setObjectiveText(0, value)) : undefined}
                />
                {objectives.length > 1 && (
                  <button
                    type="button"
                    className="btn-link danger"
                    onClick={() => setObjectives(objectives.filter((_, i) => i !== index))}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>
          <button type="button" className="btn-link align-start" onClick={() => setObjectives([...objectives, { text: '', checklist: [] }])}>
            + Add objective
          </button>
        </div>
      </section>

      <div className="actions">
        <span />
        <button type="submit" className="btn btn-primary" disabled={!isComplete(draft)}>
          Next
        </button>
      </div>

      {language && (
        <LevelDialog
          language={language}
          value={partner.level}
          open={levelDialogOpen}
          onChoose={chooseLevel}
          onClose={() => setLevelDialogOpen(false)}
        />
      )}
    </form>
  )
}
