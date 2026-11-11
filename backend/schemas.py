"""Request/response models shared by the API routes."""
from typing import Literal

from pydantic import BaseModel, Field

from game.call_summary import TranscriptLine


# --- Scenario (what the teacher fills in) ---

class ConversationPartnerModel(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    bio: str = Field(max_length=200)
    language: Literal["english", "spanish"]  # the app's languages; also supported by Guava voice
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]  # CEFR


class ChecklistItemModel(BaseModel):
    """One prompt for the voice agent, shaped like a Guava task checklist item."""
    # "instruction" -> a plain str checklist item (guidance for the agent)
    # "say"         -> guava.Say (spoken verbatim)
    kind: Literal["instruction", "say"]
    text: str


class ObjectiveModel(BaseModel):
    text: str = Field(min_length=1)
    checklist: list[ChecklistItemModel] = []  # empty = not generated yet


class ScenarioModel(BaseModel):
    partner: ConversationPartnerModel
    setting: str = Field(max_length=200)
    objectives: list[ObjectiveModel] = Field(min_length=1)


# --- What Gemini produces: checklists only (it never repeats the objectives) ---

class GeneratedChecklistsModel(BaseModel):
    checklists: list[list[ChecklistItemModel]]  # one per objective, same order


# --- Scoring ---

class TranscriptLineModel(BaseModel):
    speaker: Literal["partner", "student"]
    text: str

    @classmethod
    def from_line(cls, line: TranscriptLine) -> "TranscriptLineModel":
        """The API shape of one of the game's transcript lines (its utterance_id stays internal)."""
        return cls(speaker=line.speaker, text=line.text)


class ObjectiveScoreModel(BaseModel):
    objective: str
    met: bool
    feedback: str


class GeneratedScoreModel(BaseModel):
    """What Gemini produces when grading: a verdict per objective. It doesn't give the score."""
    summary: str
    objectives: list[ObjectiveScoreModel]  # one per objective, same order


class ScoreResponseModel(GeneratedScoreModel):
    overall_score: int = Field(ge=0, le=100)  # the share of objectives met, out of 100


class GameSummaryModel(BaseModel):
    """What "Finish scenario" returns: Gemini's evaluation, plus the transcript it was scored on."""
    evaluation: ScoreResponseModel
    transcript: list[TranscriptLineModel]
