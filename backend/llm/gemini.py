"""Thin wrapper around the Gemini API (google-genai). Reads GEMINI_API_KEY from the environment."""
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

# Tried in order: if one fails (e.g. 503 "high demand"), the next one answers.
GEMINI_MODELS = [
    "gemini-3.5-flash-lite",  # first choice
    "gemini-3.1-flash-lite",  # older Flash-Lite: same cheap, fast tier
    "gemini-3.5-flash",       # full Flash, same generation: more capable, costs more
    "gemini-2.5-flash-lite",  # older stable generation, separate capacity
    "gemini-2.5-flash",       # last resort
]


async def gemini_generate_with_schema(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Single-turn Gemini call; the answer is constrained to `schema`'s shape.
    Tries each of GEMINI_MODELS in order and returns the first answer that parses.
    Uses the async client, so awaiting it never blocks the server's event loop."""
    # Each model retries transient errors (503 "high demand", 429, other 5xx) with the SDK's defaults:
    # up to 5 attempts, exponential backoff from 1s. Only then do we move on to the next model.
    # Keep a reference to the client: the async client below is borrowed from it.
    client = genai.Client(http_options=types.HttpOptions(retry_options=types.HttpRetryOptions()))
    async with client.aio as aio_client:
        for model in GEMINI_MODELS:
            try:
                response = await aio_client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                    ),
                )
            except errors.APIError as e:
                print(f"[gemini] {model} failed: {e.code} {e.message}, trying the next model")
                continue

            if response.parsed is None:
                # DEBUG: why it didn't parse, e.g. finish_reason MAX_TOKENS (cut off) or SAFETY, and the raw text
                finish_reason = response.candidates[0].finish_reason if response.candidates else None
                print(f"[gemini] {model} {schema.__name__}: unparseable response, finish_reason={finish_reason}")
                print(f"[gemini] raw text: {response.text!r}")
                continue

            return response.parsed

    raise RuntimeError("Every Gemini model failed")
