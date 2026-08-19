# AI Product Ops Research Agent

An evidence-first research and validation agent for evaluating whether applications are realistically buildable as integrations or agent-enabled products.

## What it does

Given an application and category, the system:

1. Searches the web for developer/API/authentication/MCP evidence using Tavily.
2. Uses Gemini to convert the evidence into a structured research result.
3. Independently validates source reachability and evidence consistency.
4. Runs deterministic QC hard gates for material contradictions and unsupported classifications.
5. Uses a dedicated Gemini Validation/QC Agent for a second-pass review.
6. Returns a machine-readable research result plus a QC report.

## Architecture

```text
Application + Category
        |
        v
   Tavily Web Search
        |
        v
    Evidence Set
        |
        v
   Gemini Research Agent
        |
        v
 Structured ResearchResult
        |
        +--------------------+
        |                    |
        v                    v
 Source Validation     Deterministic QC Gates
        |                    |
        +---------+----------+
                  |
                  v
          Gemini Validation/QC
                  |
                  v
       Validated JSON + QC Report
```

The QC layer is intentionally independent of the research generation step. It can reject a result when evidence is missing, unreachable, or inconsistent with claims such as public API, self-serve credentials, official MCP, or ready buildability.

## Research dimensions

The structured result evaluates:

- Authentication methods
- Credential access model
- API availability, types, and breadth
- MCP status
- Buildability verdict and blockers
- Evidence URLs and excerpts
- Confidence and limitations

## QC behavior

The validation layer combines deterministic hard gates with a dedicated Gemini review. Examples of hard gates include:

- Public API claims must have API evidence.
- Self-serve credential claims must have credential evidence.
- Official MCP claims require validated first-party evidence.
- A `ready` buildability verdict must be consistent with public API access and self-serve credentials.
- Unreachable evidence URLs are flagged.

## Setup

Requirements: Python 3.10+.

```bash
python -m venv .venv

# Windows PowerShell
.venv\\Scripts\\Activate.ps1

# Windows Command Prompt
.venv\\Scripts\\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

Set these variables in `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Never commit `.env` or API keys to GitHub.

## Run

```bash
python run.py --app "Notion" --category "Productivity"
```

The CLI accepts any application and category; the pipeline is not hardcoded to Notion.

Examples:

```bash
python run.py --app "Slack" --category "Communication"
python run.py --app "GitHub" --category "Developer Tools"
python run.py --app "Figma" --category "Design"
```

## Output

The command prints JSON containing two top-level objects:

```text
research_result
quality_control
```

`research_result` follows the Pydantic `ResearchResult` schema. `quality_control` contains the QC pass/fail decision, score, source checks, findings, confidence adjustments, and optional corrected result.

## Example result

A successful Notion run produced a QC score of 92/100 and passed validation. The QC report also recorded an informational recommendation to maintain high MCP confidence while seeking more granular primary developer documentation.

## Limitations

- The current CLI processes one application/category per execution.
- Search quality depends on the available web-search evidence.
- The system does not claim that a product is buildable merely because an API exists; credential access, evidence quality, MCP status, and consistency checks also matter.
- A passing QC score is not a guarantee of factual completeness; it is a structured validation signal based on the collected evidence.

## Project structure

```text
app/
├── agents/
│   ├── research_agent.py
│   ├── validation_agent.py
│   └── pipeline.py
├── llm/
│   └── gemini_provider.py
├── prompts/
├── schemas/
├── tools/
└── utils/
run.py
requirements.txt
.env.example
```

## Security

`.env` is local-only and should never be committed. Use `.env.example` as the safe template for required configuration.
