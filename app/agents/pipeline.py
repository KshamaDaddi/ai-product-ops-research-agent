from __future__ import annotations

from app.agents.research_agent import ResearchAgent
from app.agents.validation_agent import ValidationAgent
from app.schemas.qc_schema import QCReport
from app.tools.source_validator import validate_evidence


class ResearchPipeline:
    """Run research, deterministic source checks, then independent QC."""

    def __init__(self, evidence: list[dict] | None = None):
        self.evidence = evidence or []
        self.research_agent = ResearchAgent(evidence=self.evidence)
        self.validation_agent = ValidationAgent()

    def run(self, app: str, category: str = "Unknown") -> tuple[dict, QCReport]:
        result = self.research_agent.run(app, category)
        result_dict = result.model_dump(mode="json")
        source_checks = validate_evidence(app, self.evidence)
        qc = self.validation_agent.validate(result_dict, source_checks)
        if qc.corrected_result is not None and qc.passed:
            result_dict = qc.corrected_result
        return result_dict, qc
