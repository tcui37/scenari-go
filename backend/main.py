import os
import threading
from contextlib import asynccontextmanager
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from game.game import Game
from game.scenario import Scenario
from llm.gemini import gemini_generate_with_schema
from llm.prompts import checklists_prompt, score_prompt
from schemas import GameSummaryModel, GeneratedChecklistsModel, ScenarioModel, ScoreResponseModel, TranscriptLineModel
from sockets.socket import create_socket_updater
from voice.agent import create_agent

load_dotenv()  # loads GEMINI_API_KEY, GUAVA_API_KEY and GUAVA_WEBRTC_CODE from backend/.env

GUAVA_WEBRTC_CODE = os.environ["GUAVA_WEBRTC_CODE"]  # the one code the shared voice agent listens on

# Games with an open socket, by ID. One socket is one game: it is registered when its socket
# sends the scenario and removed when the socket closes. The voice agent finds a call's game here.
games: dict[str, Game] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup, one voice agent starts answering calls for every game."""
    agent = create_agent(games.get)
    # setup listener on a separate thread, as listener blocks and handles incoming calls until the process exits
    threading.Thread(target=agent.listen_webrtc, args=(GUAVA_WEBRTC_CODE,), daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

async def ask_gemini(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Call Gemini; any failure becomes a 502 for the frontend."""
    try:
        return await gemini_generate_with_schema(prompt, schema)
    except Exception:
        raise HTTPException(502, "Gemini request failed. Please try again.")


# The Gemini routes are `async def` and await the async Gemini client, so the event loop
# serves other requests and game sockets while Gemini answers.
@app.post("/api/checklists")
async def generate_checklists(scenario: ScenarioModel) -> ScenarioModel:
    """Returns the scenario with one generated checklist per objective."""
    result = await ask_gemini(checklists_prompt(Scenario.from_model(scenario)), GeneratedChecklistsModel)

    if len(result.checklists) != len(scenario.objectives):
        raise HTTPException(502, "Gemini skipped an objective. Please try again.")
    scenario.checklists = result.checklists
    return scenario


@app.post("/api/games/{game_id}/summary")
async def summarize_game(game_id: str) -> GameSummaryModel:
    """Scores the game's conversation so far with Gemini, and returns it with the transcript."""
    game = games.get(game_id)
    if game is None:
        raise HTTPException(404, "This game has ended. Play again to get a summary.")
    transcript = game.call_summary.transcript
    score = await ask_gemini(score_prompt(game.scenario, transcript), ScoreResponseModel)
    return GameSummaryModel(evaluation=score, transcript=[TranscriptLineModel.from_line(line) for line in transcript])


@app.websocket("/ws/game")
async def play_game(websocket: WebSocket):
    """One socket is one game. The first message is the scenario (JSON); after that the browser
    sends raw key names (e.g. "ArrowUp", "Enter") and the game decides what they do."""
    await websocket.accept()
    game_id = uuid4().hex
    try:
        # No game exists until the scenario arrives, so a socket that closes early costs nothing.
        scenario = ScenarioModel.model_validate_json(await websocket.receive_text())
        game = games[game_id] = Game.from_scenario(Scenario.from_model(scenario))
        game.set_socket_emission_fn(create_socket_updater(websocket, game))
        # The browser places the voice call: it dials the agent's code and names this game.
        await websocket.send_json({"type": "game_created", "game_id": game_id, "webrtc_code": GUAVA_WEBRTC_CODE})
        game.update_socket()
        while True:
            game.handle_key(await websocket.receive_text())
            game.update_socket()

    except WebSocketDisconnect:
        pass  # the browser left: "Finish scenario", Back, closing the tab, or a dropped connection
    finally:
        games.pop(game_id, None)  # the game ends with its socket
