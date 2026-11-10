"""A barebones 2D grid game: the student (player) moves around a grid with the conversation partner (agent)."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import NamedTuple

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


@dataclass
class CallResult:
    """How a conversation ended. The transcript will join this later."""
    termination_reason: str  # "user-hangup" | "bot-hangup" | "bot-failure"


class Game:
    """The player drives the game with keys. During a conversation the game hands control to the
    agent, which drives it through current_objective / complete_objective / end_conversation."""

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
        self.call_results: list[CallResult] = []
        self.update_socket: Callable[[], None] | None = None  # sends the state to the browser; set by main.py

    @classmethod
    def from_scenario(cls, scenario: Scenario, rows: int = 8, cols: int = 10) -> "Game":
        """A new game for `scenario`: empty grid, player top-left, agent bottom-right."""
        return cls(
            scenario=scenario,
            grid=[[EMPTY] * cols for _ in range(rows)],
            player_position=Position(0, 0),
            agent_position=Position(rows - 1, cols - 1),
        )

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
        if not self.in_conversation and self._next_to_agent():
            self.in_conversation = True  # ignored when the agent is out of reach

    def end_conversation(self, result: CallResult | None = None) -> None:
        """The student hung up (Esc) or the agent's call ended; the agent passes how it went."""
        self.in_conversation = False
        if result:
            self.call_results.append(result)
            # The agent ended it, with no key press to answer, so tell the browser from here.
            if self.update_socket:
                self.update_socket()

    def current_objective(self) -> Objective | None:
        """The objective to work on now, or None once every objective is done."""
        index = self.objective_index
        if index >= len(self.scenario.objectives):
            return None
        return Objective(self.scenario.objectives[index], self.scenario.checklists[index])

    def complete_objective(self) -> None:
        """The current objective is done; move on to the next one."""
        self.objective_index += 1

    def _next_to_agent(self) -> bool:
        # Directly up, down, left or right of the agent (no diagonals).
        row_gap = abs(self.player_position.row - self.agent_position.row)
        col_gap = abs(self.player_position.col - self.agent_position.col)
        return row_gap + col_gap == 1

    def _position_in_bounds(self, position: Position) -> bool:
        return 0 <= position.row < len(self.grid) and 0 <= position.col < len(self.grid[0])

    def _position_collision_free(self, position: Position) -> bool:
        is_empty_tile = self.grid[position.row][position.col] == EMPTY  # walls/items will block here later
        return is_empty_tile and position != self.agent_position

    def _can_move_to(self, position: Position) -> bool:
        # Nobody moves while talking (agent movement, once added, should use this too).
        # In-bounds is checked before collision-free: `and` short-circuits, so the grid
        # is never indexed out of range.
        return (
            not self.in_conversation
            and self._position_in_bounds(position)
            and self._position_collision_free(position)
        )

    def state(self) -> dict:
        return {
            "grid": self.grid,
            "player_position": self.player_position,
            "agent_position": self.agent_position,
            "in_conversation": self.in_conversation,
        }
