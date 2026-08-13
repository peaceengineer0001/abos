"""Demo seeding, templates, and health routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...demo import SCENARIOS, seed_store
from ...templates import BUSINESS_TYPES, list_templates
from ..state import get_store, reset_store

router = APIRouter(tags=["demo"])


@router.get("/api/health")
def health():
    store = get_store()
    return {"ok": True, "data": {"status": "healthy", "service": "abos-api",
                                 "tenants": len(store.tenants)}}


@router.get("/api/templates")
def templates():
    return {"ok": True, "data": list_templates()}


@router.post("/api/demo/seed")
def seed_all():
    """Seed all six business scenarios into the live store."""
    store = get_store()
    seed_store(store)
    return {"ok": True, "data": store.list()}


@router.post("/api/demo/reset")
def reset():
    """Reset the store and reseed all six scenarios."""
    store = reset_store()
    seed_store(store)
    return {"ok": True, "data": store.list()}


@router.post("/api/demo/seed/{business_type}")
def seed_one(business_type: str):
    """Seed the demo tenant for a single business type."""
    if business_type not in BUSINESS_TYPES:
        raise HTTPException(status_code=400,
                            detail=f"unknown business_type '{business_type}'")
    store = get_store()
    scn = next((s for s in SCENARIOS if s["business_type"] == business_type), None)
    if scn is None:
        raise HTTPException(status_code=404, detail="no scenario for business type")
    if store.get(scn["tenant_id"]) is None:
        from ...demo import _seed_tenant
        _seed_tenant(store, scn)
    return {"ok": True, "data": store.require(scn["tenant_id"]).to_dict()}
