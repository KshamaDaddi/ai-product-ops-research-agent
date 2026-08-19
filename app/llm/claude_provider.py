from __future__ import annotations

import json
import os
from typing import TypeVar

import anthropic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ClaudeProvider:
    """Claude adapter with JSON-only output and local Pydantic validation."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to .env")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.max_tokens = int(os.getenv("CLAUDE_MAX_TOKENS", "12000"))

    def parse(self, system_prompt: str, user_prompt: str, schema: type[T]) -> T:
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        system = (
            system_prompt
            + "\n\nReturn ONLY valid JSON. Do not use Markdown fences. "
            + "The JSON must conform to this schema:\n"
            + schema_json
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=0,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", None) == "text").strip()
        if text.startswith("```"):
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Claude returned non-JSON output: {text[:500]}") from exc
        return schema.model_validate(payload)
