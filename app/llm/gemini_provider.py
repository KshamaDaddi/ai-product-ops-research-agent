from __future__ import annotations

import os

from google import genai
from google.genai import types
from pydantic import BaseModel


class GeminiProvider:
    """Gemini adapter using native structured JSON output and Pydantic validation."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to .env")
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    def parse(self, system_prompt: str, user_prompt: str, schema: type[BaseModel]) -> BaseModel:
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return schema.model_validate_json(response.text)
