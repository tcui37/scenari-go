import { NavLink, Route, Routes } from 'react-router'
import Home from './pages/Home.tsx'
import Game from './pages/Game.tsx'

export default function App() {
  return (
    <>
      <nav>
        <NavLink to="/">Home</NavLink>
        <NavLink to="/game">Game</NavLink>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/game" element={<Game />} />
        </Routes>
      </main>
    </>
  )
}
