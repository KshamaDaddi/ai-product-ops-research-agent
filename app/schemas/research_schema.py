from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, HttpUrl

Confidence = Literal["high", "medium", "low", "unknown"]


class Evidence(BaseModel):
    claim: str
    url: HttpUrl
    source_type: str
    excerpt: str | None = None


class Authentication(BaseModel):
    methods: list[str] = Field(default_factory=list)
    confidence: Confidence = "unknown"
    evidence: list[Evidence] = Field(default_factory=list)


class CredentialAccess(BaseModel):
    classification: Literal["self_serve", "gated", "partner_only", "unknown"] = "unknown"
    details: str | None = None
    confidence: Confidence = "unknown"
    evidence: list[Evidence] = Field(default_factory=list)


class APIResearch(BaseModel):
    availability: Literal["public", "private", "none", "unknown"] = "unknown"
    types: list[str] = Field(default_factory=list)
    breadth: Literal["broad", "moderate", "narrow", "unknown"] = "unknown"
    details: str | None = None
    confidence: Confidence = "unknown"
    evidence: list[Evidence] = Field(default_factory=list)


class MCPResearch(BaseModel):
    status: Literal["official", "community", "none_found", "unknown"] = "unknown"
    details: str | None = None
    confidence: Confidence = "unknown"
    evidence: list[Evidence] = Field(default_factory=list)


class Buildability(BaseModel):
    verdict: Literal["ready", "constrained", "blocked", "unknown"] = "unknown"
    main_blocker: str | None = None
    reasoning: str
    confidence: Confidence = "unknown"


class ResearchResult(BaseModel):
    app: str
    category: str
    description: str
    authentication: Authentication
    credential_access: CredentialAccess
    api: APIResearch
    mcp: MCPResearch
    buildability: Buildability
    evidence_summary: list[Evidence] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
