import type { Scenario } from './types.ts'

export const EMPTY_SCENARIO: Scenario = {
  partner: { name: '', bio: '', language: '', level: '' },
  setting: '',
  objectives: [{ text: '', checklist: [] }],
}

// A scenario is ready to play once every field is filled in.
export function isComplete(scenario: Scenario): boolean {
  const { partner, setting, objectives } = scenario
  return (
    partner.name.trim() !== '' &&
    partner.bio.trim() !== '' &&
    partner.language !== '' &&
    partner.level !== '' &&
    setting.trim() !== '' &&
    objectives.some((objective) => objective.text.trim() !== '')
  )
}

export function hasChecklists(scenario: Scenario): boolean {
  return scenario.objectives.some((objective) => objective.checklist.length > 0)
}

// The same scenario with every checklist cleared, i.e. only what the teacher typed.
export function withoutChecklists(scenario: Scenario): Scenario {
  return { ...scenario, objectives: scenario.objectives.map((objective) => ({ ...objective, checklist: [] })) }
}
