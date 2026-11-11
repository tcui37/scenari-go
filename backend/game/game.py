"""A barebones 2D grid game: the student (player) moves around a grid with the conversation partner (agent)."""
from collections.abc import Callable
from enum import Enum
from typing import NamedTuple

from game.call_summary import CallSummary
from game.scenario import Objective, Scenario

EMPTY = 0  # tile values; walls and items can be added later


class Direction(Enum):
    """Which way a character moves or faces."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


# (row change, column change) for each direction
DIRECTIONS: dict[Direction, tuple[int, int]] = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
    Direction.RIGHT: (0, 1),
}

# Browser key names (KeyboardEvent.key) that move the player
KEY_TO_DIRECTION = {
    "ArrowUp": Direction.UP,
    "ArrowDown": Direction.DOWN,
    "ArrowLeft": Direction.LEFT,
    "ArrowRight": Direction.RIGHT,
}


class Position(NamedTuple):
    row: int
    col: int


class Game:
    """The player drives the game with keys. During a conversation the game hands control to the
    agent, which drives it through is_complete / get_current_objective / complete_objective / end_conversation."""

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
        self.player_facing = Direction.DOWN  # the way the player looks; set by the arrow keys
        self.agent_facing = Direction.LEFT
        self.in_conversation = False  # while True, nobody moves
        self.call_connected = False  # True once the voice call picks up, until the conversation ends
        self.objective_index = 0  # the objective being worked on; len(objectives) once all are done
        self.call_summary = CallSummary()  # what was said in this game's calls
        self._socket_updater: Callable[[], None] | None = None  # sends the state to the browser; see set_socket_emission_fn

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
            "player_facing": self.player_facing.value,  # .value: a plain Enum isn't JSON
            "agent_facing": self.agent_facing.value,
            "in_conversation": self.in_conversation,
            "subtext": self.get_subtext(),
        }

    def get_subtext(self) -> str:
        """The line shown under "Play", worked out from the state, so nothing has to keep it in sync."""
        if not self.in_conversation and not self.is_complete():  # walking over
            return f"Use the arrow keys to move. Press Enter next to {self.scenario.partner.name} to talk."
        if self.in_conversation and not self.call_connected:  # Enter pressed, call connecting
            return f"Getting {self.scenario.partner.name}'s attention..."
        if not self.is_complete():  # talking
            return f"Objective: {self.get_current_objective().text}"
        return "All done!"  # every objective done, in or out of the call

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

    def move_player(self, direction: Direction) -> None:
        if self.in_conversation:
            return  # mid-conversation, the player keeps facing the agent
        self.player_facing = direction  # turns even when the move is blocked
        dr, dc = DIRECTIONS[direction]
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
        """True if something can step onto `position`. It must be:
        - outside a conversation: nobody moves while talking (agent movement should use this too)
        - in bounds: checked first, so the collision check never indexes past the grid
        - collision-free: an empty tile that the agent isn't on
        """
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

    def is_complete(self) -> bool:
        """True once every objective is done."""
        return self.objective_index >= len(self.scenario.objectives)

    def get_current_objective(self) -> Objective:
        """The objective to work on now. Check is_complete first: there is none once all are done."""
        assert not self.is_complete(), "get_current_objective called after every objective is done"
        return self.scenario.objectives[self.objective_index]

    def on_start_call(self) -> None:
        """The voice call connected: show the objective at hand."""
        self.call_connected = True
        self.update_socket()  # from the agent's thread, with no key press to answer

    def complete_objective(self) -> None:
        """The current objective is done; move on to the next one, and show it."""
        self.objective_index += 1
        self.update_socket()  # from the agent's thread, with no key press to answer

    def end_conversation(self, by_agent: bool = False) -> None:
        """The student hung up (Esc), or the agent's call ended (by_agent)."""
        self.in_conversation = False
        self.call_connected = False
        if by_agent:
            # The agent ended it, with no key press to answer, so tell the browser from here.
            self.update_socket()

