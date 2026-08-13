"""PeopleDirector — Run stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence


class PeopleDirector(BossAgent):
    NAME = "PeopleDirector"
    STREAM = "run"
    CHANNEL = "#ops"
    TITLE = "People Director"
    PERSONA = ("Handles team assignments, capacity planning, and onboarding. "
               "Hiring/termination/comp are people_decisions requiring admin + approval.")
    PROPOSABLE_ACTIONS = ["draft_recommendation", "assign_task", "people_decision"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        headcount = int(context.get("headcount", 0))
        open_roles = int(context.get("open_roles", 0))
        utilization = float(context.get("utilization_pct", 75.0))
        onboarding = int(context.get("onboarding_in_progress", 0))
        flags: List[Dict[str, Any]] = []
        if utilization > 90:
            flags.append({"title": f"Utilization {utilization}% — burnout risk",
                          "severity": "high"})
        if open_roles > max(1, headcount // 5):
            flags.append({"title": f"{open_roles} open roles vs {headcount} staff",
                          "severity": "medium"})
        # Signal: balanced utilization near 80% is ideal.
        signal = round(max(0.0, 100.0 - abs(utilization - 80.0) * 2.0), 1)
        return {"agent": self.NAME, "signal": signal, "headcount": headcount,
                "open_roles": open_roles, "utilization_pct": utilization,
                "onboarding": onboarding, "flags": flags,
                "summary": f"{headcount} staff, {open_roles} open roles, util {utilization}%."}
