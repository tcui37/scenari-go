"""A barebones 2D grid game: the student (player) moves around a grid with the conversation partner (agent)."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import NamedTuple

from game.call_summary import CallResult, CallSummary
from game.scenario import ChecklistItem, Scenario

EMPTY = 0  # tile values; walls and items can be added later

# (row change, column change) for each direction
DIRECTIONS = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

# Browser key names (KeyboardEvent.key) that move the player
KEY_TO_DIRECTION = {"ArrowUp": "up", "ArrowDown": "down", "ArrowLeft": "left", "ArrowRight": "right"}


class Position(NamedTuple):
    row: int
    col: int


@dataclass
class Objective:
    """One objective and its checklist: what the agent needs to run one part of the conversation."""
    text: str
    checklist: list[ChecklistItem]


class Game:
    """The player drives the game with keys. During a conversation the game hands control to the
    agent, which drives it through current_objective / complete_objective / end_conversation."""

    # --- Creating a game ---

    def __init__(
        self,
        scenario: Scenario,
        grid: list[list[int]],
        player_position: Position,
        agent_position: Position,
    ):
        self.scenario = scenario
        self.grid = grid  # grid[row][col], tiles only
        self.player_position = player_position  # the student
        self.agent_position = agent_position  # the conversation partner
        self.in_conversation = False  # while True, nobody moves
        self.objective_index = 0  # the objective being worked on; len(objectives) once all are done
        self.call_summary = CallSummary()  # what was said in this game's calls, and how they ended
        self._socket_updater: Callable[[], None] | None = None  # sends the state to the browser; see set_socket_updater

    @classmethod
    def from_scenario(cls, scenario: Scenario, rows: int = 8, cols: int = 10) -> "Game":
        """A new game for `scenario`: empty grid, player top-left, agent bottom-right."""
        return cls(
            scenario=scenario,
            grid=[[EMPTY] * cols for _ in range(rows)],
            player_position=Position(0, 0),
            agent_position=Position(rows - 1, cols - 1),
        )

    # --- The browser: what it sees ---

    def state(self) -> dict:
        return {
            "grid": self.grid,
            "player_position": self.player_position,
            "agent_position": self.agent_position,
            "in_conversation": self.in_conversation,
        }

    def set_socket_emission_fn(self, socket_updater: Callable[[], None]) -> None:
        """How to send this game's state to its browser. main.py sets it when the socket connects."""
        self._socket_updater = socket_updater

    def update_socket(self) -> None:
        """Send the current state to the browser, if one is connected."""
        if self._socket_updater:
            self._socket_updater()

    # --- The player: keys from the browser ---

    def handle_key(self, key: str) -> None:
        """Interpret a raw key from the browser. Keys the game doesn't use are ignored."""
        if key in KEY_TO_DIRECTION:
            self.move_player(KEY_TO_DIRECTION[key])
        elif key == "Enter":
            self.press_enter()
        elif key == "Escape":
            self.end_conversation()

    def move_player(self, direction: str) -> None:
        dr, dc = DIRECTIONS[direction]  # KeyError for an unknown direction
        target = Position(self.player_position.row + dr, self.player_position.col + dc)
        if self._can_move_to(target):
            self.player_position = target  # disallowed moves are ignored

    def press_enter(self) -> None:
        """Enter starts a conversation with the agent. The game owns the conversation state."""
        # Directly up, down, left or right of the agent (no diagonals).
        row_gap = abs(self.player_position.row - self.agent_position.row)
        col_gap = abs(self.player_position.col - self.agent_position.col)
        agent_adjacent = row_gap + col_gap == 1
        if not self.in_conversation and agent_adjacent:
            self.in_conversation = True  # ignored when the agent is out of reach

    # --- Movement rules ---

    def _can_move_to(self, position: Position) -> bool:
        # Nobody moves while talking (agent movement, once added, should use this too).
        # In-bounds is checked before collision-free: `and` short-circuits, so the grid
        # is never indexed out of range.
        return (
            not self.in_conversation
            and self._position_in_bounds(position)
            and self._position_collision_free(position)
        )

    def _position_in_bounds(self, position: Position) -> bool:
        return 0 <= position.row < len(self.grid) and 0 <= position.col < len(self.grid[0])

    def _position_collision_free(self, position: Position) -> bool:
        is_empty_tile = self.grid[position.row][position.col] == EMPTY  # walls/items will block here later
        return is_empty_tile and position != self.agent_position

    # --- The conversation: what the voice agent uses during a call ---

    def current_objective(self) -> Objective | None:
        """The objective to work on now, or None once every objective is done."""
        index = self.objective_index
        if index >= len(self.scenario.objectives):
            return None
        return Objective(self.scenario.objectives[index], self.scenario.checklists[index])

    def complete_objective(self) -> None:
        """The current objective is done; move on to the next one."""
        self.objective_index += 1

    def end_conversation(self, result: CallResult | None = None) -> None:
        """The student hung up (Esc) or the agent's call ended; the agent passes how it went."""
        self.in_conversation = False
        if result:
            self.call_summary.call_results.append(result)
            # The agent ended it, with no key press to answer, so tell the browser from here.
            self.update_socket()

