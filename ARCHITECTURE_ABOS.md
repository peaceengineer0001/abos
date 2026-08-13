# ABOS Architecture (BOSS Framework)

This document describes the **BOSS Framework** layer added by ABOS on top of
[peace-protocols](https://github.com/peaceengineer0001/peace-protocols). The
original Peace Protocols architecture is unchanged and documented in
[ARCHITECTURE.md](ARCHITECTURE.md). ABOS is strictly **additive** — all new code
lives under the `abos/` package, `scripts/`, and `tests/`.

---

## 1. Design goals

| Goal | How ABOS satisfies it |
| ---- | --------------------- |
| Governance is deterministic | Policy engine is pure code: same input → same `ALLOW/REQUIRES_APPROVAL/DENY` + reason |
| Multi-tenant isolation | Every action is scoped to a `tenant_id`; cross-tenant access is denied in the policy layer |
| Real protocol substrate | All agent messages are signed Nostr events (NIP-01) over NIP-28 channels |
| Auditability | Every decision writes an evidence record and an audit-log entry |
| Reproducible demos | Six tenants are seeded from deterministic scenarios; no randomness in outcomes |

---

## 2. Component map

```
abos/
├── tenant.py        TenantRuntime (per-business runtime) + TenantStore (registry)
├── demo.py          SCENARIOS for 6 businesses; seed_store / build_demo_state
├── core/
│   ├── agent.py     BossAgent base class, AgentIdentity (Nostr keypair per agent)
│   ├── policy.py    PolicyEngine, Roles, DEFAULT_ACTIONS, audit_log
│   ├── evidence.py  EvidenceRecord, evidence collection
│   ├── scorecard.py 7-metric DEFAULT_RUBRIC + scoring
│   └── approval.py  ApprovalQueue, GovernedDecision
├── agents/
│   ├── govern/  compliance.py security.py risk.py
│   ├── run/     operations.py finance.py people.py
│   ├── grow/    growth.py marketing.py client_success.py
│   ├── decide/  analyst.py coordinator.py
│   └── __init__.py  Council factory: AGENT_CLASSES, STREAMS, build_council
├── nostr/       crypto.py events.py relay.py channels.py
├── templates/   6 YAML business templates + loader
└── api/         FastAPI app + routes
```

---

## 3. The council: 11 agents across 4 streams

The `build_council(tenant)` factory instantiates all eleven agents and wires each
to the workspace bus with its own Nostr identity.

- **Govern** — `ComplianceOfficer`, `SecuritySteward`, `RiskManager`.
  Detect regulatory gaps, enforce security posture, score and pause risk.
- **Run** — `OperationsLead`, `FinanceController`, `PeopleOps`.
  Execute operations, authorize spend, manage staffing.
- **Grow** — `GrowthStrategist`, `MarketingLead`, `ClientSuccess`.
  Drive pipeline, run campaigns, protect retention.
- **Decide** — `Analyst`, `Coordinator`.
  Synthesize evidence and route decisions through governance/approvals.

Each agent subclasses `BossAgent`, declares the actions it can request, the
channels it may post to, and the evidence it produces.

---

## 4. Deterministic policy engine

`abos/core/policy.py` is the heart of BOSS governance.

### Roles

```
viewer     < operator < approver < admin
```

- `viewer` — read only.
- `operator` — can request routine actions.
- `approver` — can approve/deny pending decisions.
- `admin` — full authority within its own tenant.

### Decision model

`PolicyEngine.evaluate(tenant_id, actor_role, action, context)` returns one of:

| Outcome | Meaning |
| ------- | ------- |
| `ALLOW` | Action proceeds immediately |
| `REQUIRES_APPROVAL` | Action is queued for an `approver`/`admin` |
| `DENY` | Action is blocked; reason + audit entry recorded |

Rules that trigger `DENY` or `REQUIRES_APPROVAL` include: insufficient role for
the action, payment amounts above a tenant threshold, actions on a **different**
tenant (cross-tenant denial), and high-risk-scored jobs.

Because the engine is deterministic, the two demo outcomes — *high-risk vessel
paused* and *unauthorized payment blocked* — are identical on every run and are
provable, not probabilistic.

### Audit log

Every non-trivial evaluation appends to `audit_log` with `(timestamp, tenant_id,
actor_role, action, outcome, reason)`. This is the compliance trail.

---

## 5. Multi-tenant isolation

- `TenantStore` holds one `TenantRuntime` per business, keyed by `tenant_id`.
- All API routes and agent actions carry a `tenant_id`.
- The policy engine denies any action whose target tenant differs from the
  actor's tenant. There is no shared mutable state across tenants, so one
  business cannot read or mutate another's evidence, decisions, or workspace.

The six seeded tenants (SaaS startup, boutique agency, marine services,
restaurant group, retail brand, professional services) run concurrently and
independently.

---

## 6. Evidence loop

```
agent action  ─►  PolicyEngine.evaluate  ─►  outcome
      │                                          │
      ▼                                          ▼
 EvidenceRecord  ◄──────────────────────  audit_log entry
      │
      ▼
 Scorecard (7-metric rubric)  ─►  Analyst synthesis  ─►  Coordinator routing
```

1. An agent requests an action.
2. The policy engine evaluates it and records the outcome.
3. An `EvidenceRecord` captures inputs, outcome, and reason.
4. The scorecard scores the tenant across seven metrics.
5. The `Analyst` synthesizes evidence; the `Coordinator` routes decisions and
   drives the approval queue.

---

## 7. Nostr workspace bus

ABOS uses a real Nostr implementation (`abos/nostr/`) rather than a mock queue.

- **crypto.py** — secp256k1 keypairs and BIP-340 Schnorr signatures. A
  `coincurve` fast backend is used when installed (~500x faster); a correct
  pure-python fallback is used otherwise. Both are wire-compatible, verified by
  cross-backend signature tests.
- **events.py** — NIP-01 event serialization, IDs (SHA-256 of the canonical
  array), and signing. Custom BOSS event kinds `31000–31009` for agent
  telemetry, plus NIP-28 kinds `40` (channel create), `41` (metadata), `42`
  (message).
- **relay.py** — `LocalRelay` runs in-process for demos and tests;
  `WebsocketRelay` connects to any external relay so the same events can flow to
  real infrastructure.
- **channels.py** — the `WorkspaceBus` exposes five NIP-28 public channels:
  `#compliance`, `#ops`, `#finance`, `#growth`, `#decisions`. Agents post to the
  channels their stream owns.

Every message an agent emits is a signed event; the demo verifies each signature
before accepting it, proving the bus carries authentic protocol traffic.

---

## 8. API layer

`abos/api/main.py` builds the FastAPI app (open CORS for the demo), includes the
routers under `abos/api/routes/`, and auto-seeds on startup from
`demo_state.json` when present. `abos/api/state.py` holds a singleton store
(`get_store` / `reset_store`). Routes cover tenants, agents, evidence, decisions,
and demo control. Role-insufficient calls return HTTP 403 with the policy reason.

---

## 9. Relationship to peace-protocols

ABOS never edits upstream files. The Raven agent prompts, MCP bus, math and
whitepaper material, and the original Nostr concept docs remain in place. The
BOSS Framework consumes those concepts and realizes them as running,
governed, multi-tenant Python. This keeps the fork rebaseable against upstream.
