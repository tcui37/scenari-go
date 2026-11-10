from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from game.game import Game
from llm.gemini import gemini_generate
from llm.prompts import checklists_prompt, score_prompt
from schemas import GeneratedChecklists, Scenario, ScoreRequest, ScoreResponse

load_dotenv()  # loads GEMINI_API_KEY from backend/.env

# --- Games: each game is isolated by its ID; it lives in memory while its socket is connected ---
games: dict[str, Game] = {}


app = FastAPI()

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
def generate_checklists(scenario: Scenario) -> Scenario:
    """Returns the scenario with one generated checklist per objective."""
    result = ask_gemini(checklists_prompt(scenario), GeneratedChecklists)
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
def score_scenario(req: ScoreRequest) -> ScoreResponse:
    return ask_gemini(score_prompt(req), ScoreResponse)


@app.post("/api/games")
def create_game(scenario: Scenario) -> dict:
    game_id = uuid4().hex
    games[game_id] = Game.from_scenario(scenario)
    return {"game_id": game_id, "state": games[game_id].state()}


@app.websocket("/ws/games/{game_id}")
async def play_game(websocket: WebSocket, game_id: str):
    """The browser sends raw key names (e.g. "ArrowUp", "Enter"); the game decides what they do."""
    await websocket.accept()
    game = games.get(game_id)
    if game is None:
        # Accept first, then close: browsers can only read close codes, not a refused handshake.
        await websocket.close(code=4404, reason="Unknown game")
        return

    try:
        await websocket.send_json({"type": "state", **game.state()})
        while True:
            key = await websocket.receive_text()
            game.handle_key(key)
            await websocket.send_json({"type": "state", **game.state()})
    except WebSocketDisconnect:
        pass  # the browser left: "Finish scenario", Back, closing the tab, or a dropped connection
    finally:
        games.pop(game_id, None)  # a game lasts for one connection; it's gone once the socket closes