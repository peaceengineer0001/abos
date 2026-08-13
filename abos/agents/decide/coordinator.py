"""ExecutiveCoordinator — Decide stream. Cross-stream dispatch + audit."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.approval import (
    ApprovalQueue, GovernedDecision, governed_decision_from_policy,
)
from ...core.evidence import Evidence
from ...core.policy import Actor, Decision, PolicyEngine, Role
from ...nostr import events as ev


class ExecutiveCoordinator(BossAgent):
    NAME = "ExecutiveCoordinator"
    STREAM = "decide"
    CHANNEL = "#decisions"
    TITLE = "Executive Coordinator"
    PERSONA = ("Coordinates the streams, dispatches governed actions, and keeps the "
               "audit log. High-impact actions are parked in the human approval queue.")
    PROPOSABLE_ACTIONS = ["draft_recommendation"]

    def __init__(self, tenant_id, bus, policy: PolicyEngine,
                 approval_queue: Optional[ApprovalQueue] = None, **kw) -> None:
        super().__init__(tenant_id, bus, policy, **kw)
        self.queue = approval_queue or ApprovalQueue()

    def dispatch(
        self,
        proposer: str,
        action: str,
        title: str,
        summary: str,
        actor: Actor,
        evidence: Optional[List[Evidence]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Run a proposed action through policy and route the outcome.

        Returns a dict describing the outcome: allowed / parked for approval /
        denied — always with the policy reason and always audit-logged.
        """
        result = self.policy.evaluate(actor, action, self.tenant_id, evidence=evidence)

        if result.decision == Decision.DENY:
            # Publish a deterministic policy-denial event to the bus.
            self.bus.post(self.identity.privkey, self.CHANNEL, ev.KIND_POLICY_DENIAL,
                          {"agent": self.NAME, "action": action, "title": title,
                           "reason": result.reason, "policy": result.to_dict()},
                          extra_tags=[["agent", self.NAME], ["decision", "deny"]])
            return {"outcome": "denied", "reason": result.reason,
                    "policy": result.to_dict()}

        if result.decision == Decision.REQUIRES_APPROVAL:
            decision = governed_decision_from_policy(
                result, title=title, proposed_by=proposer, stream=self.STREAM,
                summary=summary, evidence_ids=[e.id for e in (evidence or [])],
                recommendations=recommendations or [])
            self.queue.enqueue(decision)
            self.bus.post(self.identity.privkey, self.CHANNEL, ev.KIND_APPROVAL_REQUEST,
                          decision.to_dict(),
                          extra_tags=[["agent", self.NAME], ["decision_id", decision.id]])
            return {"outcome": "requires_approval", "decision": decision.to_dict(),
                    "reason": result.reason}

        # ALLOW: coordinator records the governed action as executed.
        self.bus.post(self.identity.privkey, self.CHANNEL, ev.KIND_GOVERNED_DECISION,
                      {"agent": self.NAME, "action": action, "title": title,
                       "status": "executed", "reason": result.reason},
                      extra_tags=[["agent", self.NAME], ["decision", "allow"]])
        return {"outcome": "allowed", "reason": result.reason, "policy": result.to_dict()}

    def resolve(self, decision_id: str, actor: Actor, approve: bool,
                reason: str = "") -> Dict[str, Any]:
        """Apply a human approve/deny to a parked decision and publish the result."""
        if approve:
            d = self.queue.approve(decision_id, actor, reason)
        else:
            d = self.queue.deny(decision_id, actor, reason)
        self.bus.post(self.identity.privkey, self.CHANNEL, ev.KIND_APPROVAL_RESULT,
                      d.to_dict(),
                      extra_tags=[["agent", self.NAME], ["decision_id", d.id],
                                  ["result", d.status.value]])
        return d.to_dict()

    def audit(self) -> List[Dict[str, Any]]:
        return self.policy.audit(self.tenant_id)
