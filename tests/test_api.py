"""Smoke tests for the HTTP surface using FastAPI's TestClient."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "Research Navigator" in r.text


def test_analyze_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = client.post("/research/analyze", json={"topic": "some topic here", "userId": "x"})
    assert r.status_code == 503


def test_analyze_rejects_short_topic():
    r = client.post("/research/analyze", json={"topic": "ab", "userId": "x"})
    assert r.status_code == 422  # pydantic min_length validation
