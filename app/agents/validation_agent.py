from __future__ import annotations

import json
import os
from pathlib import Path

from openai import OpenAI

from app.schemas.qc_schema import QCReport
from app.schemas.research_schema import ResearchResult


class ValidationAgent:
    """Independent QC pass over a research result and its evidence."""

    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.6")
        prompt_path = Path(__file__).parents[1] / "prompts" / "validation_prompt.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def validate(self, result: ResearchResult) -> QCReport:
        payload = result.model_dump(mode="json")
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "research_result": payload,
                            "instruction": "Review this result strictly against the evidence embedded in it.",
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                },
            ],
            text_format=QCReport,
        )
        return response.output_parsed
