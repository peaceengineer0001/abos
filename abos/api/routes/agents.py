"""Agent roster routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ...agents import STREAMS
from ..state import get_store

router = APIRouter(tags=["agents"])


@router.get("/api/agents")
def list_agents(tenant_id: str | None = Query(default=None)):
    """List agents. With ``tenant_id``, returns that tenant's live council
    (with Nostr identities + status); without it, returns the static registry."""
    store = get_store()
    if tenant_id:
        rt = store.get(tenant_id)
        if rt is None:
            raise HTTPException(status_code=404, detail=f"unknown tenant '{tenant_id}'")
        return {"ok": True, "data": {"streams": STREAMS, "agents": rt.council.roster()}}
    # Static roster (no tenant): pick any existing tenant or describe classes.
    from ...agents import AGENT_CLASSES
    roster = [{"name": c.NAME, "title": c.TITLE, "stream": c.STREAM,
               "channel": c.CHANNEL, "persona": c.PERSONA,
               "proposable_actions": c.PROPOSABLE_ACTIONS} for c in AGENT_CLASSES]
    return {"ok": True, "data": {"streams": STREAMS, "agents": roster}}
