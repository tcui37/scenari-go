"""Request/response models shared by the API routes."""
from typing import Literal

from pydantic import BaseModel, Field


# --- Scenario (what the teacher fills in) ---

class ConversationPartner(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    bio: str = Field(max_length=100)
    language: Literal["english", "spanish"]  # the app's languages; also supported by Guava voice
    level: str  # e.g. "B1"


class ChecklistItem(BaseModel):
    """One prompt for the voice agent, shaped like a Guava task checklist item."""
    # "instruction" -> a plain str checklist item (guidance for the agent)
    # "say"         -> guava.Say (spoken verbatim)
    kind: Literal["instruction", "say"]
    text: str


class Scenario(BaseModel):
    partner: ConversationPartner
    setting: str = Field(max_length=200)
    objectives: list[str] = Field(min_length=1)
    # Parallel to objectives: checklists[i] belongs to objectives[i]. Empty = not generated yet.
    checklists: list[list[ChecklistItem]] = []


# --- What Gemini produces: checklists only (it never repeats the objectives) ---

class GeneratedChecklists(BaseModel):
    checklists: list[list[ChecklistItem]]  # one per objective, same order


# --- Scoring ---

class TranscriptLine(BaseModel):
    speaker: Literal["partner", "student"]
    text: str


class ScoreRequest(BaseModel):
    scenario: Scenario
    transcript: list[TranscriptLine] = []


class ObjectiveScore(BaseModel):
    objective: str
    met: bool
    feedback: str


class ScoreResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100, description="Overall score from 0 to 100")
    summary: str
    objectives: list[ObjectiveScore]
