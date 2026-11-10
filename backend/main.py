import asyncio
import os
import threading
from collections.abc import Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from game.game import Game
from game.scenario import Scenario
from llm.gemini import gemini_generate
from llm.prompts import checklists_prompt, score_prompt
from schemas import GeneratedChecklistsModel, ScenarioModel, ScoreRequestModel, ScoreResponseModel
from voice.agent import create_agent

load_dotenv()  # loads GEMINI_API_KEY, GUAVA_API_KEY and GUAVA_WEBRTC_CODE from backend/.env

# --- Games: each game is isolated by its ID; it lives in memory while its socket is connected ---
games: dict[str, Game] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup, one voice agent starts answering calls for every game."""
    agent = create_agent(games.get)
    # listen_webrtc blocks for as long as it listens, so it gets its own thread.
    threading.Thread(target=agent.listen_webrtc, args=(os.environ["GUAVA_WEBRTC_CODE"],), daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan)

def ask_gemini(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Call Gemini; any failure becomes a 502 for the frontend."""
    try:
        return gemini_generate(prompt, schema)
    except Exception:
        raise HTTPException(502, "Gemini request failed. Please try again.")


# Plain `def` (not async): FastAPI runs these in a thread pool, so the blocking
# Gemini call doesn't stall other requests.
# TODO: why?
@app.post("/api/checklists")
def generate_checklists(scenario: ScenarioModel) -> ScenarioModel:
    """Returns the scenario with one generated checklist per objective."""
    result = ask_gemini(checklists_prompt(Scenario.from_model(scenario)), GeneratedChecklistsModel)
    if len(result.checklists) != len(scenario.objectives):
        # Debug: show what Gemini returned in the `fastapi dev` terminal.
        print("Scenario sent:")
        print(scenario.model_dump_json(indent=2))
        print(f"Expected {len(scenario.objectives)} checklists, got {len(result.checklists)}:")
        print(result.model_dump_json(indent=2))
        raise HTTPException(502, "Gemini skipped an objective. Please try again.")
    scenario.checklists = result.checklists
    return scenario


@app.post("/api/score")
def score_scenario(req: ScoreRequestModel) -> ScoreResponseModel:
    return ask_gemini(score_prompt(Scenario.from_model(req.scenario), req.transcript), ScoreResponseModel)


@app.post("/api/games")
def create_game(scenario: ScenarioModel) -> dict:
    game_id = uuid4().hex
    games[game_id] = Game.from_scenario(Scenario.from_model(scenario))
    # The browser places the voice call, so it needs the code the agent listens on.
    return {"game_id": game_id, "state": games[game_id].state(), "webrtc_code": os.environ["GUAVA_WEBRTC_CODE"]}


def socket_updater(websocket: WebSocket, game: Game) -> Callable[[], None]:
    """Returns a function that sends `game`'s state to its browser. Safe to call from any thread:
    the voice agent calls it from its own, so the send is handed to the socket's event loop."""
    loop = asyncio.get_running_loop()

    def update_socket() -> None:
        asyncio.run_coroutine_threadsafe(websocket.send_json({"type": "state", **game.state()}), loop)

    return update_socket


@app.websocket("/ws/games/{game_id}")
async def play_game(websocket: WebSocket, game_id: str):
    """The browser sends raw key names (e.g. "ArrowUp", "Enter"); the game decides what they do."""
    await websocket.accept()
    game = games.get(game_id)
    if game is None:
        # Accept first, then close: browsers can only read close codes, not a refused handshake.
        await websocket.close(code=4404, reason="Unknown game")
        return

    game.update_socket = socket_updater(websocket, game)
    try:
        game.update_socket()
        while True:
            game.handle_key(await websocket.receive_text())
            game.update_socket()
    except WebSocketDisconnect:
        pass  # the browser left: "Finish scenario", Back, closing the tab, or a dropped connection
    finally:
        games.pop(game_id, None)  # a game lasts for one connection; it's gone once the socket closes