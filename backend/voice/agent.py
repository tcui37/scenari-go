"""The Guava voice agent that plays the conversation partner.

One agent serves every game. When a call connects, the game hands control to the agent for the
length of the call: the agent reads and advances the game's objectives, and ends the conversation.
"""
from collections.abc import Callable

import guava
from guava.events import BotSessionEnded

from game.game import CallResult, Game


def create_agent(find_game: Callable[[str], Game | None]) -> guava.Agent:
    """The handlers below are a call's life, in order. `find_game(game_id)` finds the call's game."""
    agent = guava.Agent()  # the persona is set per call, from the game's scenario

    def game_for(call_info: guava.CallInfo) -> Game | None:
        return find_game(_game_id(call_info))

    @agent.on_call_received
    def on_call_received(call_info: guava.CallInfo) -> guava.IncomingCallAction:
        # Only a game that started a conversation itself (Enter next to the partner) gets a call.
        game = game_for(call_info)
        return guava.AcceptCall() if game and game.in_conversation else guava.DeclineCall()

    @agent.on_call_start
    def on_call_start(call: guava.Call) -> None:
        if game := game_for(call.call_info):
            partner = game.scenario.partner
            call.set_persona(agent_name=partner.name, agent_purpose=f"{partner.bio} Setting: {game.scenario.setting}")
            call.set_language_mode(primary=partner.language)
            _start_next_objective(call, game)

    @agent.on_task_complete
    def on_task_complete(call: guava.Call, task_name: str) -> None:
        if game := game_for(call.call_info):
            game.complete_objective()
            _start_next_objective(call, game)

    @agent.on_session_end
    def on_session_end(call: guava.Call, event: BotSessionEnded) -> None:
        # Runs however the call ended (student, agent or failure): hand control back to the player.
        if game := game_for(call.call_info):
            game.end_conversation(CallResult(termination_reason=event.termination_reason))

    return agent


# --- Helpers ---

def _game_id(call_info: guava.CallInfo) -> str:
    # TODO: revisit. The browser sends the game ID with the call (customPayload).
    if call_info.call_type != "webrtc":
        return ""
    return str(call_info.custom_payload.get("game_id"))


def _start_next_objective(call: guava.Call, game: Game) -> None:
    """Give the agent the game's current objective as a task, or wrap up when none are left."""
    objective = game.current_objective()
    if objective is None:
        call.hangup("Every objective is done. Wrap up the conversation naturally and say goodbye.")
        return
    # "say" items are spoken verbatim; "instruction" items are plain guidance for the agent.
    checklist = [guava.Say(item.text) if item.kind == "say" else item.text for item in objective.checklist]
    call.set_task(f"objective_{game.objective_index}", objective=objective.text, checklist=checklist)
