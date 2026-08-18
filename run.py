from __future__ import annotations

import argparse
import json
import os

from dotenv import load_dotenv

from app.agents.research_agent import ResearchAgent
from app.tools.web_search import search_web


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="AI Product Ops Research Agent")
    parser.add_argument("--app", required=True, help="Application to research")
    parser.add_argument("--category", default="Unknown", help="Application category")
    args = parser.parse_args()

    queries = [
        "official developer API documentation authentication",
        "developer credentials API key OAuth access requirements",
        "API endpoints SDK webhooks integrations",
        "official MCP server Model Context Protocol",
    ]
    evidence = search_web(args.app, queries)
    result = ResearchAgent(evidence=evidence).run(args.app, args.category)
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
