from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel

from gemini import gemini_generate
from prompts import score_prompt, scripts_prompt
from schemas import Scenario, ScoreRequest, ScoreResponse, ScriptsResponse

load_dotenv()  # loads GEMINI_API_KEY from backend/.env

app = FastAPI()


def ask_gemini[T: BaseModel](prompt: str, schema: type[T]) -> T:
    """Call Gemini; any failure becomes a 502 for the frontend."""
    try:
        return gemini_generate(prompt, schema)
    except Exception:
        raise HTTPException(502, "Gemini request failed. Please try again.")


# Plain `def` (not async): FastAPI runs these in a thread pool, so the blocking
# Gemini call doesn't stall other requests.
@app.post("/api/scripts")
def generate_scripts(scenario: Scenario) -> ScriptsResponse:
    result = ask_gemini(scripts_prompt(scenario), ScriptsResponse)
    if len(result.scripts) != len(scenario.objectives):
        raise HTTPException(502, "Gemini skipped an objective. Please try again.")
    # Gemini may reword objectives; restore the teacher's exact text.
    for script, objective in zip(result.scripts, scenario.objectives):
        script.objective = objective
    return result


@app.post("/api/score")
def score_scenario(req: ScoreRequest) -> ScoreResponse:
    return ask_gemini(score_prompt(req), ScoreResponse)


# Placeholder for the future backend game engine.
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
