"""ComplianceOfficer — Govern stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence, EvidenceType


class ComplianceOfficer(BossAgent):
    NAME = "ComplianceOfficer"
    STREAM = "govern"
    CHANNEL = "#compliance"
    TITLE = "Compliance Officer"
    PERSONA = ("Watches policy checks, regulatory gaps, and approval gating. "
               "Never files anything itself — flags gaps and requires human sign-off.")
    PROPOSABLE_ACTIONS = ["draft_recommendation", "file_compliance"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        evidence = evidence or []
        filings = [e for e in evidence if e.etype == EvidenceType.COMPLIANCE_FILING.value]
        contracts = [e for e in evidence if e.etype == EvidenceType.CONTRACT.value]
        gaps: List[str] = []
        required = context.get("required_filings", [])
        have = {f.title.lower() for f in filings}
        for r in required:
            if not any(r.lower() in h for h in have):
                gaps.append(r)
        unsigned = [c.title for c in contracts if not c.verified]
        if unsigned:
            gaps.append(f"unverified contracts: {', '.join(unsigned)}")
        signal = max(0.0, 100.0 - 20.0 * len(gaps))
        flags = [{"title": f"Compliance gap: {g}", "severity": "high"} for g in gaps]
        return {"agent": self.NAME, "signal": signal, "gaps": gaps, "flags": flags,
                "summary": (f"{len(gaps)} compliance gap(s) detected." if gaps
                            else "No compliance gaps detected in provided evidence.")}
