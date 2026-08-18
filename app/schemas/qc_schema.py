from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

QCSeverity = Literal["error", "warning", "info"]
SourceQuality = Literal["primary", "secondary", "weak", "unknown"]

class SourceCheck(BaseModel):
    url: str
    reachable: bool
    official: bool
    source_quality: SourceQuality
    domain: str
    notes: list[str] = Field(default_factory=list)

class QCFinding(BaseModel):
    severity: QCSeverity
    field: str
    issue: str
    recommendation: str

class QCReport(BaseModel):
    passed: bool
    score: int = Field(ge=0, le=100)
    source_checks: list[SourceCheck] = Field(default_factory=list)
    findings: list[QCFinding] = Field(default_factory=list)
    confidence_adjustments: dict[str, str] = Field(default_factory=dict)
    corrected_result: dict | None = None
