"""FinanceDirector — Run stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence, EvidenceType


class FinanceDirector(BossAgent):
    NAME = "FinanceDirector"
    STREAM = "run"
    CHANNEL = "#finance"
    TITLE = "Finance Director"
    PERSONA = ("Tracks budget and cash flow and gates payment approvals. "
               "Payments require contract + financial-record evidence and human approval.")
    PROPOSABLE_ACTIONS = ["draft_recommendation", "approve_payment"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        cash = float(context.get("cash_on_hand", 0))
        monthly_burn = float(context.get("monthly_burn", 1))
        ar = float(context.get("accounts_receivable", 0))
        ap = float(context.get("accounts_payable", 0))
        runway = round(cash / monthly_burn, 1) if monthly_burn else 999.0
        flags: List[Dict[str, Any]] = []
        if runway < 3:
            flags.append({"title": f"Runway {runway} months", "severity": "critical"})
        elif runway < 6:
            flags.append({"title": f"Runway {runway} months", "severity": "high"})
        if ap > cash:
            flags.append({"title": "Payables exceed cash on hand", "severity": "high"})
        has_fin = any(e.etype == EvidenceType.FINANCIAL_RECORD.value
                      for e in (evidence or []))
        # Signal blends runway health and evidence availability.
        signal = min(100.0, max(0.0, runway * 8.0)) * (1.0 if has_fin else 0.85)
        return {"agent": self.NAME, "signal": round(signal, 1), "runway_months": runway,
                "cash_on_hand": cash, "ar": ar, "ap": ap, "flags": flags,
                "summary": f"Runway {runway} mo; cash ${cash:,.0f}, AP ${ap:,.0f}."}
