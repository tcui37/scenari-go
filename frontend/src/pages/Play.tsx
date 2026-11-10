import { useEffect, useRef, useState } from 'react'
import { Link, Navigate } from 'react-router'
import { newGame } from '../api.ts'
import { createGame, type GameView } from '../game/createGame.ts'
import { hasChecklists } from '../scenario/scenario.ts'
import type { Scenario } from '../scenario/types.ts'

type Props = {
  scenario: Scenario
}

export default function Play({ scenario }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState('')
  const [inConversation, setInConversation] = useState(false)

  // Start a game on the server, then mirror its state over a WebSocket.
  // The server owns the game; this page only sends inputs and draws what comes back.
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    let cancelled = false
    let socket: WebSocket | null = null
    let view: GameView | null = null

    newGame(scenario)
      .then(({ game_id, state }) => {
        if (cancelled) return
        const ws = new WebSocket(`/ws/games/${game_id}`)
        socket = ws
        view = createGame(container, state, (input) => {
          if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(input))
        })
        ws.onmessage = (event) => {
          const message = JSON.parse(event.data)
          if (message.type !== 'state') return
          view?.render(message)
          setInConversation(message.in_conversation)
        }
      })
      .catch(() => setError('Could not start a game. Is the backend running?'))

    return () => {
      cancelled = true
      socket?.close()
      view?.destroy()
    }
  }, [scenario])

  if (!hasChecklists(scenario)) return <Navigate to="/scenario" replace />

  return (
    <div className="stack">
      <h1>Play</h1>
      <p className="muted">
        {inConversation
          ? `Talking to ${scenario.partner.name}. Press Enter to end the conversation.`
          : `Use the arrow keys to move. Press Enter next to ${scenario.partner.name} to talk.`}
      </p>
      {error && <p className="error">{error}</p>}
      <div ref={containerRef} className="game-canvas" />

      <div className="actions">
        <Link to="/scenario" className="btn">
          Back
        </Link>
        <Link to="/summary" className="btn btn-primary">
          Finish scenario
        </Link>
      </div>
    </div>
  )
}
