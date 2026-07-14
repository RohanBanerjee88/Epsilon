# Research Navigator

Research Navigator turns a broad research interest into an evidence-backed direction worth pursuing. It sharpens the question, searches OpenAlex, arXiv, and Semantic Scholar, compares crowded and open areas, then recommends one direction with three concrete next steps.

The app now has a Next.js 16 frontend built with Tailwind CSS 4 and shadcn-style components, backed by FastAPI and Claude Sonnet 5.

## How it works

```text
user topic
  -> plan focused search queries with Claude
  -> retrieve and deduplicate papers from three providers
  -> synthesize themes, gaps, and one recommended direction with Claude
  -> persist the refined topic for the user's next session
```

The API contract is available at `POST /research/analyze`. Interactive API documentation is served at `http://localhost:8080/docs`.

## Local setup

### 1. Install the backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Put a valid Anthropic key in `.env`:

```dotenv
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Start FastAPI in the first terminal:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8080 --env-file .env
```

Check the runtime before submitting a prompt:

```bash
curl -s http://localhost:8080/health | jq
```

`ready_for_analysis` should be `true`. If it is false, the response explains whether the API key or Anthropic SDK needs attention.

### 2. Install and run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The dev script points the browser client at FastAPI on port `8080`.

## Test everything

```bash
source .venv/bin/activate
python -m pytest

cd frontend
npm run lint
npm run build
```

The backend suite is fully offline: Claude and paper providers are stubbed in agent tests. A real prompt is the final integration test because it requires your Anthropic account and external paper APIs.

Direct API test:

```bash
curl -s http://localhost:8080/research/analyze \
  -H 'content-type: application/json' \
  -d '{"topic":"robust tool-using agents","context":"I want a scoped, non-saturated semester project","userId":"demo"}' | jq
```

## Docker

The multi-stage image builds the Next.js static export, copies it into the Python image, and serves the frontend and API from one port.

```bash
docker build -t research-navigator .
docker run --rm -p 8080:8080 \
  -e ANTHROPIC_API_KEY=sk-ant-your-key-here \
  -v research-navigator-data:/data \
  research-navigator
```

Open `http://localhost:8080`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | none | Required for analysis |
| `RESEARCH_MODEL` | `claude-sonnet-5` | Anthropic model ID |
| `RESEARCH_EFFORT` | `high` | Synthesis effort level |
| `MEMORY_PATH` | `.data/memory.json` locally | Per-user research history |
| `CORS_ORIGINS` | localhost ports 3000 | Allowed Next.js development origins |
| `NEXT_PUBLIC_API_URL` | same origin | Browser API base URL |

Docker sets `MEMORY_PATH=/data/memory.json`; local runs use the writable `.data` directory automatically.

## Project layout

```text
app/
  main.py         FastAPI routes, diagnostics, error mapping, built frontend serving
  agent.py        plan -> retrieve -> synthesize -> remember loop
  retrieval.py    OpenAlex, arXiv, and Semantic Scholar clients
  memory.py       local JSON history
  prompts.py      planner and synthesis prompts
  schemas.py      request and response contracts
frontend/
  app/            Next.js app router and global theme
  components/     research workspace, results, and shadcn UI primitives
  lib/            shared types and utilities
tests/            backend API, agent, memory, and retrieval coverage
Dockerfile        multi-stage Next.js and FastAPI production image
```
