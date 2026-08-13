"""
abos.core.scorecard
===================

The BOSS 7-metric rubric scorecard. Larry Braden's canonical rubric is a pilot
deliverable ("confirm the BOSS rubric" — see the presenter brief), so the seven
metrics here are the ABOS *default* rubric and are fully configurable per tenant.

Each metric is scored 0–100, weighted, and rolled up into a single BOSS score
plus a letter grade. Scores are evidence-weighted: a metric backed by weak or
missing evidence is discounted so the scorecard never over-claims.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# The seven canonical BOSS metrics (default rubric). Weights sum to 1.0.
DEFAULT_RUBRIC: List[Dict[str, Any]] = [
    {"key": "financial_health", "label": "Financial Health", "weight": 0.20, "stream": "run"},
    {"key": "operational_efficiency", "label": "Operational Efficiency", "weight": 0.15, "stream": "run"},
    {"key": "compliance_posture", "label": "Compliance Posture", "weight": 0.15, "stream": "govern"},
    {"key": "risk_exposure", "label": "Risk Exposure (inverse)", "weight": 0.15, "stream": "govern"},
    {"key": "growth_momentum", "label": "Growth Momentum", "weight": 0.15, "stream": "grow"},
    {"key": "client_health", "label": "Client Health", "weight": 0.10, "stream": "grow"},
    {"key": "people_capacity", "label": "People & Capacity", "weight": 0.10, "stream": "run"},
]


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


@dataclass
class MetricScore:
    key: str
    label: str
    weight: float
    stream: str
    value: float                 # 0..100 raw metric value
    evidence_confidence: float = 1.0   # 0..1 discount from evidence layer

    @property
    def effective(self) -> float:
        return round(self.value * self.evidence_confidence, 2)

    @property
    def contribution(self) -> float:
        return round(self.effective * self.weight, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key, "label": self.label, "weight": self.weight,
            "stream": self.stream, "value": self.value,
            "evidence_confidence": self.evidence_confidence,
            "effective": self.effective, "contribution": self.contribution,
        }


@dataclass
class Scorecard:
    tenant_id: str
    metrics: List[MetricScore]
    generated_at: int = field(default_factory=lambda: int(time.time()))

    @property
    def score(self) -> float:
        return round(sum(m.contribution for m in self.metrics), 2)

    @property
    def grade(self) -> str:
        return _grade(self.score)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "score": self.score,
            "grade": self.grade,
            "generated_at": self.generated_at,
            "metrics": [m.to_dict() for m in self.metrics],
            "by_stream": self._by_stream(),
        }

    def _by_stream(self) -> Dict[str, float]:
        out: Dict[str, List[float]] = {}
        for m in self.metrics:
            out.setdefault(m.stream, []).append(m.effective)
        return {k: round(sum(v) / len(v), 2) for k, v in out.items()}


def build_scorecard(
    tenant_id: str,
    values: Dict[str, float],
    rubric: Optional[List[Dict[str, Any]]] = None,
    evidence_confidence: Optional[Dict[str, float]] = None,
) -> Scorecard:
    """Assemble a scorecard from raw metric values (0..100) and an optional
    per-metric evidence-confidence map (0..1)."""
    rubric = rubric or DEFAULT_RUBRIC
    ec = evidence_confidence or {}
    metrics = [
        MetricScore(
            key=m["key"], label=m["label"], weight=m["weight"], stream=m["stream"],
            value=float(values.get(m["key"], 0.0)),
            evidence_confidence=float(ec.get(m["key"], 1.0)),
        )
        for m in rubric
    ]
    return Scorecard(tenant_id=tenant_id, metrics=metrics)
