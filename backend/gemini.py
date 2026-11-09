"""Thin wrapper around the Gemini API (google-genai). Reads GEMINI_API_KEY from the environment."""
from google import genai
from google.genai import types
from pydantic import BaseModel

GEMINI_MODEL = "gemini-3.5-flash-lite"


def gemini_generate[T: BaseModel](prompt: str, schema: type[T]) -> T:
    """Single-turn Gemini call; the answer is constrained to `schema`'s shape."""
    client = genai.Client()
    response = client.models.generate_content(
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
