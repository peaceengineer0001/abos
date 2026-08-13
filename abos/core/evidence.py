"""
abos.core.evidence
==================

Evidence is the currency of the BOSS operating loop: *evidence in, governed
action out*. This module defines the evidence taxonomy, an ``Evidence`` record,
and a weighted-confidence scorer that the ChiefAnalyst uses to decide whether a
recommendation is sufficiently supported to advance.

Nothing here decides *authority* (that is :mod:`abos.core.policy`); this only
scores how well-evidenced a proposed action is.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EvidenceType(str, Enum):
    DOCUMENT = "document"
    CONTRACT = "contract"
    FINANCIAL_RECORD = "financial_record"
    COUNTERPARTY_DATA = "counterparty_data"
    PROJECT_STATUS = "project_status"
    COMPLIANCE_FILING = "compliance_filing"
    COMMUNICATION = "communication"
    METRIC_FEED = "metric_feed"


# Default trust weight per evidence type (0..1). Tenants can override.
DEFAULT_WEIGHTS: Dict[str, float] = {
    EvidenceType.CONTRACT.value: 1.0,
    EvidenceType.FINANCIAL_RECORD.value: 0.95,
    EvidenceType.COMPLIANCE_FILING.value: 0.95,
    EvidenceType.COUNTERPARTY_DATA.value: 0.8,
    EvidenceType.DOCUMENT.value: 0.7,
    EvidenceType.PROJECT_STATUS.value: 0.65,
    EvidenceType.METRIC_FEED.value: 0.6,
    EvidenceType.COMMUNICATION.value: 0.4,
}


@dataclass
class Evidence:
    """A single, tenant-scoped piece of evidence submitted to the loop."""

    tenant_id: str
    etype: str
    title: str
    summary: str = ""
    source: str = "unknown"
    verified: bool = False
    payload: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    created_at: int = field(default_factory=lambda: int(time.time()))

    def weight(self, overrides: Optional[Dict[str, float]] = None) -> float:
        base = (overrides or DEFAULT_WEIGHTS).get(self.etype, 0.5)
        # Verified evidence keeps full weight; unverified is discounted 30%.
        return round(base * (1.0 if self.verified else 0.7), 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "tenant_id": self.tenant_id, "etype": self.etype,
            "title": self.title, "summary": self.summary, "source": self.source,
            "verified": self.verified, "payload": self.payload,
            "created_at": self.created_at, "weight": self.weight(),
        }


@dataclass
class EvidenceAssessment:
    """Result of scoring a bundle of evidence for a proposed action."""

    confidence: float                 # 0..1 aggregate confidence
    total_weight: float
    count: int
    sufficient: bool
    missing: List[str] = field(default_factory=list)
    detail: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence, "total_weight": self.total_weight,
            "count": self.count, "sufficient": self.sufficient,
            "missing": self.missing, "detail": self.detail,
        }


def assess_evidence(
    evidence: List[Evidence],
    required_types: Optional[List[str]] = None,
    min_confidence: float = 0.6,
    weight_overrides: Optional[Dict[str, float]] = None,
) -> EvidenceAssessment:
    """Score an evidence bundle.

    ``confidence`` uses a saturating aggregation of weights so a few strong,
    verified items outweigh many weak ones, capped at 1.0. ``required_types``
    lets an action demand specific evidence (e.g. a payment needs a
    ``contract`` + ``financial_record``); anything missing is reported and the
    bundle is marked insufficient.
    """
    present_types = {e.etype for e in evidence}
    weights = [e.weight(weight_overrides) for e in evidence]
    total = round(sum(weights), 3)
    # Saturating confidence: 1 - product(1 - w_i)
    prod = 1.0
    for w in weights:
        prod *= (1.0 - min(w, 0.99))
    confidence = round(1.0 - prod, 3)

    missing = [t for t in (required_types or []) if t not in present_types]
    sufficient = confidence >= min_confidence and not missing

    return EvidenceAssessment(
        confidence=confidence,
        total_weight=total,
        count=len(evidence),
        sufficient=sufficient,
        missing=missing,
        detail={
            "present_types": sorted(present_types),
            "required_types": required_types or [],
            "min_confidence": min_confidence,
        },
    )
