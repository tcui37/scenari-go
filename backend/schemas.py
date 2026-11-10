"""Request/response models shared by the API routes."""
from typing import Literal

from pydantic import BaseModel, Field


# --- Scenario (what the teacher fills in) ---

class ConversationPartnerModel(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    bio: str = Field(max_length=100)
    language: Literal["english", "spanish"]  # the app's languages; also supported by Guava voice
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]  # CEFR


class ChecklistItemModel(BaseModel):
    """One prompt for the voice agent, shaped like a Guava task checklist item."""
    # "instruction" -> a plain str checklist item (guidance for the agent)
    # "say"         -> guava.Say (spoken verbatim)
    kind: Literal["instruction", "say"]
    text: str


class ScenarioModel(BaseModel):
    partner: ConversationPartnerModel
    setting: str = Field(max_length=200)
    objectives: list[str] = Field(min_length=1)
    # Parallel to objectives: checklists[i] belongs to objectives[i]. Empty = not generated yet.
    checklists: list[list[ChecklistItemModel]] = []


# --- What Gemini produces: checklists only (it never repeats the objectives) ---

class GeneratedChecklistsModel(BaseModel):
    checklists: list[list[ChecklistItemModel]]  # one per objective, same order


# --- Scoring ---

class TranscriptLineModel(BaseModel):
    speaker: Literal["partner", "student"]
    text: str


class ObjectiveScoreModel(BaseModel):
    objective: str
    met: bool
    feedback: str


class ScoreResponseModel(BaseModel):
    overall_score: int = Field(ge=0, le=100, description="Overall score from 0 to 100")
    summary: str
    objectives: list[ObjectiveScoreModel]


class GameSummaryModel(BaseModel):
    """What "Finish scenario" returns: Gemini's evaluation, plus the transcript it was scored on."""
    evaluation: ScoreResponseModel
    transcript: list[TranscriptLineModel]
