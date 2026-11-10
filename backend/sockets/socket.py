"""Sending a game's state to its browser over the game's WebSocket."""
import asyncio
from collections.abc import Callable

from fastapi import WebSocket

from game.game import Game


def create_socket_updater(websocket: WebSocket, game: Game) -> Callable[[], None]:
    """Returns a function that sends `game`'s state to its browser. Safe to call from any thread:
    the voice agent calls it from its own, so the send is handed to the socket's event loop."""
    loop = asyncio.get_running_loop()

    def update_socket() -> None:
        asyncio.run_coroutine_threadsafe(websocket.send_json({"type": "state", **game.state()}), loop)

    return update_socket
