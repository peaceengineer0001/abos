"""SecurityDirector — Govern stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence


class SecurityDirector(BossAgent):
    NAME = "SecurityDirector"
    STREAM = "govern"
    CHANNEL = "#compliance"
    TITLE = "Security Director"
    PERSONA = ("Owns access control, tenant isolation, and threat flags. "
               "Restricted-access changes require admin authority and human approval.")
    PROPOSABLE_ACTIONS = ["draft_recommendation", "grant_access"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        flags: List[Dict[str, Any]] = []
        # Detect any cross-tenant evidence leakage in the bundle.
        stray = [e.id for e in (evidence or []) if e.tenant_id != self.tenant_id]
        if stray:
            flags.append({"title": "Cross-tenant evidence detected", "severity": "critical",
                          "detail": f"evidence outside tenant: {stray}"})
        pending_access = context.get("pending_access_requests", 0)
        if pending_access:
            flags.append({"title": f"{pending_access} access request(s) pending review",
                          "severity": "medium"})
        signal = 95.0 if not flags else max(0.0, 95.0 - 30.0 * len(flags))
        return {"agent": self.NAME, "signal": signal, "flags": flags,
                "summary": ("Access posture nominal; tenant isolation intact."
                            if not flags else f"{len(flags)} security flag(s) raised.")}
