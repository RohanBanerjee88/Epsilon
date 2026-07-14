"""Pydantic models: the request body and the stable response contract.

The response schema mirrors the contract in CLAUDE.md exactly so the frontend
(and any future iOS client) can rely on a fixed shape.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ---- Request ---------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    topic: str = Field(
        ..., min_length=3, max_length=2000, description="Natural-language research interest."
    )
    context: str = Field(
        "", max_length=4000, description="Optional background, field, constraints, or goal."
    )
    user_id: str = Field(
        "anonymous", min_length=1, max_length=128, alias="userId",
        description="Stable per-user id for memory.",
    )

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
    search_directions: List[str] = Field(default_factory=list)
    relevant_sources: List[Source] = Field(default_factory=list)
    key_themes: List[str] = Field(default_factory=list)
    saturated_areas: List[str] = Field(default_factory=list)
    underexplored_areas: List[str] = Field(default_factory=list)
    recommended_direction: RecommendedDirection
    next_steps: List[str] = Field(default_factory=list)

    # Metadata about how the brief was produced (nice for the demo / debugging).
    sources_considered: int = 0
    prior_interests: List[str] = Field(default_factory=list)
    model: str = ""
