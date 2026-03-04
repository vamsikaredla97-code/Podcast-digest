"""
State management — tracks which feed items have already been processed
to prevent duplicate WhatsApp messages.

State is stored in a local JSON file: .digest_state.json
"""
import json
import os
from pathlib import Path

STATE_FILE = Path(__file__).parent / ".digest_state.json"


def _load() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"seen": []}


def _save(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_seen(item_id: str) -> bool:
    """Return True if this item has already been processed."""
    state = _load()
    return item_id in state["seen"]


def mark_seen(item_id: str) -> None:
    """Mark an item as processed so it won't be sent again."""
    state = _load()
    if item_id not in state["seen"]:
        state["seen"].append(item_id)
        _save(state)


def reset() -> None:
    """Clear all state (use for testing)."""
    _save({"seen": []})
