// Mirrors backend/game/game.py.

export type Direction = 'up' | 'down' | 'left' | 'right'

export type Position = [row: number, col: number]

export type GameState = {
  grid: number[][] // grid[row][col], tile values (0 = empty)
  player_position: Position // the student
  agent_position: Position // the conversation partner
  in_conversation: boolean // while true, nobody moves
}

// Messages the browser sends over the game socket.
export type GameInput =
  | { type: 'move'; direction: Direction }
  | { type: 'enter' } // the server's game decides what Enter does
