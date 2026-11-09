"""Request/response models shared by the API routes."""
from typing import Literal

from pydantic import BaseModel, Field


# --- Scenario (what the teacher fills in) ---

class ConversationPartner(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    bio: str = Field(max_length=100)
    language: str  # e.g. "spanish"
    level: str  # e.g. "B1"


class Scenario(BaseModel):
    partner: ConversationPartner
    setting: str = Field(max_length=200)
    objectives: list[str] = Field(min_length=1)


# --- Scripts (one per objective, shaped like a Guava task checklist) ---

class ChecklistItem(BaseModel):
    # "instruction" -> a plain str checklist item (guidance for the agent)
    # "say"         -> guava.Say (spoken verbatim)
    kind: Literal["instruction", "say"]
    text: str


class ObjectiveScript(BaseModel):
    objective: str
    checklist: list[ChecklistItem]


class ScriptsResponse(BaseModel):
    scripts: list[ObjectiveScript]


# --- Scoring ---

class TranscriptLine(BaseModel):
    speaker: Literal["partner", "student"]
    text: str


class ScoreRequest(BaseModel):
    scenario: Scenario
    scripts: list[ObjectiveScript]
    transcript: list[TranscriptLine] = []


class ObjectiveScore(BaseModel):
    objective: str
    met: bool
    feedback: str


class ScoreResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100, description="Overall score from 0 to 100")
    summary: str
    objectives: list[ObjectiveScore]
