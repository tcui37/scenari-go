// Draws the grid game with PixiJS (https://pixijs.com/8.x/guides/getting-started/quick-start).
// View only: the backend owns the state; this draws it and forwards raw key presses via `onKey`.
import { Application, Assets, Graphics, Sprite, type Texture } from 'pixi.js'
import { playSound } from '../sound.ts'
import type { Direction, GameState, Position } from './types.ts'

const TILE = 64 // px per grid cell

// 16x16 art per character and facing, e.g. public/sprites/bert/bert_up.png.
type Character = 'bert' | 'ruth' // player, agent
const DIRECTIONS: Direction[] = ['up', 'down', 'left', 'right']
const spritePath = (character: Character, facing: Direction) => `/sprites/${character}/${character}_${facing}.png`
const SPRITE_PATHS = (['bert', 'ruth'] as const).flatMap((c) => DIRECTIONS.map((d) => spritePath(c, d)))

// Keys whose default (page scroll) would get in the way.
const SCROLL_KEYS = new Set(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '])

export type GameView = {
  render: (state: GameState) => void
  destroy: () => void
}

/** Mounts the game view into `container`, sized to `initial`'s grid. */
export function createGame(
  container: HTMLElement,
  initial: GameState,
  onKey: (key: string) => void,
): GameView {
  const app = new Application()

  function onKeyDown(event: KeyboardEvent) {
    if (SCROLL_KEYS.has(event.key)) event.preventDefault()
    onKey(event.key) // e.g. "ArrowUp", "Enter", "Escape"
  }

  // The only async work. render/destroy wait on `ready`; .then callbacks run in call order,
  // so renders stay ordered and an early destroy runs once setup finishes.
  async function setup() {
    const rows = initial.grid.length
    const cols = initial.grid[0].length
    await app.init({ width: cols * TILE, height: rows * TILE, background: token('--color-game-bg') })
    container.appendChild(app.canvas)
    app.stage.addChild(drawGrid(initial.grid)) // static: drawn once

    const textures = await Assets.load<Texture>(SPRITE_PATHS) // cached; texture() reads them back
    for (const loaded of Object.values(textures)) loaded.source.scaleMode = 'nearest' // no blur on pixel art
    const sprites = {
      agent: addSprite(app, texture('ruth', initial.agent_facing)),
      player: addSprite(app, texture('bert', initial.player_facing)), // added last: drawn on top
    }
    window.addEventListener('keydown', onKeyDown)
    return sprites
  }
  const ready = setup()

  function render(state: GameState) {
    playSound('step')
    ready.then(({ player, agent }) => {
      place(player, state.player_position, texture('bert', state.player_facing))
      place(agent, state.agent_position, texture('ruth', state.agent_facing))
    })
  }

  function destroy() {
    ready.then(() => {
      window.removeEventListener('keydown', onKeyDown) // on window, so Pixi won't remove it
      app.destroy(true, { children: true }) // canvas + sprites; textures stay cached
    })
  }

  return { render, destroy }
}

// --- Helpers ---

// Reads a color from src/styles/tokens.css.
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

// Valid only after setup's Assets.load.
function texture(character: Character, facing: Direction): Texture {
  return Assets.get<Texture>(spritePath(character, facing))
}

function addSprite(app: Application, texture: Texture): Sprite {
  const sprite = new Sprite(texture)
  sprite.anchor.set(0.5) // position = centre
  sprite.width = sprite.height = TILE // kept across texture swaps
  app.stage.addChild(sprite)
  return sprite
}

// Centres `sprite` in cell [row, col], showing `texture`.
function place(sprite: Sprite, [row, col]: Position, texture: Texture) {
  sprite.texture = texture
  sprite.position.set(col * TILE + TILE / 2, row * TILE + TILE / 2)
}
