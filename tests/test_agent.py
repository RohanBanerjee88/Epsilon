"""Tests for the agent loop, with the two external boundaries (Claude + paper
retrieval) stubbed so the orchestration runs offline and deterministically."""

import pytest

import app.agent as agent
from app.schemas import AnalyzeRequest


# ---- JSON extraction -------------------------------------------------------


def test_extract_json_plain():
    assert agent._extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_strips_code_fence():
    assert agent._extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_recovers_from_surrounding_prose():
    assert agent._extract_json('sure, here: {"b": 2} hope that helps') == {"b": 2}


# ---- full loop -------------------------------------------------------------


@pytest.fixture
def stub_boundaries(monkeypatch, tmp_path):
    """Stub Claude + retrieval, and isolate memory to a temp file."""
    monkeypatch.setattr(agent.memory, "_STORE_PATH", str(tmp_path / "mem.json"))

    async def fake_retrieve(queries, per_query=4, cap=24):
        assert queries, "planner must produce queries"
        return [
            {"title": "On-Device RAG", "url": "https://doi.org/10.1/x",
             "abstract": "a", "year": 2024, "citation_count": 42, "provider": "openalex"},
            {"title": "Tiny Retrievers", "url": "https://arxiv.org/abs/1",
             "abstract": "b", "year": 2025, "citation_count": 3, "provider": "arxiv"},
        ]

    calls = {"n": 0}

    async def fake_claude_structured(system, user, schema, **kwargs):
        calls["n"] += 1
        if calls["n"] % 2 == 1:  # planner phase
            return {
                "refined_question": "How can sub-100M retrievers run on-device for science?",
                "sub_questions": ["q1", "q2"],
                "search_queries": ["on-device retrieval", "tiny embeddings", "sci search benchmarks"],
            }
        return {  # synthesis phase
            "refined_question": "How can sub-100M retrievers run on-device for science?",
            "search_directions": ["quantized embeddings"],
            "relevant_sources": [
                {"title": "On-Device RAG", "url": "https://doi.org/10.1/x",
                 "why_it_matters": "core", "source_type": "paper"},
            ],
            "key_themes": ["efficiency"],
            "saturated_areas": ["generic RAG"],
            "underexplored_areas": ["sub-100M scientific retrievers"],
            "recommended_direction": {
                "title": "Distilled on-device scientific retriever",
                "rationale": "r", "novelty_reason": "n", "feasibility_reason": "f",
            },
            "next_steps": ["s1", "s2", "s3"],
        }

    monkeypatch.setattr(agent.retrieval, "retrieve", fake_retrieve)
    monkeypatch.setattr(agent, "_claude_structured", fake_claude_structured)
    return calls


@pytest.mark.asyncio
async def test_run_analysis_assembles_valid_brief(stub_boundaries):
    req = AnalyzeRequest(topic="lightweight retrieval on-device", context="undergrad", userId="tester")
    brief = await agent.run_analysis(req)

    assert brief.refined_question.startswith("How can sub-100M")
    assert brief.sources_considered == 2
    assert len(brief.next_steps) == 3
    assert brief.model == agent.MODEL
    # retrieval metadata is merged back onto the source Claude selected
    assert brief.relevant_sources[0].year == 2024
    assert brief.relevant_sources[0].citation_count == 42


@pytest.mark.asyncio
async def test_memory_persists_between_runs(stub_boundaries):
    await agent.run_analysis(AnalyzeRequest(topic="first topic here", userId="mem-user"))
    second = await agent.run_analysis(AnalyzeRequest(topic="second topic here", userId="mem-user"))
    assert any("sub-100M" in p for p in second.prior_interests)


@pytest.mark.asyncio
async def test_memory_write_failure_does_not_discard_brief(stub_boundaries, monkeypatch):
    def fail_to_save(_user_id, _interest):
        raise OSError("read-only filesystem")

    monkeypatch.setattr(agent.memory, "add_interest", fail_to_save)
    brief = await agent.run_analysis(
        AnalyzeRequest(topic="fault tolerant research memory", userId="mem-user")
    )
    assert brief.recommended_direction.title == "Distilled on-device scientific retriever"
