from app.agents.validation_agent import ValidationAgent


def test_public_api_without_evidence_is_rejected():
    result = {
        "authentication": {},
        "credential_access": {},
        "api": {"availability": "public", "evidence": []},
        "mcp": {},
        "buildability": {},
        "evidence_summary": [],
    }
    findings = ValidationAgent._hard_gates(result, [])
    assert any(f.field == "api" and f.severity == "error" for f in findings)


def test_self_serve_without_evidence_is_rejected():
    result = {
        "authentication": {},
        "credential_access": {"classification": "self_serve", "evidence": []},
        "api": {},
        "mcp": {},
        "buildability": {},
        "evidence_summary": [],
    }
    findings = ValidationAgent._hard_gates(result, [])
    assert any(f.field == "credential_access" and f.severity == "error" for f in findings)


def test_ready_requires_public_api_and_self_serve_credentials():
    result = {
        "authentication": {},
        "credential_access": {"classification": "gated", "evidence": []},
        "api": {"availability": "private", "evidence": []},
        "mcp": {},
        "buildability": {"verdict": "ready"},
        "evidence_summary": [],
    }
    findings = ValidationAgent._hard_gates(result, [])
    assert any(f.field == "buildability" and f.severity == "error" for f in findings)


def test_missing_evidence_is_rejected():
    result = {
        "authentication": {},
        "credential_access": {},
        "api": {},
        "mcp": {},
        "buildability": {},
        "evidence_summary": [],
    }
    findings = ValidationAgent._hard_gates(result, [])
    assert any(f.field == "evidence" and f.severity == "error" for f in findings)


def test_unreachable_evidence_is_rejected():
    result = {
        "authentication": {"evidence": [{"url": "https://example.com/bad"}]},
        "credential_access": {},
        "api": {},
        "mcp": {},
        "buildability": {},
        "evidence_summary": [],
    }
    checks = [{"url": "https://example.com/bad", "reachable": False}]
    findings = ValidationAgent._hard_gates(result, checks)
    assert any(f.field == "evidence" and f.severity == "error" for f in findings)
