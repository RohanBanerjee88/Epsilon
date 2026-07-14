"""Tiny per-user memory store.

Maritime gives each agent a persistent micro-VM, so a JSON file on local disk
survives between requests. This is what turns Research Navigator from a one-shot
API into a copilot that remembers what a user has explored before.

Deliberately minimal: no DB, no schema migrations. Just append refined topics.
"""

from __future__ import annotations

import json
import os
import pathlib
import threading
from typing import Dict, List

_DEFAULT_STORE_PATH = pathlib.Path(__file__).resolve().parents[1] / ".data" / "memory.json"
_STORE_PATH = os.environ.get("MEMORY_PATH", str(_DEFAULT_STORE_PATH))
_LOCK = threading.Lock()


def _load() -> Dict[str, List[str]]:
    try:
        with open(_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return {}


def _save(data: Dict[str, List[str]]) -> None:
    os.makedirs(os.path.dirname(_STORE_PATH) or ".", exist_ok=True)
    tmp = _STORE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _STORE_PATH)


def get_interests(user_id: str) -> List[str]:
    with _LOCK:
        return list(_load().get(user_id, []))


def add_interest(user_id: str, interest: str) -> None:
    interest = (interest or "").strip()
    if not interest:
        return
    with _LOCK:
        data = _load()
        history = data.get(user_id, [])
        if interest not in history:
            history.append(interest)
        data[user_id] = history[-20:]  # cap history length
        _save(data)
