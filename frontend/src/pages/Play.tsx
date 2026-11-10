import { useEffect, useRef, useState } from 'react'
import { Link, Navigate } from 'react-router'
import { summarizeGame } from '../api.ts'
import { createGame, type GameView } from '../game/createGame.ts'
import type { ServerMessage } from '../game/types.ts'
import { createVoiceCall, type VoiceCall } from '../game/voiceCall.ts'
import { hasChecklists } from '../scenario/scenario.ts'
import type { GameSummary, Scenario } from '../scenario/types.ts'

type Props = {
  scenario: Scenario
  onFinish: (summary: GameSummary) => void
}

export default function Play({ scenario, onFinish }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const socketRef = useRef<WebSocket | null>(null) // so "Finish scenario" can reach the game
  const gameIdRef = useRef<string | null>(null)
  const [error, setError] = useState('')
  const [inConversation, setInConversation] = useState(false)
  const [finishing, setFinishing] = useState(false)

  // One WebSocket is one game: the server creates it from the scenario we send first, then
  // owns it. This page only sends raw key presses and shows the state that comes back.
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    const ws = new WebSocket('/ws/game')
    socketRef.current = ws
    let view: GameView | null = null
    let voiceCall: VoiceCall | null = null

    function sendKey(key: string) {
      if (ws.readyState === WebSocket.OPEN) ws.send(key)
    }

    ws.onopen = () => ws.send(JSON.stringify(scenario)) // the first message creates the game
    ws.onclose = () => setError('Lost the connection to the game. Go Back and press Play again.')

    ws.onmessage = (event) => {
      const message: ServerMessage = JSON.parse(event.data)
      if (message.type === 'game_created') {
        gameIdRef.current = message.game_id
        voiceCall = createVoiceCall(message, setError)
      } else {
        view ??= createGame(container, message, sendKey)
        view.render(message)
        setInConversation(message.in_conversation)
        voiceCall?.follow(message.in_conversation)
      }
    }

    return () => {
      ws.onclose = null // closing it ourselves isn't an error
      ws.close()
      voiceCall?.hangup()
      view?.destroy()
    }
  }, [scenario])

  // Score the conversation while the game still exists (it ends when this page closes its socket).
  async function finish() {
    const gameId = gameIdRef.current
    if (!gameId) return
    socketRef.current?.send('Escape') // ends any conversation, which hangs up the call
    setFinishing(true)
    setError('')
    try {
      onFinish(await summarizeGame(gameId))
    } catch (e) {
      setError((e as Error).message)
      setFinishing(false)
    }
  }

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
        <button type="button" className="btn btn-primary" onClick={finish} disabled={finishing}>
          {finishing ? 'Scoring your conversation...' : 'Finish scenario'}
        </button>
      </div>
    </div>
  )
}
