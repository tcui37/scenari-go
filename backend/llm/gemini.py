"""Thin wrapper around the Gemini API (google-genai). Reads GEMINI_API_KEY from the environment."""
from google import genai
from google.genai import types
from pydantic import BaseModel

GEMINI_MODEL = "gemini-3.5-flash-lite"
# Fallbacks if it's unavailable (e.g. 503 "high demand"), in order. Swap one in above.
# GEMINI_MODEL = "gemini-3.1-flash-lite"  # older Flash-Lite: same cheap, fast tier
# GEMINI_MODEL = "gemini-3.5-flash"       # full Flash, same generation: more capable, costs more
# GEMINI_MODEL = "gemini-2.5-flash-lite"  # older stable generation, separate capacity
# GEMINI_MODEL = "gemini-2.5-flash"       # last resort


async def gemini_generate_with_schema(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Single-turn Gemini call; the answer is constrained to `schema`'s shape.
    Uses the async client, so awaiting it never blocks the server's event loop."""
    # Retry transient errors (503 "high demand", 429, other 5xx) with the SDK's defaults:
    # up to 5 attempts, exponential backoff from 1s. Without retry_options it never retries.
    # Keep a reference to the client: the async client below is borrowed from it.
    client = genai.Client(http_options=types.HttpOptions(retry_options=types.HttpRetryOptions()))
    async with client.aio as aio_client:
        response = await aio_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
    if response.parsed is None:
        # DEBUG: why it didn't parse, e.g. finish_reason MAX_TOKENS (cut off) or SAFETY, and the raw text
        finish_reason = response.candidates[0].finish_reason if response.candidates else None
        print(f"[gemini] {schema.__name__}: unparseable response, finish_reason={finish_reason}")
        print(f"[gemini] raw text: {response.text!r}")
        raise ValueError("Gemini response did not match the schema")
    return response.parsed
