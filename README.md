# Research Navigator

An agent that turns a vague research interest into a **scoped direction worth
pursuing** — a sharper question, real papers, what's crowded vs. open, and a
concrete recommendation with next steps. Built to be deployed as a persistent
agent on [Maritime](https://maritime.sh).

It is not a paper-search box and not a summarizer. It **plans, retrieves, and
critiques**, and it **remembers** what you've explored before.

---

## What makes it agentic

The backend runs a real loop, not a single completion:

```
interpret intent
   └─► PLAN     (Claude)  sharpen the question, generate 5–8 focused queries
        └─► ACT  (retrieval)  search OpenAlex + arXiv + Semantic Scholar, dedupe
             └─► SYNTHESIZE (Claude)  cluster themes, flag saturated vs. open areas,
                                       recommend one direction + 3 next steps
                  └─► REMEMBER  persist the topic so later sessions build on it
```

Per-user memory is a JSON file on the agent's persistent disk — exactly the
kind of stateful behavior Maritime's per-agent micro-VMs are built for.

## Output contract

`POST /research/analyze` returns stable JSON:

```json
{
  "refined_question": "...",
  "search_directions": ["..."],
  "relevant_sources": [
    { "title": "...", "url": "...", "why_it_matters": "...", "source_type": "paper" }
  ],
  "key_themes": ["..."],
  "saturated_areas": ["..."],
  "underexplored_areas": ["..."],
  "recommended_direction": {
    "title": "...", "rationale": "...", "novelty_reason": "...", "feasibility_reason": "..."
  },
  "next_steps": ["...", "...", "..."]
}
```

The same container also serves a single-page web UI at `/`, so the whole thing
is **one URL** to open, demo, and record.

## Project layout

```
app/
  main.py        FastAPI: /research/analyze, /health, and the web UI at /
  agent.py       the plan → retrieve → synthesize → remember loop
  retrieval.py   keyless async search across OpenAlex / arXiv / Semantic Scholar
  prompts.py     planner + Research Navigator synthesis prompts
  memory.py      per-user interest history on persistent disk
  schemas.py     request + response models
  static/
    index.html   self-contained web frontend
Dockerfile       custom container Maritime can build directly
requirements.txt
.env.example
```

---

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # your key
uvicorn app.main:app --reload --port 8080
```

Open http://localhost:8080 and try:

> *"lightweight retrieval methods for on-device scientific search"*
> context: *"undergrad, limited compute, want a scoped semester project"*

Or hit the API directly:

```bash
curl -s localhost:8080/research/analyze \
  -H 'content-type: application/json' \
  -d '{"topic":"robust tool-using agents","context":"want a non-saturated angle","userId":"demo"}' | jq
```

### Docker

```bash
docker build -t research-navigator .
docker run -p 8080:8080 -e ANTHROPIC_API_KEY=sk-ant-... research-navigator
```

---

## Deploy on Maritime

This repo ships a `Dockerfile`, so Maritime can build and host it as a custom
container. The exact CLI verbs are in the Maritime docs
(<https://maritime.sh/docs>); the flow is:

1. **Install the CLI and log in.**
   ```bash
   # from the Maritime docs quickstart
   maritime login
   ```
2. **Set the API key as a secret** (never bake it into the image):
   ```bash
   maritime secrets set ANTHROPIC_API_KEY=sk-ant-...
   ```
   (Or add it in the dashboard under the agent's environment variables.)
3. **Deploy from the repo root** — Maritime detects the `Dockerfile`, builds an
   isolated micro-VM, and returns a live URL:
   ```bash
   maritime deploy
   ```
4. **Verify:**
   ```bash
   curl https://<your-agent>.maritime.sh/health
   ```
   Then open the same URL in a browser for the web UI.

The container listens on `$PORT` (default `8080`) and writes memory to
`/data`, which persists on the agent's disk between requests.

> Billing: apply code **`INTERNSHIP`** for $50 in credits before deploying.

---

## Demo script (≤ 60s)

1. Open the Maritime URL — show the live agent in the browser.
2. Type a vague interest in plain English; hit **Explore**.
3. Point at the **refined question**, the **real papers**, and the
   **saturated vs. underexplored** split.
4. Land on the **recommended direction + 3 next steps**: *"this is what's worth
   working on, and why."*
5. Flash the Maritime dashboard to show it's hosted there.
