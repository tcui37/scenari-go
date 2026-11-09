import { useEffect, useRef } from 'react'
import { Link, Navigate } from 'react-router'
import { createGame } from '../game/createGame.ts'
import type { ObjectiveScript } from '../scenario/types.ts'

type Props = {
  scripts: ObjectiveScript[] | null
}

export default function Play({ scripts }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  // createGame returns its own cleanup, which React runs on unmount.
  useEffect(() => {
    if (containerRef.current) return createGame(containerRef.current)
  }, [])

  if (!scripts) return <Navigate to="/scenario" replace />

  return (
    <div className="stack">
      <h1>Play</h1>
      <p className="muted">Use the arrow keys to move.</p>
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
