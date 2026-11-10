// Draws the grid game with PixiJS (https://pixijs.com/8.x/guides/getting-started/quick-start).
// View only: the backend owns the game state. This draws whatever state it is given
// and reports arrow-key presses through `onMove`.
import { Application, Assets, Graphics, Sprite } from 'pixi.js'
import type { Direction, GameState } from './types.ts'

const TILE = 64 // px
const PLAYER_TEXTURE = 'https://pixijs.com/assets/bunny.png' // sample sprite from the PixiJS docs

const KEY_TO_DIRECTION: Record<string, Direction> = {
  ArrowUp: 'up',
  ArrowDown: 'down',
  ArrowLeft: 'left',
  ArrowRight: 'right',
}

export type GameView = {
  render: (state: GameState) => void
  destroy: () => void
}

// Colors come from the CSS tokens in src/styles/tokens.css.
function token(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

function drawGrid(grid: number[][]): Graphics {
  const graphics = new Graphics()
  grid.forEach((cells, row) => {
    cells.forEach((_tile, col) => {
      const color = (row + col) % 2 === 0 ? token('--color-game-tile') : token('--color-game-tile-alt')
      graphics
        .rect(col * TILE, row * TILE, TILE, TILE)
        .fill(color)
        .stroke({ width: 1, color: token('--color-game-grid-line') })
    })
  })
  return graphics
}

/** Mounts the game view into `container`, drawn from `initial`. */
export function createGame(
  container: HTMLElement,
  initial: GameState,
  onMove: (direction: Direction) => void,
): GameView {
  const app = new Application()
  let player: Sprite | null = null
  let latest = initial // newest state, applied once the sprite has loaded
  let initialized = false
  let destroyed = false

  function render(state: GameState) {
    latest = state
    if (!player) return
    const [row, col] = state.player
    player.x = col * TILE + TILE / 2
    player.y = row * TILE + TILE / 2
  }

  function onKeyDown(event: KeyboardEvent) {
    const direction = KEY_TO_DIRECTION[event.key]
    if (!direction) return
    event.preventDefault() // stop arrow keys from scrolling the page
    onMove(direction)
  }

  // Pixi's init is async; wrap it in a function (top-level await breaks Vite builds).
  async function init() {
    const rows = initial.grid.length
    const cols = initial.grid[0].length
    await app.init({ width: cols * TILE, height: rows * TILE, background: token('--color-game-bg') })
    initialized = true
    if (destroyed) {
      app.destroy(true) // cleanup ran while init was pending (e.g. React StrictMode)
      return
    }
    container.appendChild(app.canvas)
    app.stage.addChild(drawGrid(initial.grid))

    const texture = await Assets.load(PLAYER_TEXTURE)
    if (destroyed) return
    player = new Sprite(texture)
    player.anchor.set(0.5)
    app.stage.addChild(player)
    render(latest)
    window.addEventListener('keydown', onKeyDown)
  }

  init()

  return {
    render,
    destroy() {
      destroyed = true
      window.removeEventListener('keydown', onKeyDown)
      if (initialized) app.destroy(true, { children: true })
    },
  }
}
