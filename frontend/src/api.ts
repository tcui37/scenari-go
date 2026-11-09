// REST calls to the FastAPI backend. Vite proxies /api to localhost:8000 in dev.

export async function getHello(): Promise<{ message: string }> {
  const response = await fetch('/api/hello')
  if (!response.ok) throw new Error(`Request failed: ${response.status}`)
  return response.json()
}
