"""The scenario the game runs on: plain objects, built once from the API's ScenarioModel (schemas.py)."""
from dataclasses import dataclass
from enum import StrEnum

from schemas import ScenarioModel


class Language(StrEnum):
    ENGLISH = "english"
    SPANISH = "spanish"


class Level(StrEnum):
    """CEFR levels."""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


@dataclass
class Partner:
    name: str
    bio: str
    language: Language
    level: Level


@dataclass
class ChecklistItem:
    kind: str  # "instruction" | "say"
    text: str


@dataclass
class Objective:
    """One objective and its checklist: what the agent needs to run one part of the conversation."""
    text: str
    checklist: list[ChecklistItem]  # empty until generated


@dataclass
class Scenario:
    partner: Partner
    setting: str
    objectives: list[Objective]

    @classmethod
    def from_model(cls, model: ScenarioModel) -> "Scenario":
        p = model.partner
        return cls(
            partner=Partner(name=p.name, bio=p.bio, language=Language(p.language), level=Level(p.level)),
            setting=model.setting,
            objectives=[
                Objective(o.text, [ChecklistItem(kind=i.kind, text=i.text) for i in o.checklist])
                for o in model.objectives
            ],
        )

    def get_description(self) -> str:
        """The partner, setting and objectives, as plain text for prompts."""
        p = self.partner
        objectives = "\n".join(f"- {o.text}" for o in self.objectives)
        return (
            f"Conversation partner: {p.name} — {p.bio}\n"
            f"Language: {p.language}, student level: CEFR {p.level}\n"
            f"Setting: {self.setting}\n"
            f"Objectives the student must achieve:\n{objectives}"
        )
