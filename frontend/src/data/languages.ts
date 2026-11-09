// Languages a conversation partner can speak, each with its own proficiency scale.
// English and Spanish both use CEFR; a language with another scale (e.g. JLPT)
// just lists different levels here.

export type Level = { value: string; label: string; description: string }
export type Language = { value: string; label: string; levels: Level[] }

const CEFR_LEVELS: Level[] = [
  { value: 'A1', label: 'A1 · Beginner', description: 'Basic phrases about yourself and everyday needs.' },
  { value: 'A2', label: 'A2 · Elementary', description: 'Simple exchanges on familiar, routine topics.' },
  { value: 'B1', label: 'B1 · Intermediate', description: 'Handles most travel situations and familiar topics.' },
  { value: 'B2', label: 'B2 · Upper intermediate', description: 'Talks fluently and spontaneously with native speakers.' },
  { value: 'C1', label: 'C1 · Advanced', description: 'Expresses ideas fluently, flexibly and precisely.' },
  { value: 'C2', label: 'C2 · Proficient', description: 'Understands virtually everything with ease.' },
]

export const LANGUAGES: Language[] = [
  { value: 'english', label: 'English', levels: CEFR_LEVELS },
  { value: 'spanish', label: 'Spanish', levels: CEFR_LEVELS },
]

export function findLanguage(value: string): Language | undefined {
  return LANGUAGES.find((language) => language.value === value)
}
