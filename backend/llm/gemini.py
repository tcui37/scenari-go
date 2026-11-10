"""Thin wrapper around the Gemini API (google-genai). Reads GEMINI_API_KEY from the environment."""
from google import genai
from google.genai import types
from pydantic import BaseModel

GEMINI_MODEL = "gemini-3.5-flash-lite"


async def gemini_generate_with_schema(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Single-turn Gemini call; the answer is constrained to `schema`'s shape.
    Uses the async client, so awaiting it never blocks the server's event loop."""
    client = genai.Client()  # keep a reference: the async client is borrowed from it
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
        raise ValueError("Gemini response did not match the schema")
    return response.parsed
