// The Guava voice call with the conversation partner (https://docs.goguava.ai/guides/webrtc-calls).
// The call follows the game: it is placed when a conversation starts and dropped when it ends.
// The game decides when that happens; this only places or drops the call.
import * as Guava from '@guava-ai/guava-sdk/webrtc'
import type { GameCreated } from './types.ts'

export type VoiceCall = {
  follow: (inConversation: boolean) => void
  hangup: () => void
}

export function createVoiceCall(game: GameCreated, onError: (message: string) => void): VoiceCall {
  let call: Guava.Call | null = null

  function start() {
    // The shared agent finds this game by the ID we send with the call.
    const placed = new Guava.Call({ webrtcCode: game.webrtc_code, customPayload: { game_id: game.game_id } })
    call = placed
    placed.start().catch(() => {
      onError(`Call failed: ${placed.error?.message ?? 'unknown error'}. Press Esc to end the conversation.`)
    })
  }

  function hangup() {
    call?.hangup()
    call = null
  }

  return {
    follow(inConversation) {
      if (inConversation && !call) {
        start()
      } else if (!inConversation && call) {
        hangup()
        onError('')
      }
    },
    hangup,
  }
}
