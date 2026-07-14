"""Smoke tests for the HTTP surface using FastAPI's TestClient."""

import time

from fastapi.testclient import TestClient

from app import cards
from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "ready_for_analysis" in r.json()
    assert "sdk_compatible" in r.json()


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "Epsilon" in r.text


def test_analyze_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = client.post("/research/analyze", json={"topic": "some topic here", "userId": "x"})
    assert r.status_code == 503


def test_analyze_rejects_short_topic():
    r = client.post("/research/analyze", json={"topic": "ab", "userId": "x"})
    assert r.status_code == 422  # pydantic min_length validation


def test_analyze_reports_incompatible_sdk(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.main.agent.runtime_diagnostics",
        lambda: {
            "sdk_version": "0.42.0",
            "sdk_compatible": False,
            "issue": "Anthropic SDK 0.42.0 is too old.",
        },
    )
    r = client.post("/research/analyze", json={"topic": "some topic here", "userId": "x"})
    assert r.status_code == 503
    assert "too old" in r.json()["detail"]


def test_analyze_hides_unexpected_exception_details(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.main.agent.runtime_diagnostics",
        lambda: {"sdk_version": "1.0", "sdk_compatible": True, "issue": None},
    )

    async def fail(_req):
        raise RuntimeError("secret provider internals")

    monkeypatch.setattr("app.main.agent.run_analysis", fail)
    r = client.post("/research/analyze", json={"topic": "some topic here", "userId": "x"})
    assert r.status_code == 500
    assert "secret provider internals" not in r.text


def test_research_job_completes_without_holding_request(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.main.agent.runtime_diagnostics",
        lambda: {"sdk_version": "1.0", "sdk_compatible": True, "issue": None},
    )

    async def succeed(_req):
        return {
            "refined_question": "How can compact models summarize clinical notes privately?",
            "recommended_direction": {
                "title": "Benchmark a compact private summarizer",
                "rationale": "It is measurable.",
                "novelty_reason": "Privacy and latency are evaluated together.",
                "feasibility_reason": "Public data and compact models exist.",
            },
        }

    monkeypatch.setattr("app.main.agent.run_analysis", succeed)
    created = client.post("/research/jobs", json={"topic": "compact clinical models", "userId": "x"})
    assert created.status_code == 202

    job_id = created.json()["id"]
    for _ in range(20):
        job = client.get(f"/research/jobs/{job_id}")
        if job.json()["status"] == "completed":
            break
        time.sleep(0.01)

    assert job.status_code == 200
    assert job.json()["status"] == "completed"
    assert job.json()["brief"]["recommended_direction"]["title"] == "Benchmark a compact private summarizer"


def test_brief_card_round_trip(monkeypatch, tmp_path):
    monkeypatch.setattr(cards, "_STORE_PATH", str(tmp_path / "cards.json"))
    payload = {
        "refined_question": "How can compact retrievers preserve citation quality?",
        "recommended_direction": {
            "title": "Build a citation-aware compact retriever",
            "rationale": "It turns a broad efficiency question into a measurable artifact.",
            "novelty_reason": "Citation usefulness is rarely measured under memory limits.",
            "feasibility_reason": "Public corpora and compact encoders already exist.",
        },
        "next_steps": ["Choose a corpus", "Set a memory budget", "Measure recall"],
        "underexplored_areas": ["Citation quality under fixed memory"],
        "sources_considered": 18,
    }

    created = client.post("/brief-cards", json=payload)
    assert created.status_code == 201
    card_id = created.json()["id"]

    fetched = client.get(f"/brief-cards/{card_id}")
    assert fetched.status_code == 200
    assert fetched.json()["recommended_direction"]["title"] == payload["recommended_direction"]["title"]


def test_missing_brief_card_returns_404(monkeypatch, tmp_path):
    monkeypatch.setattr(cards, "_STORE_PATH", str(tmp_path / "cards.json"))
    response = client.get("/brief-cards/not-a-real-card")
    assert response.status_code == 404
