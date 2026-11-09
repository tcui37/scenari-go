// Boilerplate 2D grid game in PixiJS (https://pixijs.com/8.x/guides/getting-started/quick-start).
// Plain TypeScript with no React, so this logic can later move behind the backend game engine.
import { Application, Assets, Graphics, Sprite } from 'pixi.js'

const COLS = 10
const ROWS = 8
const TILE = 64 // px
const PLAYER_TEXTURE = 'https://pixijs.com/assets/bunny.png' // sample sprite from the PixiJS docs

const MOVES: Record<string, [dx: number, dy: number]> = {
  ArrowUp: [0, -1],
  ArrowDown: [0, 1],
  ArrowLeft: [-1, 0],
  ArrowRight: [1, 0],
}

// Colors come from the CSS tokens in src/styles/tokens.css.
function token(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

function drawGrid(): Graphics {
  const grid = new Graphics()
  for (let row = 0; row < ROWS; row++) {
    for (let col = 0; col < COLS; col++) {
      const color = (row + col) % 2 === 0 ? token('--color-game-tile') : token('--color-game-tile-alt')
      grid
        .rect(col * TILE, row * TILE, TILE, TILE)
        .fill(color)
        .stroke({ width: 1, color: token('--color-game-grid-line') })
    }
  }
  return grid
}

/** Mounts the game into `container`. Returns a cleanup function that tears it down. */
export function createGame(container: HTMLElement): () => void {
  const app = new Application()
  const position = { col: 0, row: 0 }
  let player: Sprite | null = null
  let initialized = false
  let destroyed = false

  function placePlayer() {
    if (!player) return
    player.x = position.col * TILE + TILE / 2
    player.y = position.row * TILE + TILE / 2
  }

  function onKeyDown(event: KeyboardEvent) {
    const move = MOVES[event.key]
    if (!move) return
    event.preventDefault() // stop arrow keys from scrolling the page
    position.col = clamp(position.col + move[0], 0, COLS - 1)
    position.row = clamp(position.row + move[1], 0, ROWS - 1)
    placePlayer()
  }

  // Pixi's init is async; wrap it in a function (top-level await breaks Vite builds).
  async function init() {
    await app.init({ width: COLS * TILE, height: ROWS * TILE, background: token('--color-game-bg') })
    initialized = true
    if (destroyed) {
      app.destroy(true) // cleanup ran while init was pending (e.g. React StrictMode)
      return
    }
    container.appendChild(app.canvas)
    app.stage.addChild(drawGrid())

    const texture = await Assets.load(PLAYER_TEXTURE)
    if (destroyed) return
    player = new Sprite(texture)
    player.anchor.set(0.5)
    app.stage.addChild(player)
    placePlayer()
    window.addEventListener('keydown', onKeyDown)
  }

  init()

  return () => {
    destroyed = true
    window.removeEventListener('keydown', onKeyDown)
    if (initialized) app.destroy(true, { children: true })
  }
}
