// Mirrors backend/game/game.py.

export type Direction = 'up' | 'down' | 'left' | 'right'

export type GameState = {
  grid: number[][] // grid[row][col], tile values (0 = empty)
  player: [row: number, col: number]
}
