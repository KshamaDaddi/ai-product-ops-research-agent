from __future__ import annotations

import json
from pathlib import Path

from app.llm.gemini_provider import GeminiProvider
from app.schemas.research_schema import ResearchResult


class ResearchAgent:
    """Evidence-first research orchestration using Gemini."""

    def __init__(self, evidence: list[dict] | None = None):
        self.client = GeminiProvider()
        self.evidence = evidence or []
        prompt_path = Path(__file__).parents[1] / "prompts" / "research_prompt.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def run(self, app: str, category: str = "Unknown") -> ResearchResult:
        evidence_text = json.dumps(self.evidence, ensure_ascii=False, indent=2)
        user_prompt = f"""Research this application: {app}\nCategory: {category}\n\nAvailable web evidence:\n{evidence_text}\n\nUse only the supplied evidence for factual claims. If evidence is missing, mark the relevant field unknown."""
        return self.client.parse(self.system_prompt, user_prompt, ResearchResult)
