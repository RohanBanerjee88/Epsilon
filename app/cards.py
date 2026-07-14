"""Persistent, unguessable quick-note cards shared from completed briefs."""

from __future__ import annotations

import json
import os
import pathlib
import secrets
import threading
from datetime import datetime, timezone
from typing import Dict

from .schemas import BriefCard, BriefCardCreate

_DEFAULT_STORE_PATH = pathlib.Path(__file__).resolve().parents[1] / ".data" / "cards.json"
_STORE_PATH = os.environ.get("CARD_STORE_PATH", str(_DEFAULT_STORE_PATH))
_LOCK = threading.Lock()
_MAX_CARDS = 250


def _load() -> Dict[str, dict]:
    try:
        with open(_STORE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return {}


def _save(data: Dict[str, dict]) -> None:
    os.makedirs(os.path.dirname(_STORE_PATH) or ".", exist_ok=True)
    temporary_path = _STORE_PATH + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    os.replace(temporary_path, _STORE_PATH)


def create(payload: BriefCardCreate) -> BriefCard:
    card = BriefCard(
        id=secrets.token_urlsafe(9),
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    with _LOCK:
        cards = _load()
        cards[card.id] = card.model_dump(mode="json")
        cards = dict(list(cards.items())[-_MAX_CARDS:])
        _save(cards)
    return card


def get(card_id: str) -> BriefCard | None:
    with _LOCK:
        data = _load().get(card_id)
    return BriefCard.model_validate(data) if data else None
