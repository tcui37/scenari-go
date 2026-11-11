"""The live games, by ID. One socket is one game: main.py registers it when its socket sends the
scenario and removes it when the socket closes. The voice agent finds a call's game here."""
from game.game import Game

games: dict[str, Game] = {}


def get_game_from_id(game_id: str) -> Game:
    """The live game with this ID. Raises ValueError if there's none (bad ID, or its socket closed)."""
    if game_id not in games:
        raise ValueError(f"No game with id {game_id!r}")
    return games[game_id]
