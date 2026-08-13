"""
abos.core.agent
==============

The base BOSS agent. Every one of the 11 specialists extends
:class:`BossAgent`, which layers the BOSS governance contract on top of the
peace-protocols **Agent Zero** capability model:

* Agent Zero gives an agent a persona (system prompt), a config, and access to
  the Unified MCP Bus tools (``mcp_bus``) — the "capacity" the user referred to.
* :class:`BossAgent` adds a **real Nostr identity** (secp256k1 keypair, npub),
  a home **workspace channel**, and the three governed capabilities every BOSS
  agent shares: ``observe`` (read evidence/feed), ``analyze`` (produce findings),
  and ``recommend`` (propose an action that flows through the policy engine).

Agents never execute high-impact actions directly — they publish
recommendations and, for high-impact actions, approval requests onto the Nostr
workspace bus. Execution waits for the human approval queue.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..nostr import crypto, events as ev
from ..nostr.channels import WorkspaceBus
from .evidence import Evidence
from .policy import Actor, PolicyEngine, PolicyResult, Role


@dataclass
class AgentIdentity:
    """A BOSS agent's cryptographic + directory identity."""

    name: str
    privkey: str
    pubkey: str
    npub: str
    nip05: str

    @classmethod
    def generate(cls, name: str, relay_domain: str = "abos.workspace") -> "AgentIdentity":
        sk = crypto.generate_privkey()
        pk = crypto.get_public_key(sk)
        return cls(
            name=name, privkey=sk, pubkey=pk,
            npub=crypto.to_bech32("npub", pk),
            nip05=f"{name.lower()}@{relay_domain}",
        )

    def public_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "pubkey": self.pubkey, "npub": self.npub,
                "nip05": self.nip05}


class BossAgent:
    """Base class for all BOSS specialist agents."""

    #: overridden by subclasses
    NAME: str = "boss_agent"
    STREAM: str = "decide"
    CHANNEL: str = "#decisions"
    TITLE: str = "BOSS Agent"
    # Agent Zero persona summary (the full prompt lives with the persona files).
    PERSONA: str = "A governed BOSS specialist agent."
    # Actions this agent is allowed to *propose* (must exist in the policy catalog).
    PROPOSABLE_ACTIONS: List[str] = ["draft_recommendation"]

    def __init__(
        self,
        tenant_id: str,
        bus: WorkspaceBus,
        policy: PolicyEngine,
        identity: Optional[AgentIdentity] = None,
        relay_domain: str = "abos.workspace",
    ) -> None:
        self.tenant_id = tenant_id
        self.bus = bus
        self.policy = policy
        self.identity = identity or AgentIdentity.generate(self.NAME, relay_domain)
        # Agents act with operator authority when proposing; high-impact actions
        # still get parked for human approval by the policy engine.
        self.actor = Actor(actor_id=f"agent:{self.NAME}",
                           tenant_id=tenant_id, role=Role.OPERATOR)
        self.last_status: Dict[str, Any] = {}

    # -- identity ----------------------------------------------------------- #
    @property
    def pubkey(self) -> str:
        return self.identity.pubkey

    def status(self, state: str = "online", detail: str = "") -> ev.NostrEvent:
        """Publish an agent heartbeat/status event to its channel."""
        payload = {"agent": self.NAME, "title": self.TITLE, "stream": self.STREAM,
                   "state": state, "detail": detail, "npub": self.identity.npub}
        self.last_status = {**payload, "at": int(time.time())}
        return self.bus.post(self.identity.privkey, self.CHANNEL,
                             ev.KIND_AGENT_STATUS, payload,
                             extra_tags=[["agent", self.NAME]])

    # -- observe ------------------------------------------------------------ #
    def observe(self, channel_slug: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.bus.feed(channel_slug or self.CHANNEL)

    # -- analyze (overridable) --------------------------------------------- #
    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        """Produce a domain finding. Subclasses override with real logic.

        Returns a dict with at least ``summary`` and ``signal`` (a 0..100 score
        the ChiefAnalyst can aggregate).
        """
        return {"agent": self.NAME, "summary": f"{self.TITLE} reviewed the context.",
                "signal": 70.0, "flags": []}

    def publish_analysis(self, finding: Dict[str, Any]) -> ev.NostrEvent:
        return self.bus.post(self.identity.privkey, self.CHANNEL,
                             ev.KIND_ANALYSIS, {"agent": self.NAME, **finding},
                             extra_tags=[["agent", self.NAME]])

    # -- recommend (goes through policy) ----------------------------------- #
    def recommend(
        self,
        action: str,
        title: str,
        rationale: str,
        evidence: Optional[List[Evidence]] = None,
    ) -> Dict[str, Any]:
        """Propose an action. Returns the recommendation + the policy result.

        The recommendation event is always published; the policy result tells the
        caller (ExecutiveCoordinator) whether it can proceed, needs approval, or
        was denied — with the reason.
        """
        result: PolicyResult = self.policy.evaluate(
            self.actor, action, self.tenant_id, evidence=evidence)
        rec = {
            "agent": self.NAME, "stream": self.STREAM, "action": action,
            "title": title, "rationale": rationale,
            "evidence_ids": [e.id for e in (evidence or [])],
            "policy_decision": result.decision.value,
            "policy_reason": result.reason,
        }
        self.bus.post(self.identity.privkey, self.CHANNEL,
                      ev.KIND_RECOMMENDATION, rec, extra_tags=[["agent", self.NAME]])
        return {"recommendation": rec, "policy": result.to_dict()}

    def flag_risk(self, title: str, severity: str, detail: str) -> ev.NostrEvent:
        payload = {"agent": self.NAME, "title": title, "severity": severity,
                   "detail": detail}
        return self.bus.post(self.identity.privkey, self.CHANNEL,
                             ev.KIND_RISK_FLAG, payload,
                             extra_tags=[["agent", self.NAME], ["severity", severity]])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.NAME, "title": self.TITLE, "stream": self.STREAM,
            "channel": self.CHANNEL, "persona": self.PERSONA,
            "proposable_actions": self.PROPOSABLE_ACTIONS,
            "identity": self.identity.public_dict(),
            "status": self.last_status or {"state": "initialized"},
        }
