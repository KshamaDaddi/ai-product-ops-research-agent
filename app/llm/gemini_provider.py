from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel


class GeminiProvider:
    """Gemini adapter using JSON output with a Developer-API-safe schema."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to .env")
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    @staticmethod
    def _sanitize_schema(schema: type[BaseModel]) -> dict[str, Any]:
        """Remove JSON-Schema constructs rejected by Gemini Developer API."""
        raw = schema.model_json_schema()

        def clean(node: Any) -> Any:
            if isinstance(node, dict):
                out = {}
                for key, value in node.items():
                    if key == "additionalProperties":
                        continue
                    if key == "$schema":
                        continue
                    out[key] = clean(value)
                return out
            if isinstance(node, list):
                return [clean(x) for x in node]
            return node

        return clean(raw)

    def parse(self, system_prompt: str, user_prompt: str, schema: type[BaseModel]) -> BaseModel:
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=self._sanitize_schema(schema),
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return schema.model_validate_json(response.text)
