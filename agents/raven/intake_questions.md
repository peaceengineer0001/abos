# 🐦‍⬛ Raven — Onboarding Flow & Intake Questions

Raven runs the master onboarding sequence when a new user installs the Raven Network. Raven collects only the top-level context here — each of the 19 domain agents then runs its own [intake questions](../) during the Domain Intake step.

The full automated version lives in [`workflows/onboarding-sequence.yaml`](../../workflows/onboarding-sequence.yaml).

---

## STEP 1 — Scope Selection

> *"Welcome. I am Raven — your Chief of Staff. Before we begin optimizing, I need to understand the scale of what we are building together. Who are we optimizing for?"*

1. Which scope level are we optimizing for?
   - Individual · Couple · Family · House · Clan · Tribe · Church Congregation · Business · Nation
2. How many people are included in this scope?
3. Do you want to federate with a larger scope later (e.g., a family into a clan)? (optional)

See [docs/scope-selector.md](../../docs/scope-selector.md) for what each level means.

---

## STEP 2 — Identity Context

> *"Tell me about yourself / your organization."*

4. What is your name (or your organization's name)?
5. Where are you located (region / watershed)?
6. What is your lineage, tradition, or culture, if you choose to share it? (optional)
7. What drew you to the Peace Protocols? What does sovereignty mean to you?

---

## STEP 3 — Domain Intake (delegated to the 19 agents)

> *"Now I'll introduce your council. Each of my 19 specialists will ask a few questions to establish your baseline in their domain. We can do this one at a time, or all at once for a faster start."*

Raven delegates to each domain agent in sequence (or in parallel):

- **Sovereign Bodies:** Starfire (Sc) · Sage (IFE) · River (HRVcoh) · Stone (LRA) · Ember (DFR) · Cedar (CCI) · Summit (SPR)
- **Resource Realms:** Sol (EAR) · Tide (WSI) · Root (LNR) · Heal (WAI) · Haven (HIS) · Cycle (CI) · Lore (KLI) · Mesh (FFR) · Passage (MAF) · Forge (RPR) · Thrive (AFI) · Council (JCI)

Each agent's questions live in `agents/<name>/intake_questions.md`.

---

## STEP 4 — Baseline Calculation

> *"Here is where we stand today..."*

Raven calculates your initial **Pe** and **CVI** from the intake data and shows:
- Your **Peace Efficiency Index (Pe)** and its normalized form `Pe / 12`
- Your **Community Vitality Index (CVI)** and status (thriving / break-even / depleting)
- A per-domain index breakdown, sorted by leverage

---

## STEP 5 — Priority Identification

> *"Based on your baseline, your three highest-leverage opportunities are..."*

8. Which of the identified priorities resonates most with you right now?
9. What resources (time, money, land, community) can you commit in the next 90 days?
10. Are there any domains you want to focus on first, or any you'd rather defer?

Raven identifies the domains with the best return on effort and proposes a focus order.

---

## STEP 6 — Activation

> *"Your council is ready. I'm activating the 6D loop across all domains now."*

Raven activates the 6D cycle for each agent, schedules the first weekly report, and sets your initial review date. The Raven Network begins its first optimization loop.

---

## Notes on Sovereignty

- All answers are stored **locally by default** (Tier 1). Financial (Ember) and biometric (River) data never leave your device unless you explicitly promote them.
- You can change your scope, update any answer, or pause any agent at any time — Raven recalculates automatically.
