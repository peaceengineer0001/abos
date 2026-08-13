"""RiskManager — Govern stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence, assess_evidence


class RiskManager(BossAgent):
    NAME = "RiskManager"
    STREAM = "govern"
    CHANNEL = "#compliance"
    TITLE = "Risk Manager"
    PERSONA = ("Scores risk, weights evidence, and escalates red flags. "
               "Turns weak evidence + high exposure into a governed pause.")
    PROPOSABLE_ACTIONS = ["draft_recommendation"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        evidence = evidence or []
        assessment = assess_evidence(evidence, min_confidence=0.6)
        exposure = float(context.get("exposure_usd", 0))  # financial exposure
        counterparties = context.get("counterparties", [])
        # Risk rises with exposure and falls with evidence confidence.
        base_risk = min(100.0, exposure / 1000.0)  # $100k -> 100
        risk_score = round(base_risk * (1.0 - 0.5 * assessment.confidence), 1)
        severity = ("critical" if risk_score >= 70 else
                    "high" if risk_score >= 45 else
                    "medium" if risk_score >= 20 else "low")
        flags: List[Dict[str, Any]] = []
        if risk_score >= 45:
            flags.append({"title": f"Elevated risk on {len(counterparties)} counterparties",
                          "severity": severity,
                          "detail": f"exposure ${exposure:,.0f}, "
                                    f"evidence confidence {assessment.confidence}"})
        signal = round(100.0 - risk_score, 1)  # inverse: higher = safer
        return {"agent": self.NAME, "signal": signal, "risk_score": risk_score,
                "severity": severity, "evidence": assessment.to_dict(), "flags": flags,
                "summary": f"Risk score {risk_score}/100 ({severity})."}
