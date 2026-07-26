# ♻️ The 6D Solution-Focused Framework

Every agent — all 19 specialists and Raven — operates on the **6D recursive loop**. This is the operational heartbeat of the Raven Network and the software implementation of the whitepaper's Abundance Equilibrium (Theorem 1): each turn of the loop raises a domain's regenerative growth rate (αᵢ) while keeping the community responsive (λ > 0).

```
┌─────────────────────────────────────────────────────────┐
│                     THE 6D LOOP                          │
│                                                          │
│   DISCOVER → DECIPHER → DESIGN → DEVELOP → DEPLOY        │
│       ↑                                        ↓         │
│       └──────────────── DEFEND ─────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

The loop is **recursive**: DEFEND feeds fresh data back into DISCOVER, so each cycle starts from an updated baseline and each domain's index compounds upward over time.

Each phase is emitted as a Kind `30103` (6D Loop State) event, so the current phase of every agent is always visible in its Canvas and auditable in the relay log.

---

## D1 — DISCOVER · *What is the current state?*

The agent collects raw data for its domain.

- Runs its guided intake questions (`agents/<name>/intake_questions.md`).
- Connects to available data sources (wearables, financial apps, meters, local records).
- Establishes a baseline measurement for its index.
- Posts findings to its channel Canvas.

**Examples:**
- **Sol (EAR):** logs annual kWh consumed and kWh generated locally (rooftop solar, microgrid share).
- **Ember (DFR):** gathers total income and total debt across all obligations.
- **River (HRVcoh):** optionally connects an HRV wearable; otherwise collects self-reported stress and regulation habits.

---

## D2 — DECIPHER · *What does the data mean?*

The agent turns raw data into an index and insight.

- Calculates its Peace Protocol index (EAR, DFR, HRVcoh, …) using the [`math/`](../math/) calculators.
- Identifies the gap between current state and the sovereignty target.
- Maps interdependencies with other domains (routed to Raven for cross-agent synthesis).
- Locates the leverage point — the "fuel barge": the single biggest dependency in this domain.

**Examples:**
- **Sol:** `EAR = 4,200 / 10,000 = 0.42`. Fuel barge: no battery storage means zero night-time autonomy.
- **Ember:** `DFR = 1 − (48,000 / 60,000) = 0.20`. Highest-interest chain is a 24% credit card — the leverage point.
- **Root (LNR):** 12% of calories are local; the leverage point is winter storage, not summer growing.

---

## D3 — DESIGN · *What is the optimal path forward?*

The agent designs a sovereignty optimization plan.

- Scopes the plan to the user's level (individual → nation) and available resources.
- Specifies measurable milestones and timelines.
- Routes cross-domain implications to affected agents via Raven.

**Examples:**
- **Sol:** a 3-phase plan — (1) add 10 kWh storage, (2) expand array by 3 kW, (3) join community microgrid — targeting EAR 0.42 → 0.85 in 18 months.
- **Ember:** a debt-avalanche schedule eliminating the 24% card first, freeing $380/mo of "sovereignty leakage."
- **Cedar (CCI):** an elder-interview series to transfer 3 at-risk knowledge sets before winter.

---

## D4 — DEVELOP · *What specific tools and steps will we build?*

The agent builds the concrete implementation assets.

- Creates action items, templates, checklists, and calculators.
- Integrates relevant Peace Engineers technology pathways.
- Builds Buzz Workflows for automated tracking and reminders.

**Examples:**
- **Sol:** a battery-sizing worksheet, three installer quotes, and a Workflow that logs monthly generation vs. demand.
- **Ember:** a month-by-month payment schedule and a Workflow that alerts on any new debt obligation.
- **Root:** a planting calendar, a preservation checklist, and a CSA sign-up link.

---

## D5 — DEPLOY · *Execute the plan.*

The agent puts the plan into action.

- Posts the plan and resources to its dedicated channel.
- Activates Buzz Workflows (reminders, check-ins, milestone tracking).
- Raven coordinates cross-domain deployments to maximize **coherence shocks** (aligned wins that raise CVI).
- The user confirms deployment and sets the first review date.

**Examples:**
- **Sol:** storage installed; Workflow now logs generation nightly.
- **Ember:** avalanche payments automated; DFR tracker live in `#ember-economic`.
- **Raven:** schedules a community "first debt-free member" celebration — a deliberate coherence shock (Kind 30105).

---

## D6 — DEFEND · *Protect the sovereignty gains.*

The agent guards what was won and restarts the loop.

- Monitors the index continuously (or at set intervals).
- Alerts if the index regresses (sovereignty is being eroded).
- Identifies external shocks and designs counter-responses.
- Feeds results back into **D1 (Discover)** with updated data.
- Raven synthesizes all 19 domain defenses into a unified sovereignty posture.

**Examples:**
- **Sol:** alerts if generation drops (panel soiling, inverter fault) so EAR doesn't silently decay.
- **Ember:** flags any new borrowing that would reverse the DFR trend.
- **Raven:** rolls all 19 DEFEND signals into the weekly Pe/CVI report (see [`workflows/weekly-pe-cvi-report.yaml`](../workflows/weekly-pe-cvi-report.yaml)).

---

## Why the Loop Converges on Abundance

The Peace Protocols prove (Theorem 1) that if every realm has positive regenerative growth (αᵢ > 0) and community vitality responds to sovereignty gains (λ > 0), the **Abundance Equilibrium** (all sovereignty scores → 1) is the unique global attractor.

The 6D loop is exactly the mechanism that maintains those two conditions:
- **DESIGN + DEVELOP + DEPLOY** raise αᵢ (regenerative interventions actually get built).
- **DEPLOY's coherence shocks** keep λ > 0 (the community keeps rewarding sovereignty gains).
- **DEFEND + DISCOVER** ensure the system never drifts out of the basin of attraction.

Run the loop, defend the gains, repeat. That is how peace gets engineered — one measured cycle at a time.

---

## The 6D Workflows

Each phase can be triggered as a Buzz Workflow:

| Phase | Workflow |
|---|---|
| Discover | [`workflows/6d-discover.yaml`](../workflows/6d-discover.yaml) |
| Defend / monitoring | [`workflows/6d-defend.yaml`](../workflows/6d-defend.yaml) |
| Weekly synthesis | [`workflows/weekly-pe-cvi-report.yaml`](../workflows/weekly-pe-cvi-report.yaml) |
| Coherence shock | [`workflows/coherence-shock-event.yaml`](../workflows/coherence-shock-event.yaml) |
| Onboarding (full loop kickoff) | [`workflows/onboarding-sequence.yaml`](../workflows/onboarding-sequence.yaml) |
