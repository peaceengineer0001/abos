"""
abos.demo
=========

Deterministic demo dataset for the six business models. This is the single
source of truth used by ``scripts/seed_demo.py`` (which writes
``demo_state.json`` for the web app) and by the API autoseed. Every scenario
seeds realistic dummy tenants, users, evidence, an analysis pass, a mix of
pending approvals + resolved decisions, risk flags, and a financial summary.

Nothing here is production data — it is safe, synthetic pitch material.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .core.evidence import Evidence, EvidenceType
from .tenant import TenantStore, TenantRuntime


# --------------------------------------------------------------------------- #
# Scenario definitions (deterministic — fixed tenant ids)
# --------------------------------------------------------------------------- #
SCENARIOS: List[Dict[str, Any]] = [
    {
        "tenant_id": "tnt_marine",
        "name": "Blue Horizon Marine Services",
        "business_type": "marine_services",
        "users": [
            ("Larry Braden", "admin"),
            ("Dana Ops", "operator"),
            ("Priya Approver", "approver"),
            ("Sam Viewer", "viewer"),
        ],
        "evidence": [
            ("contract", "Charter Agreement — MV Serenity", True),
            ("compliance_filing", "USCG vessel documentation — MV Serenity", True),
            ("compliance_filing", "State registration renewal — MV Aurora", False),
            ("financial_record", "Q2 fuel & maintenance ledger", True),
            ("counterparty_data", "Dockyard Vendor Ltd — insurance cert", False),
        ],
        "context": {
            "exposure_usd": 68000, "counterparties": ["Dockyard Vendor Ltd", "FuelCo"],
            "cash_on_hand": 210000, "monthly_burn": 55000, "accounts_receivable": 90000,
            "accounts_payable": 47000, "open_tasks": 18, "overdue_tasks": 3,
            "completed_tasks": 52, "sla_target_pct": 95,
            "required_filings": ["USCG vessel documentation", "State registration renewal",
                                 "Charter operating permit", "Insurance certificate"],
            "nps": 41, "headcount": 22, "open_roles": 3, "utilization_pct": 82,
            "accounts": [{"name": "Regatta Partners", "health": "red", "renewal_days": 28},
                         {"name": "Coastal Escapes", "health": "green", "renewal_days": 120}],
            "pending_access_requests": 1,
        },
        "governed_actions": [
            {"action": "approve_payment", "proposer": "FinanceDirector",
             "title": "Release $25,000 to Dockyard Vendor Ltd",
             "summary": "Two-vessel maintenance invoice.",
             "actor_role": "approver", "resolve": None},
            {"action": "file_compliance", "proposer": "ComplianceOfficer",
             "title": "File State registration renewal — MV Aurora",
             "summary": "Renewal due in 14 days; filing evidence unverified.",
             "actor_role": "approver", "resolve": None},
            {"action": "approve_payment", "proposer": "FinanceDirector",
             "title": "Unauthorized fuel payment attempt",
             "summary": "Viewer attempted to release funds without authority/evidence.",
             "actor_role": "viewer", "resolve": None},
        ],
    },
    {
        "tenant_id": "tnt_saas",
        "name": "Northwind SaaS",
        "business_type": "saas_startup",
        "users": [("Ravi Founder", "admin"), ("Ops Lead", "operator"),
                  ("Finance Head", "approver"), ("Analyst", "viewer")],
        "evidence": [
            ("financial_record", "March MRR cohort report", True),
            ("metric_feed", "Product usage telemetry (30d)", True),
            ("contract", "Enterprise MSA — Acme Corp", True),
            ("contract", "Renewal draft — Globex", False),
        ],
        "context": {
            "exposure_usd": 30000, "counterparties": ["Acme Corp"],
            "cash_on_hand": 480000, "monthly_burn": 95000, "accounts_receivable": 120000,
            "accounts_payable": 40000, "open_tasks": 34, "overdue_tasks": 5,
            "completed_tasks": 120, "sla_target_pct": 90,
            "required_filings": ["Delaware franchise tax", "SOC2 Type I readiness"],
            "marketing_spend": 45000, "leads_generated": 220, "mql_to_sql_pct": 22,
            "target_cac": 900,
            "pipeline": [{"value": 180000, "prob": 0.6, "stage": "negotiation", "days_in_stage": 20},
                         {"value": 90000, "prob": 0.3, "stage": "qualified", "days_in_stage": 55}],
            "pipeline_target": 300000, "nps": 52, "headcount": 28, "open_roles": 6,
            "utilization_pct": 88,
            "accounts": [{"name": "Globex", "health": "at_risk", "renewal_days": 45}],
        },
        "governed_actions": [
            {"action": "sign_contract", "proposer": "GrowthDirector",
             "title": "Countersign Enterprise MSA — Acme Corp",
             "summary": "$180k ARR; legal reviewed.", "actor_role": "approver", "resolve": True},
            {"action": "send_external_message", "proposer": "MarketingDirector",
             "title": "Send win-back campaign to churned cohort",
             "summary": "3,400 recipients.", "actor_role": "operator", "resolve": None},
        ],
    },
    {
        "tenant_id": "tnt_agency",
        "name": "Meridian Boutique Agency",
        "business_type": "boutique_agency",
        "users": [("Owner", "admin"), ("PM", "operator"), ("Controller", "approver")],
        "evidence": [
            ("contract", "Retainer — Lighthouse Brands", True),
            ("project_status", "Q3 delivery tracker", True),
            ("communication", "Client escalation thread — Nimbus", False),
        ],
        "context": {
            "exposure_usd": 15000, "cash_on_hand": 130000, "monthly_burn": 60000,
            "accounts_receivable": 85000, "accounts_payable": 22000,
            "open_tasks": 27, "overdue_tasks": 6, "completed_tasks": 70, "sla_target_pct": 88,
            "required_filings": ["Business license renewal", "Contractor 1099 filings"],
            "nps": 48, "headcount": 14, "open_roles": 2, "utilization_pct": 79,
            "accounts": [{"name": "Nimbus", "health": "red", "renewal_days": 35},
                         {"name": "Lighthouse Brands", "health": "green", "renewal_days": 200}],
        },
        "governed_actions": [
            {"action": "sign_contract", "proposer": "GrowthDirector",
             "title": "Execute retainer renewal — Lighthouse Brands",
             "summary": "12-month, $18k/mo.", "actor_role": "approver", "resolve": None},
        ],
    },
    {
        "tenant_id": "tnt_restaurant",
        "name": "Copper Table Restaurant Group",
        "business_type": "restaurant_group",
        "users": [("GM", "admin"), ("Shift Lead", "operator"), ("CFO", "approver")],
        "evidence": [
            ("compliance_filing", "Health department permit — Downtown", True),
            ("compliance_filing", "Liquor license renewal — Riverside", False),
            ("financial_record", "Weekly food cost report", True),
        ],
        "context": {
            "exposure_usd": 12000, "cash_on_hand": 95000, "monthly_burn": 70000,
            "accounts_receivable": 15000, "accounts_payable": 38000,
            "open_tasks": 22, "overdue_tasks": 4, "completed_tasks": 88, "sla_target_pct": 90,
            "required_filings": ["Health department permits", "Liquor license renewal",
                                 "Food handler certifications"],
            "nps": 39, "headcount": 60, "open_roles": 8, "utilization_pct": 91,
            "accounts": [],
        },
        "governed_actions": [
            {"action": "file_compliance", "proposer": "ComplianceOfficer",
             "title": "File liquor license renewal — Riverside",
             "summary": "Expires in 10 days; filing not yet verified.",
             "actor_role": "approver", "resolve": None},
        ],
    },
    {
        "tenant_id": "tnt_retail",
        "name": "Harbor & Pine Retail",
        "business_type": "retail_brand",
        "users": [("CEO", "admin"), ("Merch Ops", "operator"), ("Finance", "approver")],
        "evidence": [
            ("metric_feed", "POS daily sales feed", True),
            ("financial_record", "Inventory valuation report", True),
            ("contract", "Supplier terms — Cotton Mills Co", False),
        ],
        "context": {
            "exposure_usd": 42000, "counterparties": ["Cotton Mills Co"],
            "cash_on_hand": 260000, "monthly_burn": 150000, "accounts_receivable": 60000,
            "accounts_payable": 110000, "open_tasks": 19, "overdue_tasks": 2,
            "completed_tasks": 64, "sla_target_pct": 93,
            "required_filings": ["Sales tax filings", "Reseller permits"],
            "marketing_spend": 60000, "leads_generated": 400, "mql_to_sql_pct": 18,
            "target_cac": 40,
            "pipeline": [{"value": 120000, "prob": 0.5, "stage": "wholesale", "days_in_stage": 30}],
            "pipeline_target": 200000, "nps": 44, "headcount": 35, "open_roles": 4,
            "utilization_pct": 76, "accounts": [],
        },
        "governed_actions": [
            {"action": "approve_payment", "proposer": "FinanceDirector",
             "title": "Pay supplier — Cotton Mills Co ($40k)",
             "summary": "Supplier terms contract still unverified.",
             "actor_role": "approver", "resolve": False},
        ],
    },
    {
        "tenant_id": "tnt_prof",
        "name": "Cedar & Stone Advisory",
        "business_type": "professional_services",
        "users": [("Managing Partner", "admin"), ("Associate", "operator"),
                  ("Billing Partner", "approver")],
        "evidence": [
            ("contract", "Engagement letter — Matter 2041", True),
            ("compliance_filing", "Trust account reconciliation — March", True),
            ("counterparty_data", "Conflict check — Opposing Co", True),
            ("financial_record", "WIP & billing milestones", True),
        ],
        "context": {
            "exposure_usd": 25000, "counterparties": ["Opposing Co"],
            "cash_on_hand": 340000, "monthly_burn": 120000, "accounts_receivable": 210000,
            "accounts_payable": 35000, "open_tasks": 40, "overdue_tasks": 3,
            "completed_tasks": 150, "sla_target_pct": 95,
            "required_filings": ["Professional liability insurance", "Bar/CPA compliance filings",
                                 "Trust account reconciliation"],
            "nps": 58, "headcount": 45, "open_roles": 2, "utilization_pct": 84,
            "accounts": [{"name": "Matter 2041 Client", "health": "green", "renewal_days": 90}],
        },
        "governed_actions": [
            {"action": "approve_payment", "proposer": "FinanceDirector",
             "title": "Release milestone billing — Matter 2041 ($60k)",
             "summary": "Contract + financials verified; conflict check clear.",
             "actor_role": "approver", "resolve": True},
        ],
    },
]


def _seed_tenant(store: TenantStore, scn: Dict[str, Any]) -> TenantRuntime:
    rt = store.create_tenant(scn["name"], scn["business_type"], tenant_id=scn["tenant_id"])

    users_by_role: Dict[str, Any] = {}
    for name, role in scn["users"]:
        u = rt.add_user(name, role)
        users_by_role.setdefault(role, u)

    for etype, title, verified in scn["evidence"]:
        rt.add_evidence(Evidence(rt.tenant_id, etype, title, verified=verified, source="seed"))

    # Run the council once to produce analysis + scorecard + risk flags.
    rt.run_council(scn["context"])

    # Dispatch the scripted governed actions through the coordinator.
    coord = rt.council.coordinator
    for ga in scn["governed_actions"]:
        actor = users_by_role.get(ga["actor_role"]) or rt.add_user("Auto", ga["actor_role"])
        outcome = coord.dispatch(
            ga["proposer"], ga["action"], ga["title"], ga["summary"], actor.actor(),
            evidence=rt.evidence_list())
        # Optionally resolve parked decisions to show completed history.
        if outcome.get("outcome") == "requires_approval" and ga.get("resolve") is not None:
            approver = users_by_role.get("approver") or users_by_role.get("admin")
            if approver:
                did = outcome["decision"]["id"]
                if ga["resolve"]:
                    coord.resolve(did, approver.actor(), True,
                                  "Evidence verified and authority confirmed.")
                else:
                    coord.resolve(did, approver.actor(), False,
                                  "Denied: supporting evidence not yet verified.")
    return rt


def seed_store(store: TenantStore | None = None) -> TenantStore:
    """Seed all six business scenarios into a store (creating one if needed)."""
    store = store or TenantStore()
    for scn in SCENARIOS:
        if store.get(scn["tenant_id"]) is None:
            _seed_tenant(store, scn)
    return store


def rehydrate_from_state(store: TenantStore, data: Dict[str, Any]) -> TenantStore:
    """Rebuild live runtimes for the API.

    Seeding is deterministic, so we simply re-run :func:`seed_store`; the live
    state then matches the tenants recorded in ``demo_state.json``.
    """
    return seed_store(store)


def build_demo_state() -> Dict[str, Any]:
    """Seed a fresh store and return its serializable state dict."""
    store = seed_store()
    return store.to_dict()
