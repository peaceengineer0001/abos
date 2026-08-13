"""MarketingDirector — Grow stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence


class MarketingDirector(BossAgent):
    NAME = "MarketingDirector"
    STREAM = "grow"
    CHANNEL = "#growth"
    TITLE = "Marketing Director"
    PERSONA = ("Plans campaigns, drafts content briefs, and segments audiences. "
               "External sends are gated (send_external_message requires approval).")
    PROPOSABLE_ACTIONS = ["draft_recommendation", "send_external_message"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        spend = float(context.get("marketing_spend", 0))
        leads = int(context.get("leads_generated", 0))
        mql_to_sql = float(context.get("mql_to_sql_pct", 0))
        cac = round(spend / leads, 2) if leads else 0.0
        target_cac = float(context.get("target_cac", 0)) or None
        flags: List[Dict[str, Any]] = []
        if target_cac and cac > target_cac:
            flags.append({"title": f"CAC ${cac} above target ${target_cac}",
                          "severity": "medium"})
        # Signal blends lead volume health and funnel conversion.
        signal = round(min(100.0, mql_to_sql * 2.0 + min(50.0, leads / 2.0)), 1)
        return {"agent": self.NAME, "signal": signal, "cac": cac, "leads": leads,
                "mql_to_sql_pct": mql_to_sql, "flags": flags,
                "summary": f"{leads} leads, CAC ${cac}, MQL→SQL {mql_to_sql}%."}
