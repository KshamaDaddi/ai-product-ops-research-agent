from __future__ import annotations

from urllib.parse import urlparse
import requests

OFFICIAL_PATH_HINTS = {"developer", "developers", "docs", "api", "platform", "support", "help", "reference"}

def domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")

def registrable_domain(host: str) -> str:
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host

def _app_tokens(app: str) -> set[str]:
    return {x.lower() for x in app.replace("-", " ").replace("_", " ").split() if len(x) > 2}

def _name_matches_domain(app: str, host: str) -> bool:
    rd = registrable_domain(host)
    return any(token in rd.split(".")[0] for token in _app_tokens(app))

def validate_source(app: str, url: str, official_domains: set[str] | None = None, timeout: int = 10) -> dict:
    """Check reachability and authority signals; reachability never proves a claim."""
    original_domain = domain(url)
    final_domain = original_domain
    notes: list[str] = []
    reachable = False
    try:
        response = requests.get(url, allow_redirects=True, timeout=timeout, stream=True, headers={"User-Agent": "AI-Product-Ops-Research-Agent/1.0"})
        reachable = response.status_code < 400
        final_domain = domain(response.url) or original_domain
        if final_domain != original_domain:
            notes.append(f"redirected_to:{final_domain}")
        response.close()
    except requests.RequestException as exc:
        notes.append(f"request_error:{type(exc).__name__}")

    known_official = {registrable_domain(d) for d in (official_domains or set()) if d}
    final_rd = registrable_domain(final_domain)
    official = final_rd in known_official if known_official else _name_matches_domain(app, final_domain)
    path_parts = {p for p in urlparse(url).path.lower().replace("/", " ").replace("-", " ").split() if p}
    has_doc_signal = bool(path_parts & OFFICIAL_PATH_HINTS)

    if official and has_doc_signal:
        quality = "primary"
    elif official:
        quality = "secondary"
        notes.append("official domain but page is not clearly developer/documentation content")
    elif has_doc_signal:
        quality = "secondary"
        notes.append("documentation-like path on an unverified domain")
    else:
        quality = "weak"
    if not official:
        notes.append("official domain not independently established")
    return {"url": url, "reachable": reachable, "official": official, "source_quality": quality, "domain": final_domain, "notes": notes}

def validate_evidence(app: str, evidence: list[dict], official_domains: set[str] | None = None) -> list[dict]:
    checks: list[dict] = []
    seen: set[str] = set()
    for item in evidence:
        url = str(item.get("url", "")).strip()
        if not url or url in seen:
            continue
        seen.add(url)
        checks.append(validate_source(app, url, official_domains=official_domains))
    return checks
