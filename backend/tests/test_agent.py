"""The voice agent's handlers, called directly with a MockCall, as Guava's docs show:
https://docs.goguava.ai/sdk-reference/agent-testing"""
import unittest

import guava
from guava.events import BotSessionEnded
from guava.testing import MockCall
from guava.types.call_info import WebRTCCallInfo

from game.games import games
from tests.test_game import make_game
from voice.agent import on_call_received, on_call_start, on_session_end, on_task_complete

GAME_ID = "test-game"


def mock_call(game_id: str = GAME_ID) -> MockCall:
    """A WebRTC call from the browser, naming its game the way voiceCall.ts does."""
    return MockCall(call_info=WebRTCCallInfo(webrtc_code="test", custom_payload={"game_id": game_id}))


class TestAgentHandlers(unittest.TestCase):
    def setUp(self):
        self.game = games[GAME_ID] = make_game()  # the mock game the calls belong to

    def tearDown(self):
        games.pop(GAME_ID, None)

    def test_accepts_call_only_in_conversation(self):
        self.assertIsInstance(on_call_received(mock_call().call_info), guava.DeclineCall)
        self.game.in_conversation = True
        self.assertIsInstance(on_call_received(mock_call().call_info), guava.AcceptCall)

    def test_declines_unknown_game(self):
        self.assertIsInstance(on_call_received(mock_call("no-such-game").call_info), guava.DeclineCall)

    def test_call_start_connects_game(self):
        self.game.in_conversation = True  # a call only starts once Enter began a conversation
        on_call_start(mock_call())
        self.assertTrue(self.game.call_connected)
        self.assertEqual("Objective: Order a drink", self.game.get_subtext())

    def test_call_start_with_earlier_transcript(self):
        self.game.call_summary.record_speech("partner", "Hi! What can I get you?")  # from an earlier call
        self.game.in_conversation = True
        on_call_start(mock_call())
        self.assertTrue(self.game.call_connected)

    def test_task_complete_advances_objectives(self):
        on_task_complete(mock_call(), "objective_0")
        self.assertEqual(1, self.game.objective_index)
        on_task_complete(mock_call(), "objective_1")
        self.assertTrue(self.game.is_complete())

    def test_session_end_by_agent_ends_conversation(self):
        self.game.in_conversation = True
        on_session_end(mock_call(), BotSessionEnded(termination_reason="user-hangup"))
        self.assertTrue(self.game.in_conversation)  # the browser's Esc already handled it
        on_session_end(mock_call(), BotSessionEnded(termination_reason="bot-hangup"))
        self.assertFalse(self.game.in_conversation)


if __name__ == "__main__":
    unittest.main()
