"""FastAPI entrypoint for the Epsilon API and built web client."""

from __future__ import annotations

import logging
import os
import pathlib

from anthropic import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import agent, cards
from .schemas import AnalyzeRequest, BriefCard, BriefCardCreate, ResearchBrief

logger = logging.getLogger(__name__)

app = FastAPI(title="Epsilon", version="2.1.0")

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend" / "out"

cors_origins = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health():
    diagnostics = agent.runtime_diagnostics()
    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return {
        "status": "ok",
        "ready_for_analysis": has_api_key and diagnostics["sdk_compatible"],
        "has_api_key": has_api_key,
        "model": agent.MODEL,
        **diagnostics,
    }


@app.post("/research/analyze", response_model=ResearchBrief)
async def analyze(req: AnalyzeRequest):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured.")

    diagnostics = agent.runtime_diagnostics()
    if not diagnostics["sdk_compatible"]:
        raise HTTPException(status_code=503, detail=diagnostics["issue"])

    try:
        return await agent.run_analysis(req)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=503,
            detail="The Anthropic API key was rejected. Check ANTHROPIC_API_KEY.",
        ) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"The configured Anthropic account cannot access {agent.MODEL}.",
        ) from exc
    except RateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="Anthropic is rate limiting requests. Wait a moment and try again.",
        ) from exc
    except (APIConnectionError, APITimeoutError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The research model could not be reached. Try again shortly.",
        ) from exc
    except APIStatusError as exc:
        logger.exception("Anthropic returned status %s", exc.status_code)
        raise HTTPException(
            status_code=502,
            detail="The research model rejected the request. Check the backend logs.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected analysis failure")
        raise HTTPException(
            status_code=500,
            detail="The analysis could not be completed. Check the backend logs.",
        ) from exc


@app.post("/brief-cards", response_model=BriefCard, status_code=201)
async def create_brief_card(payload: BriefCardCreate):
    try:
        return cards.create(payload)
    except OSError as exc:
        logger.exception("Could not persist brief card")
        raise HTTPException(
            status_code=500,
            detail="The phone card could not be created. Try again.",
        ) from exc


@app.get("/brief-cards/{card_id}", response_model=BriefCard)
async def get_brief_card(card_id: str):
    card = cards.get(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="This brief card is unavailable.")
    return card


if FRONTEND_DIR.exists():
    # The Docker build creates a static Next.js export here. API routes above
    # remain available while every other path is handled by the web client.
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    async def api_root():
        return JSONResponse(
            {
                "name": "Epsilon API",
                "docs": "/docs",
                "frontend": "Run `npm run dev` from the frontend directory.",
            }
        )
