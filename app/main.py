"""FastAPI entrypoint for Research Navigator.

Serves both the JSON agent API and the single-page web UI from one container,
so the whole thing is a single Maritime URL.
"""

from __future__ import annotations

import os
import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .agent import run_analysis
from .schemas import AnalyzeRequest, ResearchBrief

app = FastAPI(title="Research Navigator", version="1.0.0")

STATIC_DIR = pathlib.Path(__file__).parent / "static"


@app.get("/health")
async def health():
    return {"status": "ok", "has_api_key": bool(os.environ.get("ANTHROPIC_API_KEY"))}


@app.post("/research/analyze", response_model=ResearchBrief)
async def analyze(req: AnalyzeRequest):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured.")
    try:
        return await run_analysis(req)
    except Exception as exc:  # surface a clean error to the UI
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


# Serve any other static assets (kept minimal; index.html is self-contained).
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
