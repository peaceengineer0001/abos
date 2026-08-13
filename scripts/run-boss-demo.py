#!/usr/bin/env python3
"""
run-boss-demo.py — the deterministic BOSS demo from the presenter brief.

Two scenarios (matching the Larry Braden brief):

  1. A two-vessel review is routed to the specialist council (Client Success,
     Compliance, Finance, Operations), aggregated by the Chief Analyst, and
     PAUSES for human approval because it is high risk.

  2. An unauthorized payment request is BLOCKED deterministically and the reason
     is recorded — a viewer cannot approve a payment without authority/evidence.

Usage::

    python3 scripts/run-boss-demo.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abos.tenant import TenantStore                       # noqa: E402
from abos.core.evidence import Evidence, EvidenceType     # noqa: E402


def rule(title: str) -> None:
    print("\n" + "═" * 74)
    print(f"  {title}")
    print("═" * 74)


def main() -> None:
    rule("ABOS · BOSS Framework demo — Evidence in, governed action out")
    store = TenantStore()
    rt = store.create_tenant("Blue Horizon Marine Services", "marine_services",
                             tenant_id="tnt_demo_marine")
    print(f"Tenant: {rt.name}  ({rt.business_type})")
    print(f"Workspace channels: {', '.join(rt.bus.channels)}")
    print(f"Council: {len(rt.council.agents)} agents across 4 streams "
          f"(govern / run / grow / decide)")

    # Directory of humans with roles.
    admin = rt.add_user("Larry Braden", "admin")
    approver = rt.add_user("Priya Approver", "approver")
    viewer = rt.add_user("Sam Viewer", "viewer")
    print(f"Users: {admin.name} (admin), {approver.name} (approver), "
          f"{viewer.name} (viewer)")

    # Evidence in.
    for etype, title, verified in [
        (EvidenceType.CONTRACT.value, "Charter Agreement — MV Serenity", True),
        (EvidenceType.COMPLIANCE_FILING.value, "USCG documentation — MV Serenity", True),
        (EvidenceType.FINANCIAL_RECORD.value, "Q2 maintenance ledger", True),
        (EvidenceType.COUNTERPARTY_DATA.value, "Dockyard Vendor Ltd insurance", False),
    ]:
        rt.add_evidence(Evidence(rt.tenant_id, etype, title, verified=verified, source="demo"))
    print(f"Evidence submitted: {len(rt.evidence_list())} items")

    # ---------------------------------------------------------------- Scenario 1
    rule("Scenario 1 · Two-vessel review → specialist council → governed pause")
    ctx = {
        "exposure_usd": 68000, "counterparties": ["Dockyard Vendor Ltd", "FuelCo"],
        "cash_on_hand": 210000, "monthly_burn": 55000, "accounts_payable": 47000,
        "open_tasks": 18, "overdue_tasks": 3, "completed_tasks": 52,
        "required_filings": ["USCG vessel documentation", "State registration renewal"],
        "nps": 41,
        "accounts": [{"name": "Regatta Partners", "health": "red", "renewal_days": 28}],
    }
    synthesis = rt.run_council(ctx)
    card = synthesis["scorecard"]
    print(f"\nChief Analyst synthesis:")
    print(f"  BOSS score : {card['score']} ({card['grade']})")
    print(f"  Disposition: {synthesis['recommendation']}")
    print(f"  Critical/high flags routed to the council:")
    for f in synthesis["critical_flags"]:
        print(f"    - [{f['severity']:<8}] {f['agent']}: {f['title']}")

    coord = rt.council.coordinator
    outcome = coord.dispatch(
        "FinanceDirector", "approve_payment",
        "Release $25,000 to Dockyard Vendor Ltd (two-vessel maintenance)",
        "Bundled maintenance invoice across MV Serenity and MV Aurora.",
        approver.actor(), evidence=rt.evidence_list())
    print(f"\nGoverned action → '{outcome['outcome'].upper()}'")
    print(f"  Reason: {outcome['reason']}")
    if outcome["outcome"] == "requires_approval":
        did = outcome["decision"]["id"]
        print(f"  Parked in human approval queue as {did}")
        resolved = coord.resolve(did, approver.actor(), True,
                                 "Maintenance verified against contract + ledger; funds available.")
        print(f"  Human ({approver.name}) → {resolved['status'].upper()}: "
              f"{resolved['resolution_reason']}")

    # ---------------------------------------------------------------- Scenario 2
    rule("Scenario 2 · Deterministic denial of an unauthorized payment")
    print(f"{viewer.name} (role: viewer) attempts to approve a $12,000 fuel payment …")
    blocked = coord.dispatch(
        "FinanceDirector", "approve_payment", "Release $12,000 to FuelCo",
        "Attempted by a viewer without authority.", viewer.actor(),
        evidence=rt.evidence_list())
    print(f"\nGoverned action → '{blocked['outcome'].upper()}'")
    print(f"  Reason: {blocked['reason']}")
    assert blocked["outcome"] == "denied", "expected deterministic denial"
    print("  ✓ Blocked and recorded (deterministic denial).")

    # ---------------------------------------------------------------- Audit
    rule("Audit trail (this tenant)")
    for row in rt.policy.audit(rt.tenant_id):
        print(f"  [{row['decision']:<17}] {row['action']:<18} — {row['reason'][:70]}")

    # ---------------------------------------------------------------- Nostr proof
    rule("Nostr workspace bus — every message is a real signed event")
    feed = rt.bus.feed(limit=5)
    from abos.nostr.events import NostrEvent
    for e in feed[:5]:
        ev = NostrEvent(pubkey=e["pubkey"], kind=e["kind"], content=e["content"],
                        tags=e["tags"], created_at=e["created_at"], id=e["id"], sig=e["sig"])
        print(f"  kind {e['kind']:<5} {e['kind_name']:<18} sig✓={ev.verify()} "
              f"pubkey={e['pubkey'][:12]}…")
    print(f"\nTotal signed events on the bus: {len(rt.bus.feed(limit=1000))}")
    rule("Demo complete")


if __name__ == "__main__":
    main()
