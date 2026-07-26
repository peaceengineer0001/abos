# 🤖 AGENTS — The Complete Guide to the Raven Council

The Raven Network deploys exactly **20 agents** as a pre-configured Buzz Team called **"The Raven Council"**: **Raven** (the orchestrator) plus **19 domain specialists** (7 Sovereign Bodies + 12 Resource Realms).

Each agent is a Buzz agent persona with:
- a **secp256k1 keypair** and an **NIP-05 handle** (e.g. `starfire@your-relay.domain`)
- a **system prompt** encoding its Peace Protocol mandate (see [`agents/<name>/system_prompt.md`](agents/))
- a **guided intake question set** (see [`agents/<name>/intake_questions.md`](agents/))
- a **config file** (see [`agents/<name>/config.toml`](agents/))
- a **dedicated channel** in the Raven Network workspace
- a **Peace Protocol index** it is responsible for measuring and optimizing

---

## 🔌 How Agents Connect (MCP)

Every agent connects to your Raven Network relay through the **Model Context Protocol (MCP)** — identical to any Buzz agent. The general connection recipe is the same for all 20 agents; only the `--agent` name, channel, and keypair differ.

### General MCP Connection Steps

```bash
# 1. Ensure your local Buzz relay is running
./scripts/launch-raven.sh          # starts buzz-relay on ws://localhost:4736

# 2. Register the agent's MCP server (reads agents/<name>/config.toml)
buzz mcp add \
  --name <agent-name> \
  --config agents/<agent-name>/config.toml \
  --relay ws://localhost:4736

# 3. Verify the agent joined its channel
buzz agent status <agent-name>
```

Each agent's `config.toml` declares its `model`, `channel`, `index_formula`, `privacy_tier`, and MCP endpoint. The default LLM provider is **Ollama** (local) — see [`config/llm-providers.example.toml`](config/llm-providers.example.toml).

### MCP config block (shared shape)

```toml
[mcp]
transport = "stdio"            # or "sse" for remote agents
endpoint   = "ws://localhost:4736"
auth       = "nip42"           # relay authentication
```

> **Sovereignty note:** By default all 20 agents run against a relay on `localhost`. No agent transmits data off-device unless you raise its `privacy_tier` (see [`config/privacy-tiers.example.toml`](config/privacy-tiers.example.toml)).

---

## 🐦‍⬛ Agent 20 — RAVEN (Master Orchestrator)

- **Domain:** Chief of Staff / Master Orchestrator
- **Index formula:** `Pe = Σ (Rᵢ / Dᵢ)` for i = 1..12  **and**  `CVI = (H + Dg + F) / (S + Db + De)`
- **Channel:** `#raven-command`
- **Mission:** Onboard users, coordinate the 19 domain agents, run the 6D loop across all domains, calculate and report the master metrics (Pe + CVI), synthesize cross-domain leverage, and engineer coherence shocks that keep the community inside the basin of the Abundance Equilibrium.
- **MCP connection:**
  ```bash
  buzz mcp add --name raven --config agents/raven/config.toml --relay ws://localhost:4736
  ```
- Full prompt: [`agents/raven/system_prompt.md`](agents/raven/system_prompt.md) · Onboarding: [`agents/raven/intake_questions.md`](agents/raven/intake_questions.md)

---

## 🫀 The 7 Sovereign Bodies (Inner Sovereignty)

### Agent 1 — ✨ STARFIRE (Spiritual Body)
- **Domain:** Coherence with Source
- **Index:** Spiritual Coherence Index — `Sc = phase alignment of individual purpose around shared mission (θ_coh)`
- **Channel:** `#starfire-spiritual`
- **Mission:** Hold the flame of purpose and measure the coherence between who you say you are and how you actually live.
- **MCP:** `buzz mcp add --name starfire --config agents/starfire/config.toml --relay ws://localhost:4736`

### Agent 2 — 🦉 SAGE (Mental Body)
- **Domain:** Systems Literacy
- **Index:** Information Flow Efficiency — `IFE = knowledge_applied / knowledge_consumed`
- **Channel:** `#sage-mental`
- **Mission:** Measure not how much you know, but how much of what you know you actually use.
- **MCP:** `buzz mcp add --name sage --config agents/sage/config.toml --relay ws://localhost:4736`

### Agent 3 — 🌊 RIVER (Emotional Body)
- **Domain:** Heart Coherence
- **Index:** HRV Coherence — `HRVcoh = coherence ratio of heart-rate variability spectrum`
- **Channel:** `#river-emotional`
- **Mission:** Measure the physiological signature of a resilient, balanced nervous system and build shock-resistant emotional infrastructure.
- **MCP:** `buzz mcp add --name river --config agents/river/config.toml --relay ws://localhost:4736`

### Agent 4 — 🪨 STONE (Physical Body)
- **Domain:** Resource Security
- **Index:** Local Resource Autonomy — `LRA = vital_resources_met_locally / total_vital_resources`
- **Channel:** `#stone-physical`
- **Mission:** Measure how much of what your body needs is met by sources you control.
- **MCP:** `buzz mcp add --name stone --config agents/stone/config.toml --relay ws://localhost:4736`

### Agent 5 — 🔥 EMBER (Economic Body)
- **Domain:** Freedom from Debt
- **Index:** Debt Freedom Ratio — `DFR = 1 − (Debt / Income)`
- **Channel:** `#ember-economic`
- **Mission:** Keep the economic fire burning from within, not borrowed from without. Map the path to debt freedom.
- **MCP:** `buzz mcp add --name ember --config agents/ember/config.toml --relay ws://localhost:4736`

### Agent 6 — 🌲 CEDAR (Cultural Body)
- **Domain:** Identity and Story
- **Index:** Cultural Continuity Index — `CCI = (traditions_preserved + innovations_adopted) / total_cultural_assets`
- **Channel:** `#cedar-cultural`
- **Mission:** Hold the living record of who you are — stories, language, ceremonies, lineage — and strengthen what is at risk.
- **MCP:** `buzz mcp add --name cedar --config agents/cedar/config.toml --relay ws://localhost:4736`

### Agent 7 — ⛰️ SUMMIT (Political Body)
- **Domain:** Decentralized Governance
- **Index:** Sovereignty Participation Ratio — `SPR = members_actively_self_governing / total_members`
- **Channel:** `#summit-political`
- **Mission:** Measure and raise your active participation in governing yourself and your community.
- **MCP:** `buzz mcp add --name summit --config agents/summit/config.toml --relay ws://localhost:4736`

---

## 🌍 The 12 Resource Realms (Outer Sovereignty)

### Agent 8 — ☀️ SOL (Energy Realm)
- **Index:** Energy Autonomy Ratio — `EAR = E_local / E_demand`
- **Channel:** `#sol-energy`
- **Mission:** Energy is the upstream dependency. Raise your EAR toward 1 so you are no longer a load in someone else's circuit.
- **MCP:** `buzz mcp add --name sol --config agents/sol/config.toml --relay ws://localhost:4736`

### Agent 9 — 💧 TIDE (Water Realm)
- **Index:** Water Sovereignty Index — `WSI = W_regen / W_consumed`
- **Channel:** `#tide-water`
- **Mission:** Close the water loop with harvesting, greywater recycling, and atmospheric water generation.
- **MCP:** `buzz mcp add --name tide --config agents/tide/config.toml --relay ws://localhost:4736`

### Agent 10 — 🌱 ROOT (Food Realm)
- **Index:** Local Nutrition Ratio — `LNR = Food_local / Food_total`
- **Channel:** `#root-food`
- **Mission:** Feed yourself from the land you inhabit; a high LNR resists supply shocks and reinforces cultural identity.
- **MCP:** `buzz mcp add --name root --config agents/root/config.toml --relay ws://localhost:4736`

### Agent 11 — ❤️‍🩹 HEAL (Health Realm)
- **Index:** Wellness Autonomy Index — `WAI = (Preventive + Regenerative care) / Total care`
- **Channel:** `#heal-health`
- **Mission:** Orient toward prevention, nutrition, and community-scale health infrastructure over pharmaceutical dependency.
- **MCP:** `buzz mcp add --name heal --config agents/heal/config.toml --relay ws://localhost:4736`

### Agent 12 — 🏠 HAVEN (Shelter Realm)
- **Index:** Housing Independence Score — `HIS = Regen_units / Total_housing`
- **Channel:** `#haven-shelter`
- **Mission:** Break the cycle of rent extraction with resource-sovereign, regenerative shelter.
- **MCP:** `buzz mcp add --name haven --config agents/haven/config.toml --relay ws://localhost:4736`

### Agent 13 — 🔄 CYCLE (Waste Realm)
- **Index:** Circularity Index — `CI = Reused / Discarded`
- **Channel:** `#cycle-waste`
- **Mission:** There is no "away." Convert former liabilities into local regenerative output — waste becomes wealth.
- **MCP:** `buzz mcp add --name cycle --config agents/cycle/config.toml --relay ws://localhost:4736`

### Agent 14 — 📚 LORE (Education Realm)
- **Index:** Knowledge Liberation Index — `KLI = critical_thinkers / learners`
- **Channel:** `#lore-education`
- **Mission:** Measure empowered actors produced, not credentials earned. Turn knowledge into sovereign action.
- **MCP:** `buzz mcp add --name lore --config agents/lore/config.toml --relay ws://localhost:4736`

### Agent 15 — 🕸️ MESH (Communication Realm)
- **Index:** Freedom of Flow Ratio — `FFR = unrestricted_info / total_info`
- **Channel:** `#mesh-communication`
- **Mission:** Defend your community's narrative from capture with decentralized, Nostr-native, self-hosted communication.
- **MCP:** `buzz mcp add --name mesh --config agents/mesh/config.toml --relay ws://localhost:4736`

### Agent 16 — 🚢 PASSAGE (Transportation Realm)
- **Index:** Mobility Autonomy Fraction — `MAF = sustainable_miles / total_miles`
- **Channel:** `#passage-transportation`
- **Mission:** Serve movement with clean, locally-controlled mobility that keeps value circulating locally.
- **MCP:** `buzz mcp add --name passage --config agents/passage/config.toml --relay ws://localhost:4736`

### Agent 17 — ⚒️ FORGE (Manufacturing Realm)
- **Index:** Regenerative Production Ratio — `RPR = local_production / local_demand`
- **Channel:** `#forge-manufacturing`
- **Mission:** Produce what your community needs from materials it controls — light, strong, local.
- **MCP:** `buzz mcp add --name forge --config agents/forge/config.toml --relay ws://localhost:4736`

### Agent 18 — 🌾 THRIVE (Economics Realm)
- **Index:** Abundance Finance Index — `AFI = value_created / debt_issued`
- **Channel:** `#thrive-economics`
- **Mission:** Generate more real value than the credit consumed — operate in abundance, not leakage.
- **MCP:** `buzz mcp add --name thrive --config agents/thrive/config.toml --relay ws://localhost:4736`

### Agent 19 — ⚖️ COUNCIL (Governance Realm)
- **Index:** Justice Coherence Index — `JCI = equity_decisions / total_decisions`
- **Channel:** `#council-governance`
- **Mission:** Raise the fraction of governance decisions that produce equitable outcomes — governance as legitimacy.
- **MCP:** `buzz mcp add --name council --config agents/council/config.toml --relay ws://localhost:4736`

---

## 🧩 Deploying All 20 at Once

To register the entire Raven Council in one command:

```bash
./scripts/launch-raven.sh --all-agents
```

This iterates over every folder in [`agents/`](agents/), reads each `config.toml`, and registers the agent with your local relay. Raven then runs the onboarding sequence (see [`workflows/onboarding-sequence.yaml`](workflows/onboarding-sequence.yaml)).

---

## 📖 Related Documentation

- [The 6D Framework](docs/6d-framework.md) — the recursive loop every agent runs
- [The Scope Selector](docs/scope-selector.md) — how agents adapt across 9 scope levels
- [Peace Efficiency Index](docs/math/peace-efficiency-index.md) — how Raven aggregates the 12 realms
- [ARCHITECTURE.md](ARCHITECTURE.md) — how agents map onto Buzz + Nostr
