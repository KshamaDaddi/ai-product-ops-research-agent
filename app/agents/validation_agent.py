from __future__ import annotations

import json
from pathlib import Path

from app.llm.gemini_provider import GeminiProvider
from app.schemas.qc_schema import QCReport, QCFinding


class ValidationAgent:
    """Independent deterministic + Gemini QC pass."""

    def __init__(self):
        self.client = GeminiProvider()
        prompt_path = Path(__file__).parents[1] / "prompts" / "validation_prompt.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    @staticmethod
    def _hard_gates(result: dict, checks: list[dict]) -> list[QCFinding]:
        findings: list[QCFinding] = []
        by_url = {c["url"]: c for c in checks}
        evidence = []
        for section in ("authentication", "credential_access", "api", "mcp"):
            evidence.extend(result.get(section, {}).get("evidence", []))
        evidence.extend(result.get("evidence_summary", []))
        if not evidence:
            findings.append(QCFinding(severity="error", field="evidence", issue="No evidence records were supplied.", recommendation="Collect evidence for material conclusions."))
        for item in evidence:
            url = str(item.get("url", ""))
            check = by_url.get(url)
            if check and not check["reachable"]:
                findings.append(QCFinding(severity="error", field="evidence", issue=f"Evidence URL is unreachable: {url}", recommendation="Replace it or mark the claim unknown."))
        api = result.get("api", {})
        creds = result.get("credential_access", {})
        build = result.get("buildability", {})
        mcp = result.get("mcp", {})
        mcp_urls = {str(e.get("url")) for e in mcp.get("evidence", [])}
        if api.get("availability") == "public" and not api.get("evidence"):
            findings.append(QCFinding(severity="error", field="api", issue="Public API classification has no API evidence.", recommendation="Attach API documentation or change the classification."))
        if creds.get("classification") == "self_serve" and not creds.get("evidence"):
            findings.append(QCFinding(severity="error", field="credential_access", issue="Self-serve credential classification has no credential evidence.", recommendation="Provide credential-registration evidence or use unknown/gated."))
        if mcp.get("status") == "official" and not any(c.get("official") for u, c in by_url.items() if u in mcp_urls):
            findings.append(QCFinding(severity="error", field="mcp", issue="Official MCP classification lacks validated first-party evidence.", recommendation="Use first-party MCP evidence or classify as community/unknown."))
        if build.get("verdict") == "ready" and (api.get("availability") != "public" or creds.get("classification") != "self_serve"):
            findings.append(QCFinding(severity="error", field="buildability", issue="Ready verdict is inconsistent with public API and self-serve credentials.", recommendation="Use constrained/unknown unless practical developer access is established."))
        return findings

    def validate(self, research_result: dict, source_checks: list[dict]) -> QCReport:
        hard_findings = self._hard_gates(research_result, source_checks)
        payload = {"research_result": research_result, "source_checks": source_checks, "deterministic_findings": [f.model_dump() for f in hard_findings]}
        qc = self.client.parse(self.system_prompt, json.dumps(payload, ensure_ascii=False, indent=2), QCReport)
        if hard_findings:
            qc.findings = hard_findings + qc.findings
            qc.passed = False
            qc.score = min(qc.score, max(0, 100 - 15 * len(hard_findings)))
            qc.corrected_result = None
        return qc
