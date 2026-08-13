"""Pydantic request/response models for the ABOS API."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CreateTenantRequest(BaseModel):
    name: str = Field(..., examples=["Blue Horizon Yachts"])
    business_type: str = Field(..., examples=["marine_services"])
    tenant_id: Optional[str] = None


class CreateUserRequest(BaseModel):
    name: str
    role: str = Field(..., description="viewer | operator | approver | admin")


class SubmitEvidenceRequest(BaseModel):
    tenant_id: str
    etype: str = Field(..., description="document|contract|financial_record|...")
    title: str
    summary: str = ""
    source: str = "api"
    verified: bool = False
    payload: Dict[str, Any] = Field(default_factory=dict)


class DispatchActionRequest(BaseModel):
    tenant_id: str
    actor_id: str
    action: str
    title: str
    summary: str = ""
    proposed_by: str = "ExecutiveCoordinator"
    evidence_ids: List[str] = Field(default_factory=list)


class ResolveDecisionRequest(BaseModel):
    tenant_id: str
    actor_id: str
    reason: str = ""


class RunCouncilRequest(BaseModel):
    tenant_id: str
    context: Dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel):
    ok: bool = True
    data: Any = None
    error: Optional[str] = None
