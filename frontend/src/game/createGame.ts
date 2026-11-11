// Draws the grid game with PixiJS (https://pixijs.com/8.x/guides/getting-started/quick-start).
// View only: the backend owns the game state and decides what keys do. This draws
// whatever state it is given and forwards every key press, unchanged, through `onKey`.
import { Application, Assets, Graphics, Sprite, type Texture } from 'pixi.js'
import type { Direction, GameState, Position } from './types.ts'

const TILE = 64 // px

// One 16x16 sprite per character per facing direction, in public/sprites/.
type Character = 'bert' | 'ruth' // bert is the player, ruth the agent
const DIRECTIONS: Direction[] = ['up', 'down', 'left', 'right']
const spritePath = (character: Character, facing: Direction) => `/sprites/${character}/${character}_${facing}.png`
const SPRITE_PATHS = (['bert', 'ruth'] as const).flatMap((c) => DIRECTIONS.map((d) => spritePath(c, d)))

// Keys whose browser default (scrolling the page) would get in the way of playing.
const SCROLL_KEYS = new Set(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '])

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
  onKey: (key: string) => void,
): GameView {
  const app = new Application()
  let player: Sprite | null = null
  let agent: Sprite | null = null
  let textures: Record<string, Texture> = {} // by sprite path
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
    player.texture = textures[spritePath('bert', state.player_facing)]
    agent.texture = textures[spritePath('ruth', state.agent_facing)]
  }

  function onKeyDown(event: KeyboardEvent) {
    if (SCROLL_KEYS.has(event.key)) event.preventDefault()
    onKey(event.key) // raw KeyboardEvent.key, e.g. "ArrowUp", "Enter", "Escape"
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

    textures = await Assets.load<Texture>(SPRITE_PATHS)
    if (destroyed) return
    for (const texture of Object.values(textures)) texture.source.scaleMode = 'nearest' // crisp pixel art
    player = new Sprite(textures[spritePath('bert', initial.player_facing)])
    agent = new Sprite(textures[spritePath('ruth', initial.agent_facing)])
    for (const sprite of [agent, player]) {
      sprite.anchor.set(0.5)
      sprite.width = sprite.height = TILE // scale the 16x16 art up to one tile
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
