import { useEffect, useRef, useState } from 'react'

// Opens a WebSocket to the FastAPI /ws endpoint and collects every reply.
export function useEcho() {
  const socketRef = useRef<WebSocket | null>(null)
  const [messages, setMessages] = useState<string[]>([])

  useEffect(() => {
    const socket = new WebSocket('/ws')
    socket.onmessage = (event) => setMessages((prev) => [...prev, event.data])
    socketRef.current = socket
    return () => socket.close()
  }, [])

  function send(text: string) {
    socketRef.current?.send(text)
  }

  return { messages, send }
}
