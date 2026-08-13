"""Evidence submission routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...core.evidence import Evidence
from ..models import SubmitEvidenceRequest
from ..state import get_store

router = APIRouter(tags=["evidence"])


@router.post("/api/evidence")
def submit_evidence(req: SubmitEvidenceRequest):
    rt = get_store().get(req.tenant_id)
    if rt is None:
        raise HTTPException(status_code=404, detail=f"unknown tenant '{req.tenant_id}'")
    ev = Evidence(
        tenant_id=req.tenant_id, etype=req.etype, title=req.title,
        summary=req.summary, source=req.source, verified=req.verified,
        payload=req.payload,
    )
    rt.add_evidence(ev)
    return {"ok": True, "data": ev.to_dict()}


@router.get("/api/evidence/{tenant_id}")
def list_evidence(tenant_id: str):
    rt = get_store().get(tenant_id)
    if rt is None:
        raise HTTPException(status_code=404, detail=f"unknown tenant '{tenant_id}'")
    return {"ok": True, "data": [e.to_dict() for e in rt.evidence_list()]}
