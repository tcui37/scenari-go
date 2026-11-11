// Mirrors backend/schemas.py.

export type ConversationPartner = {
  name: string
  bio: string // <= 200 characters
  language: string // a value from data/languages.ts
  level: string // e.g. "B1"
}

export type Scenario = {
  partner: ConversationPartner
  setting: string // <= 200 characters
  objectives: Objective[]
}

export type Objective = {
  text: string
  checklist: ChecklistItem[] // empty = not generated yet
}

// One prompt for the voice agent. Maps to a Guava task checklist item:
// "instruction" -> plain string, "say" -> guava.Say (spoken verbatim).
export type ChecklistItem = {
  kind: 'instruction' | 'say'
  text: string
}

export type TranscriptLine = {
  speaker: 'partner' | 'student'
  text: string
}

export type ScoreResponse = {
  overall_score: number
  summary: string
  objectives: { objective: string; met: boolean; feedback: string }[]
}

// What "Finish scenario" returns: Gemini's evaluation, plus the transcript it was scored on.
export type GameSummary = {
  evaluation: ScoreResponse
  transcript: TranscriptLine[]
}
