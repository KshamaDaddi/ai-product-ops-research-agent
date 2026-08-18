from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

QCSeverity = Literal["error", "warning", "info"]


class QCFinding(BaseModel):
    severity: QCSeverity
    field: str
    issue: str
    recommendation: str


class QCReport(BaseModel):
    passed: bool
    score: int = Field(ge=0, le=100)
    findings: list[QCFinding] = Field(default_factory=list)
    corrected_result: dict | None = None
