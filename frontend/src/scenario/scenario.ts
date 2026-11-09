import type { Scenario } from './types.ts'

export const EMPTY_SCENARIO: Scenario = {
  partner: { name: '', bio: '', language: '', level: '' },
  setting: '',
  objectives: [''],
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
    objectives.some((objective) => objective.trim() !== '')
  )
}
