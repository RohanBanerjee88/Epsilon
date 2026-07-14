"""The Research Navigator agent loop.

This is the agentic core, not a single completion:

    interpret -> plan queries  (Claude call #1)
              -> retrieve evidence from paper providers
              -> synthesize + critique + recommend  (Claude call #2)
              -> remember the topic for next time

Each Claude call returns JSON, which we parse defensively.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from anthropic import AsyncAnthropic

from . import memory, prompts, retrieval
from .schemas import AnalyzeRequest, ResearchBrief

MODEL = os.environ.get("RESEARCH_MODEL", "claude-sonnet-5")
_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        # Reads ANTHROPIC_API_KEY from the environment.
        _client = AsyncAnthropic()
    return _client


def _extract_json(text: str) -> Dict[str, Any]:
    """Pull a JSON object out of a model response, tolerating stray prose/fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fall back to the outermost {...} span.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


async def _claude_json(system: str, user: str, max_tokens: int) -> Dict[str, Any]:
    client = _get_client()
    resp = await client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    return _extract_json("".join(parts))


async def _plan(req: AnalyzeRequest, prior: List[str]) -> Dict[str, Any]:
    user = prompts.PLANNER_USER_TEMPLATE.format(
        topic=req.topic,
        context=req.context or "(none provided)",
        memory_block=prompts.memory_block(prior),
    )
    plan = await _claude_json(prompts.PLANNER_SYSTEM, user, max_tokens=1024)
    # Guard against a thin plan.
    queries = [q for q in plan.get("search_queries", []) if isinstance(q, str) and q.strip()]
    if not queries:
        queries = [req.topic]
    plan["search_queries"] = queries[:8]
    plan.setdefault("refined_question", req.topic)
    return plan


def _sources_for_prompt(sources: List[dict]) -> str:
    """Compact the retrieved sources so the synthesis prompt stays lean."""
    trimmed = []
    for s in sources:
        trimmed.append(
            {
                "title": s.get("title"),
                "url": s.get("url"),
                "year": s.get("year"),
                "citation_count": s.get("citation_count"),
                "abstract": (s.get("abstract") or "")[:500],
            }
        )
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
    return await _claude_json(prompts.SYNTHESIS_SYSTEM, user, max_tokens=2048)


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

    # Stitch retrieval metadata back onto the chosen sources.
    brief_data["relevant_sources"] = _merge_source_metadata(
        brief_data.get("relevant_sources", []), sources
    )
    brief_data.setdefault("refined_question", refined_question)
    brief_data.setdefault(
        "recommended_direction",
        {
            "title": "Insufficient evidence",
            "rationale": "Retrieval returned too little to recommend a direction confidently.",
            "novelty_reason": "",
            "feasibility_reason": "",
        },
    )
    brief_data["sources_considered"] = len(sources)
    brief_data["prior_interests"] = prior
    brief_data["model"] = MODEL

    # 4) Remember this topic for next time.
    memory.add_interest(req.user_id, refined_question)

    return ResearchBrief.model_validate(brief_data)
