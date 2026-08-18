from __future__ import annotations

import os
from tavily import TavilyClient


def search_web(app: str, queries: list[str], max_results: int = 5) -> list[dict]:
    """Search the web and return normalized evidence candidates."""
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    results: list[dict] = []

    for query in queries:
        response = client.search(
            query=f"{app} {query}",
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
        )
        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "content": item.get("content"),
                    "query": query,
                }
            )

    return results
