"""
BOSS check suite — the six passing BOSS checks referenced in the presenter brief,
plus Nostr crypto and multi-tenant isolation checks.

Run::

    python3 -m pytest tests/test_boss_checks.py -v
    # or without pytest:
    python3 tests/test_boss_checks.py
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abos.nostr import crypto
from abos.nostr.events import build_event, KIND_EVIDENCE
from abos.core.evidence import Evidence, EvidenceType
from abos.core.policy import Actor, Role, Decision
from abos.tenant import TenantStore


# --------------------------------------------------------------------------- #
# BOSS check 1 — real Nostr keypairs + signed events verify
# --------------------------------------------------------------------------- #
def test_nostr_keypair_and_signature():
    sk = crypto.generate_privkey()
    pk = crypto.get_public_key(sk)
    assert len(bytes.fromhex(pk)) == 32
    msg = hashlib.sha256(b"boss").digest()
    sig = crypto.schnorr_sign(msg, sk)
    assert crypto.schnorr_verify(msg, pk, sig)
    assert not crypto.schnorr_verify(hashlib.sha256(b"x").digest(), pk, sig)
    ev = build_event(sk, KIND_EVIDENCE, {"hello": "world"})
    assert ev.verify()
    assert crypto.to_bech32("npub", pk).startswith("npub1")


# --------------------------------------------------------------------------- #
# BOSS check 2 — 11-agent registry across 4 streams
# --------------------------------------------------------------------------- #
def test_council_has_eleven_agents():
    store = TenantStore()
    rt = store.create_tenant("Test Co", "saas_startup")
    assert len(rt.council.agents) == 11
    streams = {a.STREAM for a in rt.council.agents.values()}
    assert streams == {"govern", "run", "grow", "decide"}
    # every agent has a distinct real pubkey
    pubkeys = {a.pubkey for a in rt.council.agents.values()}
    assert len(pubkeys) == 11


# --------------------------------------------------------------------------- #
# BOSS check 3 — tenant-mismatch denial (isolation)
# --------------------------------------------------------------------------- #
def test_tenant_isolation_denial():
    store = TenantStore()
    a = store.create_tenant("Alpha", "saas_startup", tenant_id="tnt_a")
    store.create_tenant("Beta", "boutique_agency", tenant_id="tnt_b")
    intruder = Actor("u1", "tnt_a", Role.ADMIN)
    result = a.policy.evaluate(intruder, "read_workspace", "tnt_b")
    assert result.decision == Decision.DENY
    assert "tenant isolation" in result.reason


# --------------------------------------------------------------------------- #
# BOSS check 4 — role/authority denial (viewer cannot approve payment)
# --------------------------------------------------------------------------- #
def test_authority_denial():
    store = TenantStore()
    rt = store.create_tenant("Gamma", "marine_services", tenant_id="tnt_g")
    viewer = Actor("v1", "tnt_g", Role.VIEWER)
    result = rt.policy.evaluate(viewer, "approve_payment", "tnt_g")
    assert result.decision == Decision.DENY
    assert "insufficient authority" in result.reason


# --------------------------------------------------------------------------- #
# BOSS check 5 — evidence requirement + high-impact approval flag
# --------------------------------------------------------------------------- #
def test_evidence_and_approval_flag():
    store = TenantStore()
    rt = store.create_tenant("Delta", "marine_services", tenant_id="tnt_d")
    approver = Actor("a1", "tnt_d", Role.APPROVER)

    # No evidence -> denied for insufficient evidence.
    denied = rt.policy.evaluate(approver, "approve_payment", "tnt_d", evidence=[])
    assert denied.decision == Decision.DENY
    assert "insufficient evidence" in denied.reason

    # With required evidence -> high-impact requires human approval.
    evidence = [
        Evidence("tnt_d", EvidenceType.CONTRACT.value, "Contract", verified=True),
        Evidence("tnt_d", EvidenceType.FINANCIAL_RECORD.value, "Ledger", verified=True),
    ]
    parked = rt.policy.evaluate(approver, "approve_payment", "tnt_d", evidence=evidence)
    assert parked.decision == Decision.REQUIRES_APPROVAL


# --------------------------------------------------------------------------- #
# BOSS check 6 — evidence-weighted scorecard (7 metrics, graded)
# --------------------------------------------------------------------------- #
def test_scorecard_seven_metrics():
    store = TenantStore()
    rt = store.create_tenant("Epsilon", "restaurant_group", tenant_id="tnt_e")
    rt.add_evidence(Evidence("tnt_e", EvidenceType.FINANCIAL_RECORD.value, "F", verified=True))
    synthesis = rt.run_council({"cash_on_hand": 100000, "monthly_burn": 20000})
    card = synthesis["scorecard"]
    assert len(card["metrics"]) == 7
    assert 0 <= card["score"] <= 100
    assert card["grade"] in {"A", "B", "C", "D", "F"}
    # weights (renormalized) sum to ~1.0
    assert abs(sum(m["weight"] for m in card["metrics"]) - 1.0) < 0.01


# --------------------------------------------------------------------------- #
# Bonus — approval queue authority is enforced on resolution
# --------------------------------------------------------------------------- #
def test_approval_queue_resolution_authority():
    from abos.core.approval import ApprovalError
    store = TenantStore()
    rt = store.create_tenant("Zeta", "professional_services", tenant_id="tnt_z")
    viewer = rt.add_user("V", "viewer")
    approver = rt.add_user("A", "approver")
    rt.add_evidence(Evidence("tnt_z", EvidenceType.CONTRACT.value, "C", verified=True))
    rt.add_evidence(Evidence("tnt_z", EvidenceType.FINANCIAL_RECORD.value, "F", verified=True))
    coord = rt.council.coordinator
    outcome = coord.dispatch("FinanceDirector", "approve_payment", "Pay", "x",
                             approver.actor(), evidence=rt.evidence_list())
    assert outcome["outcome"] == "requires_approval"
    did = outcome["decision"]["id"]
    try:
        coord.resolve(did, viewer.actor(), True, "nope")
        assert False, "viewer must not resolve"
    except ApprovalError:
        pass
    resolved = coord.resolve(did, approver.actor(), True, "ok")
    assert resolved["status"] == "approved"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} BOSS checks passed.")
