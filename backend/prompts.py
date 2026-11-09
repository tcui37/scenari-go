"""Prompt builders for Gemini. Response shapes come from schemas.py (sent as response_schema)."""
from schemas import ScoreRequest, Scenario


def _describe(scenario: Scenario) -> str:
    p = scenario.partner
    objectives = "\n".join(f"- {o}" for o in scenario.objectives)
    return (
        f"Conversation partner: {p.name} — {p.bio}\n"
        f"Language: {p.language}, student level: CEFR {p.level}\n"
        f"Setting: {scenario.setting}\n"
        f"Objectives the student must achieve:\n{objectives}"
    )


def scripts_prompt(scenario: Scenario) -> str:
    return f"""You are designing a role-play for a language learner.
The student talks to the conversation partner below, played by a voice AI agent.

{_describe(scenario)}

For EACH objective, write a checklist of 3-6 prompts that guide the partner through
that part of the conversation, in order. Each item is either:
- "instruction": guidance for the partner, in English (e.g. "Ask what size they want.")
- "say": a line the partner speaks verbatim, in {scenario.partner.language},
  at CEFR {scenario.partner.level} difficulty. Use "say" sparingly.

Return one script per objective, in the same order."""


def score_prompt(req: ScoreRequest) -> str:
    transcript = "\n".join(f"{line.speaker}: {line.text}" for line in req.transcript)
    return f"""You are grading a language learner's role-play conversation.

{_describe(req.scenario)}

Transcript:
{transcript or "(empty: no conversation took place)"}

Judge each objective only from the transcript. If the transcript is empty, mark every
objective as not met, give overall_score 0, and say no conversation was recorded.
Write feedback in English, addressed to the student, one or two sentences each.

Score from 0 to 100. Return one result per objective, in the same order."""
