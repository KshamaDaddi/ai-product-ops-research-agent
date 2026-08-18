from __future__ import annotations

import json
import os
from pathlib import Path

from openai import OpenAI

from app.schemas.research_schema import ResearchResult


class ResearchAgent:
    """LLM orchestration layer for one application research task.

    Web retrieval is intentionally separated from this class so the same
    research logic can later use Tavily, another search provider, or a
    pre-collected evidence set.
    """

    def __init__(self, evidence: list[dict] | None = None):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.6")
        self.evidence = evidence or []
        prompt_path = Path(__file__).parents[1] / "prompts" / "research_prompt.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def run(self, app: str, category: str = "Unknown") -> ResearchResult:
        evidence_text = json.dumps(self.evidence, ensure_ascii=False, indent=2)
        user_prompt = f"""Research this application: {app}\nCategory: {category}\n\nAvailable web evidence:\n{evidence_text}\n\nUse only the supplied evidence for factual claims. If evidence is missing, mark the relevant field unknown."""

        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=ResearchResult,
        )
        return response.output_parsed
