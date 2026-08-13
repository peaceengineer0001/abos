"""GrowthDirector — Grow stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence


class GrowthDirector(BossAgent):
    NAME = "GrowthDirector"
    STREAM = "grow"
    CHANNEL = "#growth"
    TITLE = "Growth Director"
    PERSONA = ("Manages pipeline stages and scores opportunities. "
               "Drafts deal recommendations; contract execution stays with humans.")
    PROPOSABLE_ACTIONS = ["draft_recommendation", "sign_contract"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        pipeline = context.get("pipeline", [])  # list of {value, stage, prob}
        weighted = sum(float(d.get("value", 0)) * float(d.get("prob", 0)) for d in pipeline)
        total_value = sum(float(d.get("value", 0)) for d in pipeline)
        stale = [d for d in pipeline if int(d.get("days_in_stage", 0)) > 45]
        flags: List[Dict[str, Any]] = []
        if stale:
            flags.append({"title": f"{len(stale)} stale opportunities (>45d in stage)",
                          "severity": "medium"})
        target = float(context.get("pipeline_target", 1))
        coverage = round(100.0 * weighted / target, 1) if target else 0.0
        signal = min(100.0, coverage)
        return {"agent": self.NAME, "signal": signal, "weighted_pipeline": round(weighted, 0),
                "total_pipeline": round(total_value, 0), "coverage_pct": coverage,
                "stale_count": len(stale), "flags": flags,
                "summary": f"Weighted pipeline ${weighted:,.0f} ({coverage}% of target)."}
