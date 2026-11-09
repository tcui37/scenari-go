import { useEffect, useRef, useState } from 'react'
import * as Guava from '@guava-ai/guava-sdk/webrtc'

const WEBRTC_CODE = import.meta.env.VITE_GUAVA_WEBRTC_CODE

export default function Voice() {
  const callRef = useRef<Guava.Call | null>(null)
  const [state, setState] = useState<Guava.CallState>('not-started')
  const [error, setError] = useState('')

  // Hang up if the user navigates away mid-call.
  useEffect(() => () => void callRef.current?.hangup(), [])

  // Must run from a click: browsers only allow mic access after a user gesture.
  async function startCall() {
    setError('')
    const call = new Guava.Call({ webrtcCode: WEBRTC_CODE })
    call.onStateChange(setState)
    callRef.current = call
    try {
      await call.start()
    } catch {
      setError(call.error?.message ?? 'Call failed')
    }
  }

  async function hangUp() {
    await callRef.current?.hangup()
  }

  const inCall = state !== 'not-started' && state !== 'ended'

  return (
    <>
      <h1>Voice</h1>
      {!WEBRTC_CODE && <p>Set VITE_GUAVA_WEBRTC_CODE in frontend/.env.local</p>}

      <button onClick={startCall} disabled={inCall || !WEBRTC_CODE}>
        Start call
      </button>
      <button onClick={hangUp} disabled={!inCall}>
        Hang up
      </button>

      <p>State: {state}</p>
      {error && <p>Error: {error}</p>}
    </>
  )
}
