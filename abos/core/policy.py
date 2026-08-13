"""
abos.core.policy
===============

The multi-tenant policy engine. This is the governance spine the presenter brief
leads with: *tenant, authority, evidence, approval, audit*. Every governed
action passes through :meth:`PolicyEngine.evaluate`, which returns a
deterministic ALLOW / REQUIRES_APPROVAL / DENY decision **with a logged reason**.

Guarantees:
  * **Tenant isolation** — an actor may only act within their own tenant; a
    cross-tenant request is denied deterministically.
  * **Role-based authority** — ``viewer < operator < approver < admin``; each
    action type declares the minimum role required to *execute* it.
  * **Evidence sufficiency** — high-impact actions require an evidence bundle
    that clears a confidence threshold and any required evidence types.
  * **Deterministic denial** — identical inputs always yield the identical
    decision, and every denial records *why* (for the audit log).

The classic demo case: a ``viewer`` cannot approve a payment without authority
or evidence — and ABOS says exactly why.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .evidence import Evidence, assess_evidence


# --------------------------------------------------------------------------- #
# Roles & authority ordering
# --------------------------------------------------------------------------- #
class Role(str, Enum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    APPROVER = "approver"
    ADMIN = "admin"


ROLE_RANK = {Role.VIEWER: 0, Role.OPERATOR: 1, Role.APPROVER: 2, Role.ADMIN: 3}


class Decision(str, Enum):
    ALLOW = "allow"
    REQUIRES_APPROVAL = "requires_approval"
    DENY = "deny"


@dataclass
class ActionSpec:
    """Declares the governance requirements for one type of action."""

    name: str
    min_role: Role                     # minimum role to *execute* directly
    high_impact: bool = False          # pauses for human approval
    required_evidence: List[str] = field(default_factory=list)
    min_confidence: float = 0.6
    description: str = ""


# The default ABOS action catalog. Business templates extend/override this.
DEFAULT_ACTIONS: Dict[str, ActionSpec] = {
    "read_workspace": ActionSpec("read_workspace", Role.VIEWER, description="View feeds"),
    "submit_evidence": ActionSpec("submit_evidence", Role.OPERATOR, description="Add evidence"),
    "draft_recommendation": ActionSpec("draft_recommendation", Role.OPERATOR,
                                       description="Agent drafts a recommendation"),
    "assign_task": ActionSpec("assign_task", Role.OPERATOR, description="Route/assign work"),
    "approve_payment": ActionSpec(
        "approve_payment", Role.APPROVER, high_impact=True,
        required_evidence=["contract", "financial_record"], min_confidence=0.75,
        description="Release a payment"),
    "sign_contract": ActionSpec(
        "sign_contract", Role.APPROVER, high_impact=True,
        required_evidence=["contract"], min_confidence=0.75,
        description="Execute a contract"),
    "file_compliance": ActionSpec(
        "file_compliance", Role.APPROVER, high_impact=True,
        required_evidence=["compliance_filing"], min_confidence=0.7,
        description="Submit a regulatory filing"),
    "send_external_message": ActionSpec(
        "send_external_message", Role.OPERATOR, high_impact=True,
        description="Send a message to an external counterparty"),
    "grant_access": ActionSpec(
        "grant_access", Role.ADMIN, high_impact=True,
        description="Grant or change restricted access"),
    "people_decision": ActionSpec(
        "people_decision", Role.ADMIN, high_impact=True,
        description="Hiring / termination / compensation"),
}


@dataclass
class Actor:
    """The principal requesting an action."""

    actor_id: str
    tenant_id: str
    role: Role


@dataclass
class PolicyResult:
    decision: Decision
    action: str
    reason: str
    actor_id: str
    tenant_id: str
    checks: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"pol_{uuid.uuid4().hex[:12]}")
    at: int = field(default_factory=lambda: int(time.time()))

    @property
    def allowed(self) -> bool:
        return self.decision != Decision.DENY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "decision": self.decision.value, "action": self.action,
            "reason": self.reason, "actor_id": self.actor_id,
            "tenant_id": self.tenant_id, "checks": self.checks, "at": self.at,
        }


class PolicyEngine:
    """Deterministic, auditable multi-tenant policy evaluator."""

    def __init__(self, actions: Optional[Dict[str, ActionSpec]] = None) -> None:
        self.actions = dict(DEFAULT_ACTIONS)
        if actions:
            self.actions.update(actions)
        self.audit_log: List[PolicyResult] = []

    def register_action(self, spec: ActionSpec) -> None:
        self.actions[spec.name] = spec

    def evaluate(
        self,
        actor: Actor,
        action: str,
        tenant_id: str,
        evidence: Optional[List[Evidence]] = None,
        weight_overrides: Optional[Dict[str, float]] = None,
    ) -> PolicyResult:
        """Evaluate one action request and append the result to the audit log."""
        evidence = evidence or []
        checks: Dict[str, Any] = {}

        # 1) Unknown action -> deny.
        spec = self.actions.get(action)
        if spec is None:
            return self._log(PolicyResult(
                Decision.DENY, action, f"unknown action '{action}'",
                actor.actor_id, actor.tenant_id, {"known_actions": list(self.actions)}))

        # 2) Tenant isolation -> deny on mismatch.
        tenant_ok = actor.tenant_id == tenant_id
        checks["tenant_isolation"] = {"actor_tenant": actor.tenant_id,
                                      "target_tenant": tenant_id, "ok": tenant_ok}
        if not tenant_ok:
            return self._log(PolicyResult(
                Decision.DENY, action,
                f"tenant isolation: actor '{actor.actor_id}' in '{actor.tenant_id}' "
                f"may not act on tenant '{tenant_id}'",
                actor.actor_id, actor.tenant_id, checks))

        # 3) Authority (role rank).
        have = ROLE_RANK[actor.role]
        need = ROLE_RANK[spec.min_role]
        authority_ok = have >= need
        checks["authority"] = {"actor_role": actor.role.value,
                               "required_role": spec.min_role.value, "ok": authority_ok}
        if not authority_ok:
            return self._log(PolicyResult(
                Decision.DENY, action,
                f"insufficient authority: '{action}' requires role "
                f"'{spec.min_role.value}' but actor is '{actor.role.value}'",
                actor.actor_id, actor.tenant_id, checks))

        # 4) Evidence sufficiency (for actions that require it).
        if spec.required_evidence or spec.high_impact:
            assessment = assess_evidence(
                [e for e in evidence if e.tenant_id == tenant_id],
                required_types=spec.required_evidence,
                min_confidence=spec.min_confidence,
                weight_overrides=weight_overrides,
            )
            checks["evidence"] = assessment.to_dict()
            if spec.required_evidence and not assessment.sufficient:
                missing = assessment.missing
                reason = (
                    f"insufficient evidence for '{action}': "
                    f"confidence {assessment.confidence} < {spec.min_confidence}"
                    + (f"; missing {missing}" if missing else "")
                )
                return self._log(PolicyResult(
                    Decision.DENY, action, reason,
                    actor.actor_id, actor.tenant_id, checks))

        # 5) High-impact -> requires human approval (even if authorized).
        if spec.high_impact:
            return self._log(PolicyResult(
                Decision.REQUIRES_APPROVAL, action,
                f"high-impact action '{action}' authorized but paused for human approval",
                actor.actor_id, actor.tenant_id, checks))

        # 6) Otherwise allow.
        return self._log(PolicyResult(
            Decision.ALLOW, action, f"action '{action}' allowed",
            actor.actor_id, actor.tenant_id, checks))

    def _log(self, result: PolicyResult) -> PolicyResult:
        self.audit_log.append(result)
        return result

    def audit(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = self.audit_log
        if tenant_id:
            rows = [r for r in rows if r.tenant_id == tenant_id]
        return [r.to_dict() for r in rows]
