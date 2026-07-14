"""Smoke tests for the HTTP surface using FastAPI's TestClient."""

from fastapi.testclient import TestClient

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
    assert "Research Navigator" in r.text


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
