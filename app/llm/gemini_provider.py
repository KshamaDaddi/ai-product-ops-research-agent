from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel


class GeminiProvider:
    """Gemini adapter using Chat.send_message for structured JSON output."""

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
                    if key in {"additionalProperties", "$schema"}:
                        continue
                    out[key] = clean(value)
                return out
            if isinstance(node, list):
                return [clean(x) for x in node]
            return node

        return clean(raw)

    def parse(self, system_prompt: str, user_prompt: str, schema: type[BaseModel]) -> BaseModel:
        chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=self._sanitize_schema(schema),
            ),
        )
        response = chat.send_message(user_prompt)
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return schema.model_validate_json(response.text)
