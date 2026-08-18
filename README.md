# AI Product Ops Research Agent

An evidence-first research agent for evaluating whether applications are realistically buildable as integrations or agent-enabled products.

## Pipeline

`Application -> Web Evidence -> Research Agent -> Structured JSON`

The system separates API availability from credential access and distinguishes official MCP support from community implementations.

## Setup

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

Set `OPENAI_API_KEY` and `TAVILY_API_KEY` in `.env`.

## Run

```bash
python run.py --app "Slack" --category "Communication"
```

The command searches for developer/API/authentication evidence, then asks the structured research agent to classify the application.

## Output

The result follows the Pydantic `ResearchResult` schema in `app/schemas/research_schema.py` and includes authentication, credential access, API, MCP, buildability, evidence, confidence, and limitations.

## Next stages

- Add a dedicated evidence validation/QC agent.
- Add official-source prioritization and URL validation.
- Add batch processing for the full application list.
- Add tests and reproducibility checks.
- Add a Streamlit demo UI.
