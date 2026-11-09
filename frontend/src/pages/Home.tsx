import { useEffect, useState } from 'react'
import { getHello } from '../api.ts'

export default function Home() {
  const [message, setMessage] = useState('Loading...')

  useEffect(() => {
    getHello()
      .then((data) => setMessage(data.message))
      .catch(() => setMessage('Could not reach the backend. Is FastAPI running?'))
  }, [])

  return (
    <>
      <h1>scenari-go</h1>
      <p>{message}</p>
    </>
  )
}
