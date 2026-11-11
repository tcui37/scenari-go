import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import './index.css'
import App from './App.tsx'
import { playSound, type SoundName } from './sound.ts'

// Every button clicks, on every page: <button>s and links styled as buttons (.btn).
// A button can pick another sound with data-sound="<name>". A disabled <button> gets no click event.
document.addEventListener('click', (event) => {
  const button = event.target instanceof Element ? event.target.closest<HTMLElement>('button, .btn') : null
  if (button) playSound((button.dataset.sound as SoundName | undefined) ?? 'click')
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
