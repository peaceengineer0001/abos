"""
abos.api.main
============

The ABOS FastAPI backend. Run with::

    uvicorn abos.api.main:app --reload

On startup it autoseeds from ``demo_state.json`` if present (see
``abos.api.state``), so the demo web app has data immediately. CORS is open so
the Next.js demo panel (deployed separately on Abacus.AI) can call it.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import __version__
from .routes import tenants, agents, evidence, decisions, demo

app = FastAPI(
    title="ABOS — Agentic Business Operating System API",
    version=__version__,
    description=(
        "Evidence in, governed action out. Multi-tenant BOSS council of 11 "
        "Nostr-native agents across four streams (govern / run / grow / decide) "
        "with a deterministic, auditable policy engine and human approval queue."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(demo.router)
app.include_router(tenants.router)
app.include_router(agents.router)
app.include_router(evidence.router)
app.include_router(decisions.router)


@app.get("/")
def root():
    return {
        "service": "abos-api",
        "version": __version__,
        "tagline": "Evidence in. Governed action out.",
        "docs": "/docs",
        "endpoints": [
            "GET  /api/health",
            "GET  /api/templates",
            "POST /api/tenants",
            "GET  /api/tenants",
            "GET  /api/tenants/{id}",
            "GET  /api/tenants/{id}/workspace",
            "POST /api/tenants/{id}/run-council",
            "GET  /api/agents?tenant_id=",
            "POST /api/evidence",
            "POST /api/decisions/dispatch",
            "GET  /api/decisions?tenant_id=&status=pending",
            "POST /api/decisions/{id}/approve",
            "POST /api/decisions/{id}/deny",
            "GET  /api/scorecard/{tenant_id}",
            "GET  /api/audit/{tenant_id}",
            "POST /api/demo/seed",
            "POST /api/demo/seed/{business_type}",
        ],
    }


@app.on_event("startup")
def _startup() -> None:
    # Touch the store so autoseed runs at boot.
    from .state import get_store
    get_store()
