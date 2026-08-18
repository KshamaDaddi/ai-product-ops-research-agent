from __future__ import annotations

from app.agents.research_agent import ResearchAgent
from app.agents.validation_agent import ValidationAgent
from app.schemas.qc_schema import QCReport
from app.schemas.research_schema import ResearchResult


class ResearchPipeline:
    """Run research followed by an independent QC pass."""

    def __init__(self, evidence: list[dict] | None = None):
        self.research_agent = ResearchAgent(evidence=evidence)
        self.validation_agent = ValidationAgent()

    def run(self, app: str, category: str = "Unknown") -> tuple[ResearchResult, QCReport]:
        result = self.research_agent.run(app, category)
        qc = self.validation_agent.validate(result)
        return result, qc
