"""Prompt builders for Gemini. Response shapes come from schemas.py (sent as response_schema)."""
from game.call_summary import TranscriptLine
from game.scenario import Scenario


def checklists_prompt(scenario: Scenario) -> str:
    return f"""You are designing a role-play for a language learner.
The student talks to the conversation partner below, played by an AI.

{scenario.get_description()}

For EACH objective, write a checklist of 1-2 prompts that guide the partner through
that part of the conversation, in order. Each item is either:
- "instruction": guidance for the partner, in English (e.g. "Ask what size they want.")
- "say": a line the partner speaks verbatim, in {scenario.partner.language},
  at CEFR {scenario.partner.level} difficulty. Use "say" sparingly.

Return exactly {len(scenario.objectives)} checklist(s): one per objective, in the same order.
Each objective is one unit, even if it asks for several things (e.g. "order a drink and a pastry"
gets a single checklist covering both). Never split an objective into multiple checklists."""


def score_prompt(scenario: Scenario, transcript: list[TranscriptLine]) -> str:
    lines = "\n".join(f"{line.speaker}: {line.text}" for line in transcript)
    return f"""You are grading a language learner's role-play conversation.

{scenario.get_description()}

Transcript:
{lines or "(empty: no conversation took place)"}

Judge each objective only from the transcript. If the transcript is empty, mark every
objective as not met, give overall_score 0, and say no conversation was recorded.
Write feedback in English, addressed to the student, one or two sentences each.

Score from 0 to 100. Return one result per objective, in the same order."""
