import unittest

from game.game import Direction, Game, Position
from game.scenario import Language, Level, Objective, Partner, Scenario


def make_game() -> Game:
    """A 2x2 grid: the player at (0, 0), the agent (Lucy) at (1, 1), two objectives."""
    scenario = Scenario(
        partner=Partner(name="Lucy", bio="A barista.", language=Language.ENGLISH, level=Level.A1),
        setting="A café.",
        objectives=[Objective("Order a drink", []), Objective("Pay", [])],
    )
    return Game.from_scenario(scenario, rows=2, cols=2)


class TestGame(unittest.TestCase):
    def test_starts_walking(self):
        game = make_game()
        self.assertFalse(game.in_conversation)
        self.assertTrue(game.get_subtext().startswith("Use the arrow keys to move."))

    def test_arrow_moves_player(self):
        game = make_game()
        game.handle_key("ArrowRight")
        self.assertEqual(Position(0, 1), game.player_position)
        self.assertEqual(Direction.RIGHT, game.player_facing)

    def test_blocked_move_only_turns(self):
        game = make_game()
        game.handle_key("ArrowUp")  # off the top of the grid
        self.assertEqual(Position(0, 0), game.player_position)
        self.assertEqual(Direction.UP, game.player_facing)

    def test_enter_needs_agent_adjacent(self):
        game = make_game()
        game.handle_key("Enter")  # (0, 0) isn't next to (1, 1)
        self.assertFalse(game.in_conversation)
        game.handle_key("ArrowRight")
        game.handle_key("Enter")
        self.assertTrue(game.in_conversation)
        self.assertEqual("Getting Lucy's attention...", game.get_subtext())

    def test_call_shows_objective(self):
        game = make_game()
        game.handle_key("ArrowRight")
        game.handle_key("Enter")
        game.on_start_call()
        self.assertEqual("Objective: Order a drink", game.get_subtext())

    def test_completing_every_objective(self):
        game = make_game()
        game.complete_objective()
        self.assertFalse(game.is_complete())
        game.complete_objective()
        self.assertTrue(game.is_complete())
        self.assertEqual("All done!", game.get_subtext())
        with self.assertRaises(AssertionError):
            game.get_current_objective()

    def test_escape_ends_conversation(self):
        game = make_game()
        game.handle_key("ArrowRight")
        game.handle_key("Enter")
        game.handle_key("Escape")
        self.assertFalse(game.in_conversation)


if __name__ == "__main__":
    unittest.main()
