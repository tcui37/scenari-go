"""What a game records about its calls: everything said, and how each call ended."""
from dataclasses import dataclass, field


@dataclass
class CallResult:
    """How a conversation ended."""
    termination_reason: str  # "user-hangup" | "bot-hangup" | "bot-failure"


@dataclass
class TranscriptLine:
    """One thing said during a call."""
    speaker: str  # "student" | "partner"
    text: str
    utterance_id: str | None = None  # speech recognition re-sends a line as it refines it; same id = same line


@dataclass
class CallSummary:
    """All of a game's calls, in order. The voice agent records into it; "Finish scenario" scores it."""
    transcript: list[TranscriptLine] = field(default_factory=list)
    call_results: list[CallResult] = field(default_factory=list)

    def record_speech(self, speaker: str, text: str, utterance_id: str | None = None) -> None:
        """Add a line to the transcript, or update an earlier version of the same utterance."""
        if utterance_id:
            for line in reversed(self.transcript):
                if line.utterance_id == utterance_id:
                    line.text = text
                    return
        self.transcript.append(TranscriptLine(speaker, text, utterance_id))
