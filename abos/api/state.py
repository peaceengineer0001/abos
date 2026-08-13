"""
abos.api.state
=============

Process-wide shared state for the API: a single :class:`TenantStore` plus
helpers to (re)load the demo dataset from ``demo_state.json`` when present so the
demo web app always has data to render.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from ..tenant import TenantStore

# Where seed_demo.py writes the demo dataset.
DEMO_STATE_PATH = os.environ.get(
    "ABOS_DEMO_STATE",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                 "demo_state.json"),
)

_store: Optional[TenantStore] = None


def get_store() -> TenantStore:
    global _store
    if _store is None:
        _store = TenantStore()
        _try_autoseed()
    return _store


def reset_store() -> TenantStore:
    global _store
    _store = TenantStore()
    return _store


def _try_autoseed() -> None:
    """If a demo_state.json exists, rebuild live runtimes from it so the API is
    populated on boot. Falls back silently if the file is absent."""
    if not os.path.exists(DEMO_STATE_PATH):
        return
    try:
        from ..demo import rehydrate_from_state
        with open(DEMO_STATE_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        rehydrate_from_state(_store, data)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[abos.api.state] autoseed skipped: {exc}")
