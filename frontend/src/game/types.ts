// Mirrors backend/game/game.py and the messages on /ws/game (backend/main.py).
// The browser sends the scenario first, then raw key names; the game interprets them.

export type Position = [row: number, col: number]

export type GameState = {
  grid: number[][] // grid[row][col], tile values (0 = empty)
  player_position: Position // the student
  agent_position: Position // the conversation partner
  in_conversation: boolean // while true, nobody moves
}

// Sent once, right after the server creates the game: what the browser needs to place a voice call.
export type GameCreated = { type: 'game_created'; game_id: string; webrtc_code: string }

// Sent on connect and after every change.
export type StateMessage = { type: 'state' } & GameState

export type ServerMessage = GameCreated | StateMessage
