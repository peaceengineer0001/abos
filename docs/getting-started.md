# 🚀 Getting Started with the Raven Network

This guide takes you from zero to a running Raven Network with all 20 agents active and your first **Pe** and **CVI** scores calculated. Estimated time: **20–40 minutes**, mostly waiting on downloads.

---

## 1. Prerequisites

The Raven Network forks Buzz (Rust backend, Tauri 2 + React 19 desktop). You need:

| Tool | Minimum Version | Purpose | Install |
|---|---|---|---|
| **git** | 2.30+ | clone + submodules | [git-scm.com](https://git-scm.com) |
| **Rust** | 1.77+ (stable) | build the Buzz relay | [rustup.rs](https://rustup.rs) |
| **Node.js** | 20 LTS+ | build the desktop UI | [nodejs.org](https://nodejs.org) |
| **pnpm** | 9+ | JS package manager | `npm i -g pnpm` |
| **Python** | 3.10+ | run the math calculators | [python.org](https://python.org) |
| **Tauri deps** | latest | desktop shell (webkit2gtk, etc.) | [tauri.app/start/prerequisites](https://tauri.app/start/prerequisites/) |
| **Ollama** *(recommended)* | latest | local LLM provider | [ollama.com](https://ollama.com) |

> **Sovereignty tip:** Ollama is the recommended default provider — no data leaves your device. You can also use Anthropic, OpenAI, or Buzz Mesh (see [`config/llm-providers.example.toml`](../config/llm-providers.example.toml)).

### Pull a local model (recommended)

```bash
ollama pull llama3.1:8b      # domain agents
ollama pull llama3.1:70b     # Raven (orchestrator) — needs a capable machine
```

If your machine can't run the 70b model, set Raven to `llama3.1:8b` too, or join a chapter **Buzz Mesh** to pool compute.

---

## 2. Clone the Repository (with the Buzz submodule)

Buzz is included as a git submodule, so use `--recurse-submodules`:

```bash
git clone --recurse-submodules https://github.com/peaceengineer0001/peace-protocols.git
cd peace-protocols
```

Already cloned without submodules? Fetch Buzz now:

```bash
git submodule update --init --recursive
```

---

## 3. One-Command Setup

The setup script installs dependencies, builds the Buzz relay, and generates your live config files from the `.example` templates:

```bash
./scripts/setup.sh
```

What it does:
1. Verifies prerequisites (git, Rust, Node, pnpm, Python).
2. Initializes the Buzz submodule if needed.
3. Copies `config/*.example.toml` → live `config/*.toml` (which are git-ignored).
4. Installs frontend dependencies (`pnpm install`).
5. Builds the Buzz relay (`cargo build --release` inside the submodule).
6. Runs `scripts/run-math-tests.sh` to confirm the calculators work.

---

## 4. Configure Your LLM Provider

Open `config/llm-providers.toml` (created by setup) and confirm your provider. The default is Ollama:

```toml
[llm]
provider = "ollama"
model    = "llama3.1:8b"
endpoint = "http://localhost:11434/v1"

[agents]
raven_model         = "llama3.1:70b"
domain_agents_model = "llama3.1:8b"
```

Using Anthropic or OpenAI instead? Add your API key here (it is stored locally and git-ignored).

---

## 5. First Run — Launch the Raven Network

```bash
./scripts/launch-raven.sh
```

This starts the Buzz relay on `ws://localhost:4736`, registers all 20 agents from [`agents/`](../agents/), and opens the desktop app. On first launch **Raven** greets you and runs the onboarding sequence:

1. **Scope Selection** — Individual, Couple, Family, House, Clan, Tribe, Church Congregation, Business, or Nation. See [scope-selector.md](scope-selector.md).
2. **Identity Context** — your name, location, and (optionally) lineage/tradition.
3. **Domain Intake** — each of the 19 agents asks its baseline questions (see each agent's `intake_questions.md`).
4. **Baseline Calculation** — Raven computes your initial **Pe** and **CVI**.
5. **Priority Identification** — your three highest-leverage opportunities.
6. **Activation** — the 6D loop begins across all domains.

The full onboarding logic is defined in [`workflows/onboarding-sequence.yaml`](../workflows/onboarding-sequence.yaml).

---

## 6. Verify Everything Is Running

```bash
# Check the relay is up
buzz relay status

# List the registered agents (expect 20)
buzz agent list

# Ask Raven for your current scores
buzz agent ask raven "What are my current Pe and CVI scores?"
```

You can also compute scores directly from the Python calculators without the full app:

```bash
python3 math/pe_calculator.py --demo
python3 math/cvi_calculator.py --demo
```

---

## 7. Where To Go Next

- 📐 [Scope Selector](scope-selector.md) — pick and configure your scope level
- ♻️ [The 6D Framework](6d-framework.md) — understand the recursive optimization loop
- 🤖 [AGENTS.md](../AGENTS.md) — meet all 20 agents and their MCP connections
- 📊 [Peace Efficiency Index](math/peace-efficiency-index.md) — the master metric math
- 🔐 [Privacy tiers](../config/privacy-tiers.example.toml) — control what (if anything) is ever shared

---

## 🛟 Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `submodule 'buzz' not initialized` | cloned without `--recurse-submodules` | `git submodule update --init --recursive` |
| Relay won't start on `4736` | port in use | set a different port in `config/peace-protocols.toml` |
| Agents time out | LLM endpoint unreachable | confirm `ollama serve` is running, check `endpoint` |
| Raven model too slow/OOM | 70b model too large | set `raven_model = "llama3.1:8b"` or use Buzz Mesh |
| Math tests fail | wrong Python version | use Python 3.10+ |

Still stuck? Open an issue with your OS, versions, and the relevant log lines.
