"""
abos.tenant
==========

The per-tenant runtime and the global tenant store.

A :class:`TenantRuntime` binds together everything a single business needs:
a workspace bus (NIP-28 channels on a relay), the shared policy engine, the
11-agent council, an evidence store, an approval queue, a user directory, and a
KPI/metric snapshot. The :class:`TenantStore` holds all runtimes for the API
and enforces that every tenant is isolated.

The whole store can be serialized to / restored from ``demo_state.json`` so the
demo web app has a stable, inspectable dataset.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .agents import build_council, Council
from .core.approval import ApprovalQueue, GovernedDecision, DecisionStatus
from .core.evidence import Evidence
from .core.policy import Actor, PolicyEngine, Role
from .core.scorecard import build_scorecard, Scorecard
from .nostr.channels import WorkspaceBus
from .nostr.relay import RelayBackend, get_relay
from .templates import load_template, rubric_for


@dataclass
class User:
    user_id: str
    name: str
    role: str
    tenant_id: str

    def actor(self) -> Actor:
        return Actor(actor_id=self.user_id, tenant_id=self.tenant_id, role=Role(self.role))

    def to_dict(self) -> Dict[str, Any]:
        return {"user_id": self.user_id, "name": self.name, "role": self.role,
                "tenant_id": self.tenant_id}


class TenantRuntime:
    """Everything a single tenant business runs on."""

    def __init__(self, tenant_id: str, name: str, business_type: str,
                 relay: Optional[RelayBackend] = None) -> None:
        self.tenant_id = tenant_id
        self.name = name
        self.business_type = business_type
        self.template = load_template(business_type)
        self.rubric = rubric_for(business_type)
        self.created_at = int(time.time())

        # Governance + bus + council
        self.policy = PolicyEngine()
        self.bus = WorkspaceBus(tenant_id, relay=relay or get_relay("local"))
        self.bus.ensure_channels()
        self.queue = ApprovalQueue()
        self.council: Council = build_council(tenant_id, self.bus, self.policy, self.queue)
        self.council.announce()

        # State stores
        self.users: Dict[str, User] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.metrics: Dict[str, float] = {}
        self.last_analysis: Optional[Dict[str, Any]] = None

    # -- users -------------------------------------------------------------- #
    def add_user(self, name: str, role: str, user_id: Optional[str] = None) -> User:
        uid = user_id or f"user_{uuid.uuid4().hex[:8]}"
        user = User(uid, name, role, self.tenant_id)
        self.users[uid] = user
        return user

    # -- evidence ----------------------------------------------------------- #
    def add_evidence(self, ev: Evidence) -> Evidence:
        ev.tenant_id = self.tenant_id  # enforce isolation
        self.evidence[ev.id] = ev
        return ev

    def evidence_list(self) -> List[Evidence]:
        return list(self.evidence.values())

    # -- analysis loop ------------------------------------------------------ #
    def run_council(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run every specialist over the shared context+evidence, then let the
        ChiefAnalyst aggregate into a scorecard + synthesis."""
        context = context or {}
        evidence = self.evidence_list()
        findings = []
        for agent in self.council.specialists():
            finding = agent.analyze(context, evidence)
            agent.publish_analysis(finding)
            findings.append(finding)
        synthesis = self.council.analyst.aggregate(findings, evidence, self.rubric)
        self.last_analysis = synthesis
        return synthesis

    # -- scorecard ---------------------------------------------------------- #
    def scorecard(self, values: Optional[Dict[str, float]] = None) -> Scorecard:
        vals = values or self._derive_metric_values()
        return build_scorecard(self.tenant_id, vals, self.rubric)

    def _derive_metric_values(self) -> Dict[str, float]:
        """Use the last analysis if available, else neutral defaults."""
        if self.last_analysis:
            sc = self.last_analysis.get("scorecard", {})
            return {m["key"]: m["value"] for m in sc.get("metrics", [])}
        return {m["key"]: 70.0 for m in self.rubric}

    # -- workspace ---------------------------------------------------------- #
    def workspace(self, channel: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "channels": {slug: ch.__dict__ for slug, ch in self.bus.channels.items()},
            "feed": self.bus.feed(channel, limit=limit),
        }

    # -- serialization ------------------------------------------------------ #
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id, "name": self.name,
            "business_type": self.business_type,
            "display_name": self.template.get("display_name"),
            "created_at": self.created_at,
            "users": [u.to_dict() for u in self.users.values()],
            "evidence": [e.to_dict() for e in self.evidence.values()],
            "metrics": self.metrics,
            "kpis": self.template.get("kpis", []),
            "agents": self.council.roster(),
            "pending_decisions": [d.to_dict() for d in self.queue.pending()],
            "all_decisions": [d.to_dict() for d in self.queue.all()],
            "scorecard": (self.last_analysis or {}).get("scorecard")
                         or self.scorecard().to_dict(),
            "workspace_feed": self.bus.feed(limit=200),
            "audit_log": self.policy.audit(self.tenant_id),
        }


class TenantStore:
    """Global, in-memory registry of tenant runtimes (per API process).

    A single shared relay backs all tenants but tenant isolation is enforced by
    the policy engine and by tagging every event with the tenant id.
    """

    def __init__(self, relay: Optional[RelayBackend] = None) -> None:
        self.relay = relay or get_relay("local")
        self.tenants: Dict[str, TenantRuntime] = {}

    def create_tenant(self, name: str, business_type: str,
                      tenant_id: Optional[str] = None) -> TenantRuntime:
        tid = tenant_id or f"tnt_{uuid.uuid4().hex[:8]}"
        if tid in self.tenants:
            raise ValueError(f"tenant '{tid}' already exists")
        rt = TenantRuntime(tid, name, business_type, relay=self.relay)
        self.tenants[tid] = rt
        return rt

    def get(self, tenant_id: str) -> Optional[TenantRuntime]:
        return self.tenants.get(tenant_id)

    def require(self, tenant_id: str) -> TenantRuntime:
        rt = self.tenants.get(tenant_id)
        if rt is None:
            raise KeyError(f"unknown tenant '{tenant_id}'")
        return rt

    def list(self) -> List[Dict[str, Any]]:
        return [{
            "tenant_id": t.tenant_id, "name": t.name,
            "business_type": t.business_type,
            "display_name": t.template.get("display_name"),
            "users": len(t.users), "evidence": len(t.evidence),
            "pending_decisions": len(t.queue.pending()),
        } for t in self.tenants.values()]

    def to_dict(self) -> Dict[str, Any]:
        return {"generated_at": int(time.time()),
                "tenants": {tid: t.to_dict() for tid, t in self.tenants.items()}}
