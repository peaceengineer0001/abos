"""Tenant CRUD, workspace feed, scorecard, and council-run routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..models import CreateTenantRequest, CreateUserRequest, RunCouncilRequest
from ..state import get_store

router = APIRouter(tags=["tenants"])


@router.post("/api/tenants")
def create_tenant(req: CreateTenantRequest):
    store = get_store()
    try:
        rt = store.create_tenant(req.name, req.business_type, tenant_id=req.tenant_id)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "data": rt.to_dict()}


@router.get("/api/tenants")
def list_tenants():
    return {"ok": True, "data": get_store().list()}


@router.get("/api/tenants/{tenant_id}")
def get_tenant(tenant_id: str):
    rt = get_store().get(tenant_id)
    if rt is None:
        raise HTTPException(status_code=404, detail=f"unknown tenant '{tenant_id}'")
    return {"ok": True, "data": rt.to_dict()}


@router.post("/api/tenants/{tenant_id}/users")
def add_user(tenant_id: str, req: CreateUserRequest):
    rt = get_store().get(tenant_id)
    if rt is None:
        raise HTTPException(status_code=404, detail=f"unknown tenant '{tenant_id}'")
    user = rt.add_user(req.name, req.role)
    return {"ok": True, "data": user.to_dict()}


@router.get("/api/tenants/{tenant_id}/workspace")
def get_workspace(tenant_id: str, channel: str | None = Query(default=None),
                  limit: int = Query(default=100, le=500)):
    rt = get_store().get(tenant_id)
    if rt is None:
        raise HTTPException(status_code=404, detail=f"unknown tenant '{tenant_id}'")
    return {"ok": True, "data": rt.workspace(channel, limit)}


@router.get("/api/scorecard/{tenant_id}")
def get_scorecard(tenant_id: str):
    rt = get_store().get(tenant_id)
    if rt is None:
        raise HTTPException(status_code=404, detail=f"unknown tenant '{tenant_id}'")
    card = (rt.last_analysis or {}).get("scorecard") or rt.scorecard().to_dict()
    return {"ok": True, "data": card}


@router.post("/api/tenants/{tenant_id}/run-council")
def run_council(tenant_id: str, req: RunCouncilRequest):
    rt = get_store().get(tenant_id)
    if rt is None:
        raise HTTPException(status_code=404, detail=f"unknown tenant '{tenant_id}'")
    synthesis = rt.run_council(req.context)
    return {"ok": True, "data": synthesis}
