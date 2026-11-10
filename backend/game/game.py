"""A barebones 2D grid game: one player moving up, down, left and right."""

EMPTY = 0  # tile values; walls and items can be added later

# (row change, column change) for each direction
DIRECTIONS = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}


class Game:
    def __init__(self, rows: int = 8, cols: int = 10):
        self.grid = [[EMPTY] * cols for _ in range(rows)]  # grid[row][col], tiles only
        self.player = [0, 0]  # [row, col], kept separate from the grid

    def move(self, direction: str) -> None:
        dr, dc = DIRECTIONS[direction]  # KeyError for an unknown direction
        row, col = self.player[0] + dr, self.player[1] + dc
        if 0 <= row < len(self.grid) and 0 <= col < len(self.grid[0]):
            self.player = [row, col]  # moves off the edge are ignored

    def state(self) -> dict:
        return {"grid": self.grid, "player": self.player}
