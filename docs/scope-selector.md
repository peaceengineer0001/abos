# 📐 The Scope Selector — 9 Levels of Human Organization

One of the core innovations of the Raven Network is that **the same 20-agent stack scales across every level of human organization**. The Peace Protocols recognize that individuals, couples, families, clans, tribes, congregations, businesses, and nations all manage the same 19 domains. Only the *scale of the inputs* and the *nature of the optimization* differ — the framework is identical.

When you first launch, Raven asks: *"Who are we optimizing for?"* Your answer sets the scope, which reshapes every agent's intake questions, index calculation, and system prompt.

---

## The 9 Scope Levels at a Glance

| Level | Size | Pe / CVI Basis | Typical First Focus |
|---|---|---|---|
| **Individual** | 1 | Personal sovereignty metrics | DFR, LRA, EAR |
| **Couple** | 2 | Shared household + aggregated individual | HIS, AFI, Sc |
| **Family** | ~6 | Household + child development | LNR, HIS, KLI |
| **House** | variable | Shared infrastructure | EAR, WSI, CI |
| **Clan** | ~30 | Inter-household resource sharing | LNR, MAF, AFI |
| **Tribe** | ~150 (Dunbar) | Community infrastructure | All 12 realms, SPR |
| **Church Congregation** | variable | Cultural + spiritual + mutual-aid | Sc, CCI, AFI, WAI |
| **Business** | variable | Operational sovereignty | EAR, RPR, AFI, FFR |
| **Nation** | large | Full geopolitical sovereignty | All 19 + λ₂ network metrics |

---

## How Scope Changes Each Agent

Every agent reads the active scope (from a Kind `30104` Scope Configuration event) and adapts three things:

1. **Intake questions** — what data is collected
2. **Index calculation** — how the ratio is computed and over what population
3. **System-prompt tone** — how the agent speaks and what interventions it proposes

The clearest example is **Sol (Energy / EAR)**:

- *Individual EAR:* "Does your home have solar panels? What % of your electricity bill comes from local generation?"
- *Tribe EAR:* "What % of the community's total energy demand is met by locally-owned generation assets?"
- *Nation EAR:* "What % of national energy demand is met by domestically-owned renewable generation?"

The formula `EAR = E_local / E_demand` never changes — only the boundary of what counts as "local" and "demand."

---

## Per-Level Detail & Examples

### 🧍 Individual
A single person optimizing their own life.
- **Focus:** personal finances (DFR), personal resource autonomy (LRA), home energy (EAR).
- **Example:** *"I want to be debt-free in 3 years and grow 25% of my own food."* Ember maps a debt-avalanche plan; Root designs a raised-bed + preservation plan; Raven tracks Pe rising as dependency falls.

### 💑 Couple
Two partners sharing a household.
- **Focus:** shared shelter (HIS), joint finances (AFI), shared purpose (Sc via Starfire).
- **Example:** A couple drafts a shared mission statement (Starfire), consolidates a joint debt-freedom plan (Ember), and evaluates buying vs. renting for housing sovereignty (Haven).

### 👨‍👩‍👧‍👦 Family
A nuclear family, up to ~6, with children.
- **Focus:** local nutrition (LNR), housing (HIS), education (KLI), plus child development.
- **Example:** Root plans a family food forest; Lore builds a home-learning pathway that counts *empowered actors produced*; Cedar schedules elder interviews so cultural knowledge transfers to the kids.

### 🏘️ House
An extended or communal household sharing infrastructure.
- **Focus:** shared energy (EAR), shared water (WSI), shared waste loops (CI).
- **Example:** A co-living house sizes a shared battery bank (Sol), installs greywater recycling (Tide), and starts composting + repair culture (Cycle).

### 🪢 Clan
An extended family network, up to ~30 people across several households.
- **Focus:** inter-household resource sharing (LNR), shared mobility (MAF), pooled finance (AFI).
- **Example:** Households pool a shared vehicle fleet (Passage), coordinate a seasonal harvest exchange (Root), and start a mutual-credit pool (Thrive).

### 🏕️ Tribe
A community or neighborhood around Dunbar's number (~150).
- **Focus:** all 12 realms at community scale, plus governance participation (SPR).
- **Example:** The tribe stands up a community microgrid (Sol), a participatory-budgeting council (Summit + Council), and a shared maker-space (Forge). Raven reports the tribe's aggregate Pe/CVI.

### ⛪ Church Congregation
A religious or spiritual community.
- **Focus:** spiritual coherence (Sc), cultural continuity (CCI), mutual-aid finance (AFI), community health (WAI).
- **Example:** Starfire designs a shared ritual calendar; Thrive sets up a benevolence/mutual-aid fund; Heal organizes a preventive-health cooperative.

### 🏢 Business
An organization or enterprise.
- **Focus:** operational energy (EAR), regenerative production (RPR), finance (AFI), information flow (FFR).
- **Example:** A manufacturer audits supplier dependency (Forge/RPR), moves to on-site solar (Sol/EAR), and adopts self-hosted communication (Mesh/FFR) to protect its information sovereignty.

### 🌐 Nation
A large community or nation-state.
- **Focus:** all 19 domains, plus network-topology metrics — algebraic connectivity **λ₂** and **hub-betweenness** — to measure structural resilience.
- **Example:** A nation models its energy mix (Sol), water security (Tide), food self-sufficiency (Root), and governance legitimacy (Council/JCI), while Raven tracks λ₂ to ensure no single hub failure can fracture the network.

---

## Cross-Scale Federation

A family-level Raven Network can **federate** with a clan-level network and a tribe-level network on the same Nostr relay mesh — aggregating Pe and CVI **upward** while preserving the sovereignty and isolation of each level's raw data.

```
Individual ──► Family ──► Clan ──► Tribe ──► Nation ──► Keystone (7,777)
   (raw)      (aggregate) (aggregate) (aggregate) (aggregate) (anonymized)
```

Rules (enforced by the scope module — see [ARCHITECTURE.md](../ARCHITECTURE.md#5-scope-federation)):
- Raw domain data (Kind 30102) **never** leaves its origin scope without explicit promotion.
- Only aggregate Pe/CVI (Kinds 30100/30101) flow upward.
- Commands never flow downward — a parent scope can read a child's aggregate, never write to it.

This is the Peace Protocols vision of **"7,777 without hierarchy"** implemented in software.

---

## Configuring Your Scope

Scope defaults live in [`config/scope-config.example.toml`](../config/scope-config.example.toml). Copy it to `config/scope-config.toml` (setup does this for you) and edit:

```toml
[scope]
level = "family"          # individual | couple | family | house | clan | tribe | congregation | business | nation
members = 4               # count included in this scope
community_id = "npub1..." # the Buzz Community / relay id for this scope

[federation]
publish_aggregates_to = "clan"   # or "" to stay fully local
privacy_tier = 1                 # 1 = local only (default)
```

Change your scope any time — Raven re-runs the relevant intake questions and recalculates your baseline.
