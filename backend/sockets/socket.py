"""Sending JSON messages to a browser over its WebSocket."""
import asyncio
from collections.abc import Callable

from fastapi import WebSocket


def create_socket_updater(websocket: WebSocket) -> Callable[[dict], None]:
    """Returns a function that sends a message (a JSON dict) to the browser. Safe to call from any thread:
    the voice agent calls it from its own, so the send is handed to the socket's event loop."""
    loop = asyncio.get_running_loop()

    def update_socket(message: dict) -> None:
        asyncio.run_coroutine_threadsafe(websocket.send_json(message), loop)

    return update_socket
