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
    confidence_adjustments: list[str] = Field(default_factory=list)
    # A free-form object becomes additionalProperties in JSON Schema, which
    # Gemini Developer API rejects. Keep this as JSON text instead.
    corrected_result: str | None = None
