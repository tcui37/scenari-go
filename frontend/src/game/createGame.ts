// Draws the grid game with PixiJS (https://pixijs.com/8.x/guides/getting-started/quick-start).
// View only: the backend owns the game state. This draws whatever state it is given
// and reports key presses through `onInput`.
import { Application, Assets, Graphics, Sprite } from 'pixi.js'
import type { GameInput, GameState, Position } from './types.ts'

const TILE = 64 // px
const PLAYER_TEXTURE = 'https://pixijs.com/assets/bunny.png' // sample sprite from the PixiJS docs

const KEY_TO_INPUT: Record<string, GameInput> = {
  ArrowUp: { type: 'move', direction: 'up' },
  ArrowDown: { type: 'move', direction: 'down' },
  ArrowLeft: { type: 'move', direction: 'left' },
  ArrowRight: { type: 'move', direction: 'right' },
  Enter: { type: 'enter' },
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
  onInput: (input: GameInput) => void,
): GameView {
  const app = new Application()
  let player: Sprite | null = null
  let agent: Sprite | null = null
  let latest = initial // newest state, applied once the sprites have loaded
  let initialized = false
  let destroyed = false

  function place(sprite: Sprite, [row, col]: Position) {
    sprite.x = col * TILE + TILE / 2
    sprite.y = row * TILE + TILE / 2
  }

  function render(state: GameState) {
    latest = state
    if (!player || !agent) return
    place(player, state.player_position)
    place(agent, state.agent_position)
  }

  function onKeyDown(event: KeyboardEvent) {
    const input = KEY_TO_INPUT[event.key]
    if (!input) return
    event.preventDefault() // stop arrow keys from scrolling the page
    onInput(input)
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
    agent = new Sprite(texture)
    agent.tint = token('--color-game-agent') // same sample sprite, tinted to tell them apart
    for (const sprite of [agent, player]) {
      sprite.anchor.set(0.5)
      app.stage.addChild(sprite)
    }
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
