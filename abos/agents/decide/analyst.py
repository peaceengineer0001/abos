"""ChiefAnalyst — Decide stream. Aggregates evidence + council findings."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence, assess_evidence
from ...core.scorecard import build_scorecard, DEFAULT_RUBRIC
from ...nostr import events as ev


# Which council signals feed which scorecard metric.
_METRIC_SOURCES = {
    "financial_health": ["FinanceDirector"],
    "operational_efficiency": ["OperationsDirector"],
    "compliance_posture": ["ComplianceOfficer"],
    "risk_exposure": ["RiskManager", "SecurityDirector"],
    "growth_momentum": ["GrowthDirector", "MarketingDirector"],
    "client_health": ["ClientSuccessDirector"],
    "people_capacity": ["PeopleDirector"],
}


class ChiefAnalyst(BossAgent):
    NAME = "ChiefAnalyst"
    STREAM = "decide"
    CHANNEL = "#decisions"
    TITLE = "Chief Analyst"
    PERSONA = ("Aggregates evidence and specialist findings into a BOSS scorecard "
               "and a synthesized recommendation. Prepares decisions; never executes.")
    PROPOSABLE_ACTIONS = ["draft_recommendation"]

    def aggregate(
        self,
        findings: List[Dict[str, Any]],
        evidence: Optional[List[Evidence]] = None,
        rubric: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Turn council findings + evidence into a scorecard + synthesis."""
        rubric = rubric or DEFAULT_RUBRIC
        by_agent = {f.get("agent"): f for f in findings}
        assessment = assess_evidence(evidence or [], min_confidence=0.6)

        metric_values: Dict[str, float] = {}
        metric_conf: Dict[str, float] = {}
        for m in rubric:
            sources = _METRIC_SOURCES.get(m["key"], [])
            signals = [float(by_agent[s]["signal"]) for s in sources
                       if s in by_agent and "signal" in by_agent[s]]
            metric_values[m["key"]] = round(sum(signals) / len(signals), 1) if signals else 0.0
            # Evidence confidence discounts metrics uniformly for the demo.
            metric_conf[m["key"]] = round(0.75 + 0.25 * assessment.confidence, 3)

        scorecard = build_scorecard(self.tenant_id, metric_values, rubric, metric_conf)

        all_flags: List[Dict[str, Any]] = []
        for f in findings:
            for fl in f.get("flags", []):
                all_flags.append({**fl, "agent": f.get("agent")})
        critical = [f for f in all_flags if f.get("severity") in ("critical", "high")]

        synthesis = {
            "agent": self.NAME,
            "scorecard": scorecard.to_dict(),
            "evidence": assessment.to_dict(),
            "flag_count": len(all_flags),
            "critical_flags": critical,
            "council_size": len(findings),
            "summary": (f"BOSS score {scorecard.score} ({scorecard.grade}); "
                        f"{len(critical)} critical/high flag(s) across "
                        f"{len(findings)} specialists."),
            "recommendation": self._recommend_disposition(scorecard.score, critical),
        }
        # Publish scorecard + analysis to the decisions channel.
        self.bus.post(self.identity.privkey, self.CHANNEL, ev.KIND_SCORECARD,
                      scorecard.to_dict(), extra_tags=[["agent", self.NAME]])
        self.publish_analysis(synthesis)
        return synthesis

    @staticmethod
    def _recommend_disposition(score: float, critical: List[Dict[str, Any]]) -> str:
        if critical:
            return "escalate_for_human_review"
        if score >= 80:
            return "proceed"
        if score >= 60:
            return "proceed_with_conditions"
        return "hold_and_remediate"
