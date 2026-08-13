"""
abos.core.approval
=================

The governed-action / human-approval layer. When the policy engine returns
``REQUIRES_APPROVAL`` for a high-impact action, ABOS creates a
:class:`GovernedDecision` and parks it in the :class:`ApprovalQueue` until a
human with sufficient authority approves or denies it — with a recorded reason.

This is the "human stays in control" half of the pitch: agents analyze,
recommend, and draft; contracts, payments, filings, external messages, people
decisions, and restricted access wait here.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .policy import Actor, Decision, PolicyResult, Role, ROLE_RANK


class DecisionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXECUTED = "executed"


@dataclass
class GovernedDecision:
    """A high-impact action awaiting (or having received) human judgement."""

    tenant_id: str
    action: str
    title: str
    proposed_by: str                    # agent id / pubkey that proposed it
    stream: str = "decide"
    summary: str = ""
    evidence_ids: List[str] = field(default_factory=list)
    policy: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    status: DecisionStatus = DecisionStatus.PENDING
    resolved_by: Optional[str] = None
    resolution_reason: Optional[str] = None
    impact: str = "high"
    id: str = field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:12]}")
    created_at: int = field(default_factory=lambda: int(time.time()))
    resolved_at: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "tenant_id": self.tenant_id, "action": self.action,
            "title": self.title, "summary": self.summary, "stream": self.stream,
            "proposed_by": self.proposed_by, "evidence_ids": self.evidence_ids,
            "policy": self.policy, "recommendations": self.recommendations,
            "status": self.status.value, "impact": self.impact,
            "resolved_by": self.resolved_by, "resolution_reason": self.resolution_reason,
            "created_at": self.created_at, "resolved_at": self.resolved_at,
        }


class ApprovalError(Exception):
    """Raised when an approval/denial is itself not permitted."""


class ApprovalQueue:
    """In-memory queue of governed decisions (persisted by the API/state layer)."""

    def __init__(self) -> None:
        self._decisions: Dict[str, GovernedDecision] = {}

    def enqueue(self, decision: GovernedDecision) -> GovernedDecision:
        self._decisions[decision.id] = decision
        return decision

    def get(self, decision_id: str) -> Optional[GovernedDecision]:
        return self._decisions.get(decision_id)

    def pending(self, tenant_id: Optional[str] = None) -> List[GovernedDecision]:
        out = [d for d in self._decisions.values() if d.status == DecisionStatus.PENDING]
        if tenant_id:
            out = [d for d in out if d.tenant_id == tenant_id]
        return sorted(out, key=lambda d: d.created_at, reverse=True)

    def all(self, tenant_id: Optional[str] = None) -> List[GovernedDecision]:
        out = list(self._decisions.values())
        if tenant_id:
            out = [d for d in out if d.tenant_id == tenant_id]
        return sorted(out, key=lambda d: d.created_at, reverse=True)

    # -- human resolution --------------------------------------------------- #
    def _authorize_approver(self, decision: GovernedDecision, actor: Actor) -> None:
        if actor.tenant_id != decision.tenant_id:
            raise ApprovalError(
                f"tenant isolation: '{actor.actor_id}' cannot resolve decisions "
                f"for tenant '{decision.tenant_id}'")
        if ROLE_RANK[actor.role] < ROLE_RANK[Role.APPROVER]:
            raise ApprovalError(
                f"insufficient authority: role '{actor.role.value}' cannot approve/deny "
                f"(requires 'approver' or 'admin')")

    def approve(self, decision_id: str, actor: Actor, reason: str = "") -> GovernedDecision:
        d = self._require(decision_id)
        self._authorize_approver(d, actor)
        if d.status != DecisionStatus.PENDING:
            raise ApprovalError(f"decision {decision_id} already {d.status.value}")
        d.status = DecisionStatus.APPROVED
        d.resolved_by = actor.actor_id
        d.resolution_reason = reason or "approved by authorized human"
        d.resolved_at = int(time.time())
        return d

    def deny(self, decision_id: str, actor: Actor, reason: str) -> GovernedDecision:
        d = self._require(decision_id)
        self._authorize_approver(d, actor)
        if d.status != DecisionStatus.PENDING:
            raise ApprovalError(f"decision {decision_id} already {d.status.value}")
        if not reason:
            raise ApprovalError("a denial must include a reason")
        d.status = DecisionStatus.DENIED
        d.resolved_by = actor.actor_id
        d.resolution_reason = reason
        d.resolved_at = int(time.time())
        return d

    def _require(self, decision_id: str) -> GovernedDecision:
        d = self._decisions.get(decision_id)
        if d is None:
            raise ApprovalError(f"unknown decision '{decision_id}'")
        return d


def governed_decision_from_policy(
    policy_result: PolicyResult,
    title: str,
    proposed_by: str,
    stream: str = "decide",
    summary: str = "",
    evidence_ids: Optional[List[str]] = None,
    recommendations: Optional[List[Dict[str, Any]]] = None,
) -> GovernedDecision:
    """Create a GovernedDecision from a REQUIRES_APPROVAL policy result."""
    return GovernedDecision(
        tenant_id=policy_result.tenant_id,
        action=policy_result.action,
        title=title,
        proposed_by=proposed_by,
        stream=stream,
        summary=summary,
        evidence_ids=evidence_ids or [],
        policy=policy_result.to_dict(),
        recommendations=recommendations or [],
    )
