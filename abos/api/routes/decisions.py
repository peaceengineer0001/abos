"""Governed-decision routes: dispatch, list, approve, deny, audit."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ...core.approval import ApprovalError
from ..models import DispatchActionRequest, ResolveDecisionRequest
from ..state import get_store

router = APIRouter(tags=["decisions"])


def _tenant(tenant_id: str):
    rt = get_store().get(tenant_id)
    if rt is None:
        raise HTTPException(status_code=404, detail=f"unknown tenant '{tenant_id}'")
    return rt


def _actor(rt, actor_id: str):
    user = rt.users.get(actor_id)
    if user is None:
        raise HTTPException(status_code=404,
                            detail=f"unknown actor '{actor_id}' in tenant '{rt.tenant_id}'")
    return user.actor()


@router.post("/api/decisions/dispatch")
def dispatch(req: DispatchActionRequest):
    """Run a proposed action through the policy engine and route the outcome
    (allowed / requires_approval / denied) — always with the reason."""
    rt = _tenant(req.tenant_id)
    actor = _actor(rt, req.actor_id)
    evidence = ([rt.evidence[eid] for eid in req.evidence_ids if eid in rt.evidence]
                if req.evidence_ids else rt.evidence_list())
    outcome = rt.council.coordinator.dispatch(
        req.proposed_by, req.action, req.title, req.summary, actor, evidence=evidence)
    return {"ok": True, "data": outcome}


@router.get("/api/decisions")
def list_decisions(tenant_id: str = Query(...), status: str | None = Query(default=None)):
    rt = _tenant(tenant_id)
    if status == "pending":
        rows = [d.to_dict() for d in rt.queue.pending()]
    else:
        rows = [d.to_dict() for d in rt.queue.all()]
    return {"ok": True, "data": rows}


@router.post("/api/decisions/{decision_id}/approve")
def approve(decision_id: str, req: ResolveDecisionRequest):
    rt = _tenant(req.tenant_id)
    actor = _actor(rt, req.actor_id)
    try:
        result = rt.council.coordinator.resolve(decision_id, actor, True, req.reason)
    except ApprovalError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return {"ok": True, "data": result}


@router.post("/api/decisions/{decision_id}/deny")
def deny(decision_id: str, req: ResolveDecisionRequest):
    rt = _tenant(req.tenant_id)
    actor = _actor(rt, req.actor_id)
    try:
        result = rt.council.coordinator.resolve(decision_id, actor, False, req.reason)
    except ApprovalError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return {"ok": True, "data": result}


@router.get("/api/audit/{tenant_id}")
def audit(tenant_id: str):
    rt = _tenant(tenant_id)
    return {"ok": True, "data": rt.policy.audit(tenant_id)}
