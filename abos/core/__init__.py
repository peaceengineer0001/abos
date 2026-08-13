"""
abos.core
=========

The governance core of the Agentic Business Operating System:

* :mod:`abos.core.agent` — the ``BossAgent`` base (extends the Agent Zero model).
* :mod:`abos.core.policy` — multi-tenant, role-based, evidence-aware policy engine.
* :mod:`abos.core.evidence` — evidence taxonomy + weighted-confidence scoring.
* :mod:`abos.core.scorecard` — the BOSS 7-metric rubric scorecard.
* :mod:`abos.core.approval` — governed decisions + human approval queue.
"""

from .agent import BossAgent, AgentIdentity
from .policy import (
    PolicyEngine, PolicyResult, ActionSpec, Actor, Role, Decision,
    DEFAULT_ACTIONS, ROLE_RANK,
)
from .evidence import Evidence, EvidenceType, EvidenceAssessment, assess_evidence, DEFAULT_WEIGHTS
from .scorecard import Scorecard, MetricScore, build_scorecard, DEFAULT_RUBRIC
from .approval import (
    GovernedDecision, ApprovalQueue, ApprovalError, DecisionStatus,
    governed_decision_from_policy,
)

__all__ = [
    "BossAgent", "AgentIdentity",
    "PolicyEngine", "PolicyResult", "ActionSpec", "Actor", "Role", "Decision",
    "DEFAULT_ACTIONS", "ROLE_RANK",
    "Evidence", "EvidenceType", "EvidenceAssessment", "assess_evidence", "DEFAULT_WEIGHTS",
    "Scorecard", "MetricScore", "build_scorecard", "DEFAULT_RUBRIC",
    "GovernedDecision", "ApprovalQueue", "ApprovalError", "DecisionStatus",
    "governed_decision_from_policy",
]
