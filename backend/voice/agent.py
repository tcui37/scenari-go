"""The Guava voice agent that plays the conversation partner.

One agent serves every game. When a call connects, the game hands control to the agent for the
length of the call: the agent reads and advances the game's objectives, and ends the conversation.
"""
from collections.abc import Callable

import guava
from guava.commands import SpeedPreset
from guava.events import AgentSpeechEvent, BotSessionEnded, CallerSpeechEvent

from game.game import Game
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


def create_agent(game_id_to_game: Callable[[str], Game | None]) -> guava.Agent:
    """The handlers below are a call's life, in order. `find_game(game_id)` finds the call's game."""
    agent = guava.Agent()  # the persona is set per call, from the game's scenario

    def extract_game_from_caller(call_info: guava.CallInfo) -> Game | None:
        # TODO: revisit. The browser sends the game ID with the call (customPayload).
        if call_info.call_type != "webrtc":
            return None
        return game_id_to_game(str(call_info.custom_payload.get("game_id")))

    @agent.on_call_received
    def on_call_received(call_info: guava.CallInfo) -> guava.IncomingCallAction:
        # Only a game that started a conversation itself (Enter next to the partner) gets a call.
        game = extract_game_from_caller(call_info)
        return guava.AcceptCall() if game and game.in_conversation else guava.DeclineCall()

    @agent.on_call_start
    def on_call_start(call: guava.Call) -> None:
        if game := extract_game_from_caller(call.call_info):
            partner = game.scenario.partner
            call.set_persona(
                agent_name=partner.name,
                agent_purpose=f"{partner.bio} Setting: {game.scenario.setting}",
                speech_speed=SPEECH_SPEED_BY_LEVEL[partner.level],
            )
            call.set_language_mode(primary=partner.language)
            game.start_call()
            _start_objective(call, game, game.objective_index)  # each call is fresh: start wherever the student is

    @agent.on_task_complete
    def on_task_complete(call: guava.Call, task_name: str) -> None:
        if game := extract_game_from_caller(call.call_info):
            game.complete_objective()
            _start_objective(call, game, game.objective_index)

    @agent.on_caller_speech
    def on_caller_speech(call: guava.Call, event: CallerSpeechEvent) -> None:
        if game := extract_game_from_caller(call.call_info):
            game.call_summary.record_speech("student", event.utterance, event.utterance_id)

    @agent.on_agent_speech
    def on_agent_speech(call: guava.Call, event: AgentSpeechEvent) -> None:
        if game := extract_game_from_caller(call.call_info):
            game.call_summary.record_speech("partner", event.utterance)

    @agent.on_session_end
    def on_session_end(call: guava.Call, event: BotSessionEnded) -> None:
        if event.termination_reason == "user-hangup":
            return
        if game := extract_game_from_caller(call.call_info):
            game.end_conversation(by_agent=True)  # the agent or a failure ended it: hand control back

    return agent


# --- Helpers ---

def _start_objective(call: guava.Call, game: Game, index: int) -> None:
    """Give the agent the objective at `index` as a task, or wrap up when there's none."""
    objectives, checklists = game.scenario.objectives, game.scenario.checklists
    if index >= len(objectives):
        call.hangup("Every objective is done. Wrap up the conversation naturally and say goodbye.")
        return
    checklist = [guava.Say(item.text) if item.kind == "say" else item.text for item in checklists[index]]
    
    goal = objectives[index]
    call.set_task(
        f"objective_{index}",
        objective=f"The student's goal: {goal}. Play your role so they can do it themselves",
        checklist=checklist,
        completion_criteria=f"Complete once the student has done this themselves: {goal}.",
    )
