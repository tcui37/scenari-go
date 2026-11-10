// Mirrors backend/game/game.py. The browser only sends raw key names; the game interprets them.

export type Position = [row: number, col: number]

export type GameState = {
  grid: number[][] // grid[row][col], tile values (0 = empty)
  player_position: Position // the student
  agent_position: Position // the conversation partner
  in_conversation: boolean // while true, nobody moves
}
