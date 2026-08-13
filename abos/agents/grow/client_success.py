"""ClientSuccessDirector — Grow stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence


class ClientSuccessDirector(BossAgent):
    NAME = "ClientSuccessDirector"
    STREAM = "grow"
    CHANNEL = "#growth"
    TITLE = "Client Success Director"
    PERSONA = ("Tracks NPS, renewal risk, and escalation routing. "
               "Routes at-risk accounts to the council; renewals stay human-approved.")
    PROPOSABLE_ACTIONS = ["draft_recommendation", "assign_task"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        nps = float(context.get("nps", 0))
        accounts = context.get("accounts", [])  # {name, health, renewal_days}
        at_risk = [a for a in accounts if str(a.get("health", "")).lower() in ("red", "at_risk")]
        upcoming = [a for a in accounts if 0 <= int(a.get("renewal_days", 999)) <= 60]
        flags: List[Dict[str, Any]] = []
        if at_risk:
            flags.append({"title": f"{len(at_risk)} account(s) at risk", "severity": "high",
                          "detail": ", ".join(a.get("name", "?") for a in at_risk)})
        if nps < 30:
            flags.append({"title": f"NPS {nps} below healthy threshold", "severity": "medium"})
        # Signal: NPS normalized (-100..100 -> 0..100).
        signal = round(max(0.0, min(100.0, (nps + 100.0) / 2.0)), 1)
        return {"agent": self.NAME, "signal": signal, "nps": nps,
                "at_risk_count": len(at_risk), "renewals_due": len(upcoming),
                "flags": flags,
                "summary": f"NPS {nps}; {len(at_risk)} at-risk, {len(upcoming)} renewals due."}
