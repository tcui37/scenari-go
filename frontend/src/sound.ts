// Short sound effects, played with the browser's Audio. Files live in public/sounds/.
const SOUNDS = {
  step: '/sounds/step.ogg', // the player moved one tile
  click: '/sounds/click.ogg', // any button
  enter: '/sounds/enter_scenarigo.ogg', // the home page's "Get started"
}
export type SoundName = keyof typeof SOUNDS

// Preloaded once; each play uses a copy, so quick repeats (fast steps) overlap.
const loaded = Object.fromEntries(
  Object.entries(SOUNDS).map(([name, src]) => [name, new Audio(src)]),
) as Record<SoundName, HTMLAudioElement>

export function playSound(name: SoundName) {
  const sound = loaded[name].cloneNode() as HTMLAudioElement
  sound.volume = 0.5
  sound.play().catch(() => {}) // a blocked or missing sound must never break the game
}
