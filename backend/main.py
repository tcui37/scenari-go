from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from game.game import DIRECTIONS, Game
from llm.gemini import gemini_generate
from llm.prompts import checklists_prompt, score_prompt
from schemas import GeneratedChecklists, Scenario, ScoreRequest, ScoreResponse

load_dotenv()  # loads GEMINI_API_KEY from backend/.env

app = FastAPI()

def ask_gemini(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Call Gemini; any failure becomes a 502 for the frontend."""
    try:
        return gemini_generate(prompt, schema)
    except Exception:
        raise HTTPException(502, "Gemini request failed. Please try again.")


# Plain `def` (not async): FastAPI runs these in a thread pool, so the blocking
# Gemini call doesn't stall other requests.
@app.post("/api/checklists")
def generate_checklists(scenario: Scenario) -> Scenario:
    """Returns the scenario with one generated checklist per objective."""
    result = ask_gemini(checklists_prompt(scenario), GeneratedChecklists)
    if len(result.checklists) != len(scenario.objectives):
        raise HTTPException(502, "Gemini skipped an objective. Please try again.")
    scenario.checklists = result.checklists
    return scenario


@app.post("/api/score")
def score_scenario(req: ScoreRequest) -> ScoreResponse:
    return ask_gemini(score_prompt(req), ScoreResponse)


# --- Game: each game is isolated by its ID; state lives in memory until the server restarts ---

games: dict[str, Game] = {}


@app.post("/api/games")
def create_game() -> dict:
    game_id = uuid4().hex
    games[game_id] = Game()
    return {"game_id": game_id, "state": games[game_id].state()}


@app.websocket("/ws/games/{game_id}")
async def play_game(websocket: WebSocket, game_id: str):
    await websocket.accept()
    game = games.get(game_id)
    if game is None:
        # Accept first, then close: browsers can only read close codes, not a refused handshake.
        await websocket.close(code=4404, reason="Unknown game")
        return

    await websocket.send_json({"type": "state", **game.state()})
    try:
        while True:
            message = await websocket.receive_json()  # {"type": "move", "direction": "up"}
            if message.get("type") == "move" and message.get("direction") in DIRECTIONS:
                game.move(message["direction"])
                await websocket.send_json({"type": "state", **game.state()})
            else:
                await websocket.send_json({"type": "error", "message": "Expected a move: up, down, left or right."})
    except WebSocketDisconnect:
        pass  # the game stays in memory, so reconnecting with the same ID resumes it
