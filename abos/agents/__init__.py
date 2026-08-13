"""
abos.agents
==========

The 11 BOSS specialist agents across the four streams, plus a factory that
instantiates the full council for a tenant — each with a real Nostr keypair and
wired to the tenant's workspace bus and policy engine.

Streams:
    govern  → ComplianceOfficer, SecurityDirector, RiskManager
    run     → OperationsDirector, FinanceDirector, PeopleDirector
    grow    → GrowthDirector, MarketingDirector, ClientSuccessDirector
    decide  → ChiefAnalyst, ExecutiveCoordinator
"""

from __future__ import annotations

from typing import Dict, List, Optional

from ..core.approval import ApprovalQueue
from ..core.policy import PolicyEngine
from ..nostr.channels import WorkspaceBus
from .govern import ComplianceOfficer, SecurityDirector, RiskManager
from .run import OperationsDirector, FinanceDirector, PeopleDirector
from .grow import GrowthDirector, MarketingDirector, ClientSuccessDirector
from .decide import ChiefAnalyst, ExecutiveCoordinator

# Ordered registry of the 11 specialist classes.
AGENT_CLASSES = [
    ComplianceOfficer, SecurityDirector, RiskManager,
    OperationsDirector, FinanceDirector, PeopleDirector,
    GrowthDirector, MarketingDirector, ClientSuccessDirector,
    ChiefAnalyst, ExecutiveCoordinator,
]

STREAMS = {
    "govern": ["ComplianceOfficer", "SecurityDirector", "RiskManager"],
    "run": ["OperationsDirector", "FinanceDirector", "PeopleDirector"],
    "grow": ["GrowthDirector", "MarketingDirector", "ClientSuccessDirector"],
    "decide": ["ChiefAnalyst", "ExecutiveCoordinator"],
}


class Council:
    """The full 11-agent BOSS council for one tenant."""

    def __init__(self, tenant_id: str, bus: WorkspaceBus, policy: PolicyEngine,
                 approval_queue: Optional[ApprovalQueue] = None,
                 relay_domain: str = "abos.workspace") -> None:
        self.tenant_id = tenant_id
        self.bus = bus
        self.policy = policy
        self.queue = approval_queue or ApprovalQueue()
        self.agents: Dict[str, object] = {}
        for cls in AGENT_CLASSES:
            if cls is ExecutiveCoordinator:
                agent = cls(tenant_id, bus, policy, approval_queue=self.queue,
                            relay_domain=relay_domain)
            else:
                agent = cls(tenant_id, bus, policy, relay_domain=relay_domain)
            self.agents[cls.NAME] = agent

    def get(self, name: str):
        return self.agents.get(name)

    @property
    def analyst(self) -> ChiefAnalyst:
        return self.agents["ChiefAnalyst"]  # type: ignore[return-value]

    @property
    def coordinator(self) -> ExecutiveCoordinator:
        return self.agents["ExecutiveCoordinator"]  # type: ignore[return-value]

    def specialists(self) -> List:
        """The 9 non-Decide specialists that produce findings."""
        return [a for name, a in self.agents.items()
                if name not in ("ChiefAnalyst", "ExecutiveCoordinator")]

    def announce(self) -> None:
        """Publish an online status for every agent to its channel."""
        for a in self.agents.values():
            a.status("online")

    def roster(self) -> List[dict]:
        return [a.to_dict() for a in self.agents.values()]


def build_council(tenant_id: str, bus: WorkspaceBus, policy: PolicyEngine,
                  approval_queue: Optional[ApprovalQueue] = None,
                  relay_domain: str = "abos.workspace") -> Council:
    return Council(tenant_id, bus, policy, approval_queue, relay_domain)


__all__ = [
    "AGENT_CLASSES", "STREAMS", "Council", "build_council",
    "ComplianceOfficer", "SecurityDirector", "RiskManager",
    "OperationsDirector", "FinanceDirector", "PeopleDirector",
    "GrowthDirector", "MarketingDirector", "ClientSuccessDirector",
    "ChiefAnalyst", "ExecutiveCoordinator",
]
