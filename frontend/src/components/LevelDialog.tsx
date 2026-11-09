import { useEffect, useRef } from 'react'
import Select from 'react-select'
import type { Language, Level } from '../data/languages.ts'

type Props = {
  language: Language
  value: string
  open: boolean
  onChoose: (level: string) => void
  onClose: () => void
}

// Pop-up shown after a language is picked: a searchable list of that language's levels.
export default function LevelDialog({ language, value, open, onChoose, onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  // Sync the native <dialog> with the `open` prop.
  useEffect(() => {
    const dialog = dialogRef.current
    if (open && !dialog?.open) dialog?.showModal()
    if (!open && dialog?.open) dialog.close()
  }, [open])

  return (
    <dialog ref={dialogRef} className="dialog" onClose={onClose}>
      <div className="stack">
        <h2>{language.label} level</h2>
        <p className="muted">How well does the student speak {language.label}?</p>

        {open && (
          <Select<Level>
            unstyled
            classNamePrefix="select"
            options={language.levels}
            value={language.levels.find((level) => level.value === value) ?? null}
            onChange={(level) => level && onChoose(level.value)}
            formatOptionLabel={(level, { context }) =>
              context === 'menu' ? (
                <div>
                  <div>{level.label}</div>
                  <div className="muted">{level.description}</div>
                </div>
              ) : (
                level.label
              )
            }
            placeholder="Search levels..."
            autoFocus
            defaultMenuIsOpen
          />
        )}

        <div className="row">
          <button type="button" className="btn" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </dialog>
  )
}
