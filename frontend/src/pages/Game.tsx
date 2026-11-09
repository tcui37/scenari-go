import { useState, type FormEvent } from 'react'
import { useEcho } from '../useEcho.ts'

export default function Game() {
  const { messages, send } = useEcho()
  const [text, setText] = useState('')

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    send(text)
    setText('')
  }

  return (
    <>
      <h1>Game</h1>
      <p>The grid goes here. For now, test the WebSocket:</p>

      <form onSubmit={handleSubmit}>
        <input value={text} onChange={(e) => setText(e.target.value)} />
        <button type="submit">Send</button>
      </form>

      <ul>
        {messages.map((msg, i) => (
          <li key={i}>{msg}</li>
        ))}
      </ul>
    </>
  )
}
