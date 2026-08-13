# ABOS — Agentic Business Operating System

> A private fork of [peace-protocols](https://github.com/peaceengineer0001/peace-protocols)
> extended with the **BOSS Framework** (Business Operating System Steward).

ABOS turns the Peace Protocols agent + Nostr substrate into a governed,
multi-tenant operating system for running a real business with autonomous agents.
It adds an **11-agent council** organized into four streams — **Govern, Run, Grow,
Decide** — that coordinate over a real Nostr workspace bus, produce auditable
**evidence**, and are gated by a **deterministic multi-tenant policy engine** so
that risky or unauthorized actions are *provably* blocked before they happen.

This repository is **additive**: everything from `peace-protocols` (the Raven
agent prompts, the MCP bus, the math/whitepaper material, the Nostr concepts) is
preserved intact under its original paths. The new code lives entirely under the
`abos/` Python package plus `scripts/` and `tests/`.

---

## Why ABOS

Most "AI business" demos are a single chatbot with tool access and no guardrails.
ABOS is built around three hard requirements that a real operator cares about:

1. **Governance is deterministic, not vibes.** Every consequential action passes
   through a policy engine that returns `ALLOW`, `REQUIRES_APPROVAL`, or `DENY`
   with a machine-readable reason and an audit-log entry. The same input always
   yields the same decision. Denials are not "the model declined" — they are code.
2. **Multi-tenant isolation.** Six very different businesses run side by side.
   No agent in one tenant can see or act on another tenant's data. Isolation is
   enforced in the policy layer, not by prompt etiquette.
3. **Real protocol, not a mock.** Agents talk over a real **Nostr** event bus.
   Every message is a signed Nostr event (NIP-01) with a real secp256k1 /
   BIP-340 Schnorr signature; the workspace uses **NIP-28 public channels**. You
   can point the bus at any external relay.

---

## The BOSS Council (11 agents, 4 streams)

| Stream | Agent | Role |
| ------ | ----- | ---- |
| **Govern** | `ComplianceOfficer` | Regulatory / licensing gap detection, controls |
| **Govern** | `SecuritySteward` | Access, secrets, threat posture |
| **Govern** | `RiskManager` | Risk scoring, high-risk pauses |
| **Run** | `OperationsLead` | Day-to-day execution, SOPs, throughput |
| **Run** | `FinanceController` | Spend, cash, payment authorization |
| **Run** | `PeopleOps` | Staffing, scheduling, HR guardrails |
| **Grow** | `GrowthStrategist` | Pipeline, funnel, LTV:CAC |
| **Grow** | `MarketingLead` | Campaigns, brand, content |
| **Grow** | `ClientSuccess` | Retention, NPS, escalations |
| **Decide** | `Analyst` | Evidence synthesis, scorecards |
| **Decide** | `Coordinator` | Orchestration, decision routing, approvals |

Agents are created through a **Council factory** (`abos.agents.build_council`).
Each agent gets its own real Nostr identity (secp256k1 keypair) and posts to the
workspace channels it is authorized for.

---

## Architecture at a glance

```
                 ┌──────────────────────────────────────────────┐
                 │                 FastAPI API                    │
                 │  /tenants  /agents  /evidence  /decisions  /demo│
                 └───────────────┬───────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                         │
  ┌───────────┐          ┌───────────────┐          ┌──────────────┐
  │  Policy   │          │  Council of 11 │          │   Evidence   │
  │  Engine   │◄────────►│   BOSS agents  │─────────►│   + Scorecard│
  │(determin- │  gates   │ (Govern/Run/   │ produce  │   (7-metric  │
  │ istic)    │          │  Grow/Decide)  │          │    rubric)   │
  └───────────┘          └───────┬────────┘          └──────────────┘
                                 │ signed events
                         ┌───────▼────────┐
                         │  Nostr bus     │
                         │  NIP-28 chans  │  #compliance #ops #finance
                         │  NIP-01 events │  #growth #decisions
                         └────────────────┘
```

See **[ARCHITECTURE_ABOS.md](ARCHITECTURE_ABOS.md)** for the full design. The
original Peace Protocols architecture remains in **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

## Quick start

Requires Python 3.10+.

```bash
# 1. Install dependencies
pip install -r requirements.txt
#    (coincurve is optional but strongly recommended — it makes Nostr signing
#     ~500x faster. A pure-python BIP-340 fallback is used if it is absent.)

# 2. Seed the six demo businesses (writes demo_state.json)
python3 scripts/seed_demo.py

# 3. Run the scripted BOSS demo (two governance scenarios)
python3 scripts/run-boss-demo.py

# 4. Start the API
uvicorn abos.api.main:app --reload
#    -> http://127.0.0.1:8000/docs   (interactive OpenAPI)
```

On startup the API auto-seeds from `demo_state.json` if present, otherwise it
seeds fresh in-memory.

---

## The demo

`scripts/run-boss-demo.py` runs two deterministic governance scenarios end to end:

1. **Two-vessel review pauses the high-risk job.** The marine-services tenant
   submits two vessel jobs. The RiskManager + ComplianceOfficer score both; the
   high-risk vessel (missing documentation) is routed to `REQUIRES_APPROVAL` and
   paused, while the low-risk one proceeds. Every step is a signed Nostr event.
2. **Unauthorized payment is blocked.** A `viewer`-role actor attempts to
   authorize a large payment. The policy engine returns `DENY` with an explicit
   reason and writes an audit entry. The FinanceController never executes it.

Both outcomes are produced by code, not by model discretion, so they are
identical on every run.

---

## Six business templates

Deterministic, fully-seeded demo tenants live in `abos/templates/`:

| Template | Business type |
| -------- | ------------- |
| `saas_startup` | B2B SaaS startup |
| `boutique_agency` | Creative / marketing agency |
| `marine_services` | Marine vessel services (USCG-regulated) |
| `restaurant_group` | Multi-location restaurant group |
| `retail_brand` | DTC retail brand |
| `professional_services` | Licensed professional services firm |

Each template carries its own role map, scorecard rubric, and seed scenario.

---

## API surface

All routes are served under the `/api` prefix.

| Method | Path | Purpose |
| ------ | ---- | ------- |
| `GET` | `/api/health` | Liveness |
| `POST` | `/api/demo/seed` | Seed / reseed all six demo tenants |
| `POST` | `/api/demo/seed/{business_type}` | Seed a single business type |
| `POST` | `/api/demo/reset` | Reset the in-memory store |
| `GET` | `/api/templates` | List available business templates |
| `GET` | `/api/tenants` | List tenants |
| `GET` | `/api/tenants/{tenant_id}` | Tenant detail |
| `GET` | `/api/tenants/{tenant_id}/users` | Users / roles for a tenant |
| `POST` | `/api/tenants/{tenant_id}/run-council` | Run the 11-agent council |
| `GET` | `/api/tenants/{tenant_id}/workspace` | Nostr workspace feed |
| `GET` | `/api/agents` | Council roster / agent catalog |
| `GET` | `/api/scorecard/{tenant_id}` | 7-metric scorecard |
| `GET` | `/api/evidence` | Evidence across tenants |
| `GET` | `/api/evidence/{tenant_id}` | Evidence log for a tenant |
| `GET` | `/api/audit/{tenant_id}` | Policy audit log |
| `GET` | `/api/decisions` | List decisions |
| `POST` | `/api/decisions/dispatch` | Submit an action for governance |
| `POST` | `/api/decisions/{decision_id}/approve` | Approve a pending decision |
| `POST` | `/api/decisions/{decision_id}/deny` | Deny a pending decision |

Role-gated actions return **HTTP 403** with a policy reason when the caller's
role is insufficient (e.g. a `viewer` attempting a payment authorization).

---

## Nostr layer

The `abos/nostr/` package is a self-contained, dependency-light Nostr
implementation:

- `crypto.py` — secp256k1 keypairs + BIP-340 Schnorr signatures. Uses
  `coincurve` when available, with a correct pure-python fallback. Both backends
  are wire-compatible.
- `events.py` — NIP-01 event construction, IDs, and signing. Custom BOSS kinds
  `31000–31009` plus NIP-28 kinds `40/41/42`.
- `relay.py` — an in-process `LocalRelay` for demos/tests and a `WebsocketRelay`
  for talking to real external relays.
- `channels.py` — the `WorkspaceBus`: five NIP-28 public channels
  (`#compliance`, `#ops`, `#finance`, `#growth`, `#decisions`).

---

## Tests

```bash
python3 tests/test_boss_checks.py
```

Covers keypair generation, cross-backend signature compatibility, deterministic
policy denial, multi-tenant isolation, evidence production, scorecard scoring,
and template loading.

---

## Repository layout (new code)

```
abos/
  tenant.py          TenantRuntime + TenantStore
  demo.py            deterministic seed scenarios for 6 businesses
  core/
    agent.py         BossAgent base + AgentIdentity
    policy.py        PolicyEngine (deterministic ALLOW/APPROVAL/DENY + audit)
    evidence.py      evidence records
    scorecard.py     7-metric rubric
    approval.py      ApprovalQueue + GovernedDecision
  agents/
    govern/ run/ grow/ decide/   the 11 BOSS agents + Council factory
  nostr/             crypto, events, relay, channels
  templates/         6 business YAMLs + loader
  api/               FastAPI app, models, state, routes/
scripts/
  seed_demo.py       writes demo_state.json
  run-boss-demo.py   scripted two-scenario demo
tests/
  test_boss_checks.py
```

---

## Relationship to peace-protocols

ABOS is a **private downstream fork**. It does not modify or remove any upstream
Peace Protocols material; it layers the BOSS Framework on top. If upstream
changes, this fork can rebase and keep the `abos/` package unchanged.

## License

Inherits the upstream license (see [LICENSE](LICENSE)). Private repository —
not for public distribution.
