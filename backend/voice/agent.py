"""The Guava voice agent that plays the conversation partner.

One agent serves every game. When a call connects, the game hands control to the agent for the
length of the call: the agent reads and advances the game's objectives, and ends the conversation.
The handlers below are a call's life, in order.
"""
import guava
from dotenv import load_dotenv
from guava.commands import SpeedPreset
from guava.events import AgentSpeechEvent, BotSessionEnded, CallerSpeechEvent

from game.game import Game
from game.games import get_game_from_id
from game.scenario import Level

# Slower speech for lower CEFR levels (Guava's presets; "medium" is normal speed).
SPEECH_SPEED_BY_LEVEL: dict[Level, SpeedPreset] = {
    Level.A1: "x-slow",
    Level.A2: "slow",
    Level.B1: "slow",
    Level.B2: "medium",
    Level.C1: "medium",
    Level.C2: "fast",
}

load_dotenv()  # guava.Agent() reads GUAVA_API_KEY when it's constructed
agent = guava.Agent()  # the single agent; main.py starts its one listener. Persona is set per call


@agent.on_call_received
def on_call_received(call_info: guava.CallInfo) -> guava.IncomingCallAction:
    # Only a game that started a conversation itself (Enter next to the partner) gets a call.
    try:
        game = extract_game_from_call_info(call_info)
    except ValueError:
        return guava.DeclineCall()  # not one of our games
    return guava.AcceptCall() if game.in_conversation else guava.DeclineCall()


@agent.on_call_start
def on_call_start(call: guava.Call) -> None:
    game = extract_game_from_call_info(call.call_info)
    partner = game.scenario.partner
    call.set_persona(
        agent_name=partner.name,
        agent_purpose=f"{partner.bio} Setting: {game.scenario.setting}",
        speech_speed=SPEECH_SPEED_BY_LEVEL[partner.level],
    )
    call.set_language_mode(primary=partner.language)
    game.on_start_call()
    _start_next_task(call, game)  # each call is fresh: start wherever the student is


@agent.on_task_complete
def on_task_complete(call: guava.Call, task_name: str) -> None:
    game = extract_game_from_call_info(call.call_info)
    game.complete_objective()
    _start_next_task(call, game)


@agent.on_caller_speech
def on_caller_speech(call: guava.Call, event: CallerSpeechEvent) -> None:
    game = extract_game_from_call_info(call.call_info)
    game.call_summary.record_speech("student", event.utterance, event.utterance_id)


@agent.on_agent_speech
def on_agent_speech(call: guava.Call, event: AgentSpeechEvent) -> None:
    game = extract_game_from_call_info(call.call_info)
    game.call_summary.record_speech("partner", event.utterance)


@agent.on_session_end
def on_session_end(call: guava.Call, event: BotSessionEnded) -> None:
    if event.termination_reason == "user-hangup":
        return
    game = extract_game_from_call_info(call.call_info)
    game.end_conversation(by_agent=True)  # the agent or a failure ended it: hand control back


# --- Helpers ---

def extract_game_from_call_info(call_info: guava.CallInfo) -> Game:
    """The game this call belongs to, from the game_id the browser sent with it. Raises ValueError if none."""
    return get_game_from_id(str(call_info.custom_payload.get("game_id")))


def _start_next_task(call: guava.Call, game: Game) -> None:
    """Give the agent the game's current objective as a task, or wrap up when there's none."""
    if game.is_complete():
        call.hangup("Every objective is done. Wrap up the conversation naturally and say goodbye.")
        return
    objective = game.get_current_objective()
    checklist = [guava.Say(item.text) if item.kind == "say" else item.text for item in objective.checklist]
    goal = objective.text
    call.set_task(
        f"objective_{game.objective_index}",
        objective=f"The student's goal: {goal}. Play your role so they can do it themselves",
        checklist=checklist,
        completion_criteria=f"Complete once the student has done this themselves: {goal}.",
    )
