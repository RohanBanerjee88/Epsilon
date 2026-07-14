"""Unit tests for the retrieval helpers (no network required)."""

from app.retrieval import _dedupe, _reconstruct_abstract


def test_reconstruct_abstract_orders_by_position():
    inverted = {"world": [1], "hello": [0], "again": [2]}
    assert _reconstruct_abstract(inverted) == "hello world again"


def test_reconstruct_abstract_handles_empty():
    assert _reconstruct_abstract(None) == ""
    assert _reconstruct_abstract({}) == ""


def test_dedupe_collapses_near_duplicate_titles():
    items = [
        {"title": "Deep Nets"},
        {"title": "deep  nets!"},   # same after normalization
        {"title": "Another Paper"},
    ]
    out = _dedupe(items)
    assert [i["title"] for i in out] == ["Deep Nets", "Another Paper"]


def test_dedupe_drops_untitled():
    items = [{"title": ""}, {"title": None}, {"title": "Real"}]
    out = _dedupe(items)
    assert [i["title"] for i in out] == ["Real"]
