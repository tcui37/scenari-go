import { useEffect, useRef, useState } from 'react'
import { Link, Navigate } from 'react-router'
import * as Guava from '@guava-ai/guava-sdk/webrtc'
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
  // The server owns the game: this page only sends raw key presses and shows what comes back.
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    let cancelled = false
    let socket: WebSocket | null = null
    let view: GameView | null = null
    let call: Guava.Call | null = null

    newGame(scenario)
      .then(({ game_id, state, webrtc_code }) => {
        if (cancelled) return
        const ws = new WebSocket(`/ws/games/${game_id}`)
        socket = ws

        view = createGame(container, state, (key) => {
          if (ws.readyState === WebSocket.OPEN) ws.send(key)
        })

        ws.onmessage = (event) => {
          const message = JSON.parse(event.data)
          if (message.type !== 'state') return
          view?.render(message)
          setInConversation(message.in_conversation)

          // The voice call follows the game's state: the game decides when a conversation
          // starts and ends, and the browser only places or drops the call.
          if (message.in_conversation && !call) {
            const started = new Guava.Call({ webrtcCode: webrtc_code, customPayload: { game_id } })
            call = started
            started.start().catch(() => {
              setError(`Call failed: ${started.error?.message ?? 'unknown error'}. Press Esc to end the conversation.`)
            })
          } else if (!message.in_conversation && call) {
            call.hangup()
            call = null
            setError('')
          }
        }
      })
      .catch(() => setError('Could not start a game. Is the backend running?'))

    return () => {
      cancelled = true
      socket?.close()
      call?.hangup()
      view?.destroy()
    }
  }, [scenario])

  if (!hasChecklists(scenario)) return <Navigate to="/scenario" replace />

  return (
    <div className="stack">
      <h1>Play</h1>
      <p className="muted">
        {inConversation
          ? `Talking to ${scenario.partner.name}. Press Esc to end the conversation.`
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
