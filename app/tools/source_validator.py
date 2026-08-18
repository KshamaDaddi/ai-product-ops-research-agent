from __future__ import annotations

from urllib.parse import urlparse

import requests


OFFICIAL_HINTS = {
    "developer", "developers", "docs", "api", "platform", "support", "help"
}


def _domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def _is_official_domain(app: str, domain: str) -> bool:
    tokens = [token.lower() for token in app.replace("-", " ").split() if token]
    return bool(tokens) and any(token in domain for token in tokens)


def validate_source(app: str, url: str, timeout: int = 10) -> dict:
    """Perform deterministic source-level checks without trusting the LLM.

    Reachability is a technical check, not proof that the page supports a claim.
    Official-domain detection is heuristic and is surfaced as such.
    """
    domain = _domain(url)
    notes: list[str] = []
    reachable = False

    try:
        response = requests.head(url, allow_redirects=True, timeout=timeout)
        if response.status_code >= 400 or response.status_code == 405:
            response = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
        reachable = response.status_code < 400
        final_domain = _domain(response.url)
        if final_domain and final_domain != domain:
            notes.append(f"redirected_to:{final_domain}")
            domain = final_domain
    except requests.RequestException as exc:
        notes.append(f"request_error:{type(exc).__name__}")

    official = _is_official_domain(app, domain)
    path_tokens = set(urlparse(url).path.lower().replace("/", " ").replace("-", " ").split())

    if official:
        quality = "primary"
    elif path_tokens & OFFICIAL_HINTS:
        quality = "secondary"
    else:
        quality = "weak"

    if not official:
        notes.append("official-domain detection is heuristic")

    return {
        "url": url,
        "reachable": reachable,
        "official": official,
        "source_quality": quality,
        "domain": domain,
        "notes": notes,
    }


def validate_evidence(app: str, evidence: list[dict]) -> list[dict]:
    checks = []
    seen: set[str] = set()
    for item in evidence:
        url = str(item.get("url", "")).strip()
        if not url or url in seen:
            continue
        seen.add(url)
        checks.append(validate_source(app, url))
    return checks
