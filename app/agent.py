"""The Research Navigator agent loop.

This is the agentic core, not a single completion:

    interpret -> plan queries  (Claude, structured output)
              -> retrieve evidence from paper providers
              -> synthesize + critique + recommend  (Claude, structured output)
              -> remember the topic for next time

Both Claude calls use the Messages API's structured outputs
(`output_config.format` with a JSON schema), so the model is *constrained* to
return schema-valid JSON. That eliminates the fragile "parse whatever the model
wrote" step that used to fail on stray formatting.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from anthropic import AsyncAnthropic

from . import memory, prompts, retrieval
from .schemas import AnalyzeRequest, ResearchBrief

# Latest Sonnet, high effort by default (both overridable via env).
MODEL = os.environ.get("RESEARCH_MODEL", "claude-sonnet-5")
EFFORT = os.environ.get("RESEARCH_EFFORT", "high")  # low | medium | high | xhigh | max

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        # Reads ANTHROPIC_API_KEY from the environment.
        _client = AsyncAnthropic()
    return _client


# ---- Structured-output schemas ---------------------------------------------
# Structured outputs require additionalProperties:false on every object and an
# explicit `required` list; no min/max or length constraints are allowed.

PLAN_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["refined_question", "sub_questions", "search_queries"],
    "properties": {
        "refined_question": {"type": "string"},
        "sub_questions": {"type": "array", "items": {"type": "string"}},
        "search_queries": {"type": "array", "items": {"type": "string"}},
    },
}

_SOURCE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "url", "why_it_matters", "source_type"],
    "properties": {
        "title": {"type": "string"},
        "url": {"type": "string"},
        "why_it_matters": {"type": "string"},
        "source_type": {"type": "string", "enum": ["paper", "web", "other"]},
    },
}

SYNTHESIS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "refined_question",
        "search_directions",
        "relevant_sources",
        "key_themes",
        "saturated_areas",
        "underexplored_areas",
        "recommended_direction",
        "next_steps",
    ],
    "properties": {
        "refined_question": {"type": "string"},
        "search_directions": {"type": "array", "items": {"type": "string"}},
        "relevant_sources": {"type": "array", "items": _SOURCE_SCHEMA},
        "key_themes": {"type": "array", "items": {"type": "string"}},
        "saturated_areas": {"type": "array", "items": {"type": "string"}},
        "underexplored_areas": {"type": "array", "items": {"type": "string"}},
        "recommended_direction": {
            "type": "object",
            "additionalProperties": False,
            "required": ["title", "rationale", "novelty_reason", "feasibility_reason"],
            "properties": {
                "title": {"type": "string"},
                "rationale": {"type": "string"},
                "novelty_reason": {"type": "string"},
                "feasibility_reason": {"type": "string"},
            },
        },
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
}


def _extract_json(text: str) -> Dict[str, Any]:
    """Structured outputs return clean JSON, but stay defensive about fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


async def _claude_structured(
    system: str,
    user: str,
    schema: Dict[str, Any],
    *,
    max_tokens: int,
    thinking: Dict[str, Any],
    effort: str | None = None,
) -> Dict[str, Any]:
    """One Claude call constrained to `schema` via structured outputs."""
    client = _get_client()
    output_config: Dict[str, Any] = {"format": {"type": "json_schema", "schema": schema}}
    if effort:
        output_config["effort"] = effort

    resp = await client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config=output_config,
        thinking=thinking,
    )

    if resp.stop_reason == "refusal":
        raise RuntimeError("The model declined to answer this request.")
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("The response was cut off (max_tokens). Try a narrower topic.")

    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    if not text.strip():
        raise RuntimeError("The model returned an empty response.")
    return _extract_json(text)


async def _plan(req: AnalyzeRequest, prior: List[str]) -> Dict[str, Any]:
    user = prompts.PLANNER_USER_TEMPLATE.format(
        topic=req.topic,
        context=req.context or "(none provided)",
        memory_block=prompts.memory_block(prior),
    )
    # Planning is cheap and deterministic — no need to burn thinking tokens.
    plan = await _claude_structured(
        prompts.PLANNER_SYSTEM, user, PLAN_SCHEMA,
        max_tokens=2048, thinking={"type": "disabled"},
    )
    queries = [q for q in plan.get("search_queries", []) if isinstance(q, str) and q.strip()]
    if not queries:
        queries = [req.topic]
    plan["search_queries"] = queries[:8]
    plan.setdefault("refined_question", req.topic)
    return plan


def _sources_for_prompt(sources: List[dict]) -> str:
    trimmed = [
        {
            "title": s.get("title"),
            "url": s.get("url"),
            "year": s.get("year"),
            "citation_count": s.get("citation_count"),
            "abstract": (s.get("abstract") or "")[:500],
        }
        for s in sources
    ]
    return json.dumps(trimmed, ensure_ascii=False)


async def _synthesize(
    req: AnalyzeRequest, refined_question: str, sources: List[dict], prior: List[str]
) -> Dict[str, Any]:
    user = prompts.SYNTHESIS_USER_TEMPLATE.format(
        topic=req.topic,
        context=req.context or "(none provided)",
        memory_block=prompts.memory_block(prior),
        refined_question=refined_question,
        retrieved_sources_json=_sources_for_prompt(sources),
    )
    # This is where judgment matters — give it adaptive thinking + real effort.
    return await _claude_structured(
        prompts.SYNTHESIS_SYSTEM, user, SYNTHESIS_SCHEMA,
        max_tokens=12000, thinking={"type": "adaptive"}, effort=EFFORT,
    )


def _merge_source_metadata(brief_sources: List[dict], retrieved: List[dict]) -> List[dict]:
    """Attach year/citation_count from retrieval onto the sources Claude picked."""
    by_url = {s.get("url"): s for s in retrieved}
    by_title = {(s.get("title") or "").lower(): s for s in retrieved}
    out = []
    for s in brief_sources or []:
        match = by_url.get(s.get("url")) or by_title.get((s.get("title") or "").lower())
        if match:
            s.setdefault("year", match.get("year"))
            s.setdefault("citation_count", match.get("citation_count"))
        out.append(s)
    return out


async def run_analysis(req: AnalyzeRequest) -> ResearchBrief:
    prior = memory.get_interests(req.user_id)

    # 1) Plan: sharpen the question and design focused queries.
    plan = await _plan(req, prior)
    refined_question = plan["refined_question"]

    # 2) Act: retrieve evidence across providers.
    sources = await retrieval.retrieve(plan["search_queries"])

    # 3) Synthesize: cluster, critique, recommend.
    brief_data = await _synthesize(req, refined_question, sources, prior)

    brief_data["relevant_sources"] = _merge_source_metadata(
        brief_data.get("relevant_sources", []), sources
    )
    brief_data.setdefault("refined_question", refined_question)
    brief_data["sources_considered"] = len(sources)
    brief_data["prior_interests"] = prior
    brief_data["model"] = MODEL

    # 4) Remember this topic for next time.
    memory.add_interest(req.user_id, refined_question)

    return ResearchBrief.model_validate(brief_data)
