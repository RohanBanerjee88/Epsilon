"""Pydantic models: the request body and the stable response contract.

The response schema mirrors the contract in CLAUDE.md exactly so the frontend
(and any future iOS client) can rely on a fixed shape.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ---- Request ---------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Natural-language research interest.")
    context: str = Field("", description="Optional background, field, constraints, or goal.")
    user_id: str = Field("anonymous", alias="userId", description="Stable per-user id for memory.")

    model_config = {"populate_by_name": True}


# ---- Response contract -----------------------------------------------------


class Source(BaseModel):
    title: str
    url: str
    why_it_matters: str = ""
    source_type: Literal["paper", "web", "other"] = "paper"
    year: Optional[int] = None
    citation_count: Optional[int] = None


class RecommendedDirection(BaseModel):
    title: str
    rationale: str
    novelty_reason: str
    feasibility_reason: str


class ResearchBrief(BaseModel):
    refined_question: str
    search_directions: List[str] = []
    relevant_sources: List[Source] = []
    key_themes: List[str] = []
    saturated_areas: List[str] = []
    underexplored_areas: List[str] = []
    recommended_direction: RecommendedDirection
    next_steps: List[str] = []

    # Metadata about how the brief was produced (nice for the demo / debugging).
    sources_considered: int = 0
    prior_interests: List[str] = []
    model: str = ""
