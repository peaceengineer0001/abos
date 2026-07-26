#!/usr/bin/env bash
#
# launch-raven.sh — start Raven, the orchestrator agent.
#
# Raven is the entry point of the Peace Protocols agent constellation. It runs
# the intake conversation, selects the active scope, and coordinates the 19
# domain agents across the 6D loop (Discover -> Decipher -> Design -> Develop
# -> Deploy -> Defend). This launcher wires up the local config and starts the
# orchestrator; if the compiled core is not yet built it falls back to the
# reference Python entry point.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

info() { printf '\033[1;34m[raven]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*"; }

# --- Resolve config ---------------------------------------------------------
CONFIG="${PEACE_CONFIG:-.local/peace-protocols.toml}"
if [ ! -f "$CONFIG" ]; then
  warn "No local config at $CONFIG — falling back to config/peace-protocols.example.toml"
  warn "Run scripts/setup.sh first to create your local config."
  CONFIG="config/peace-protocols.example.toml"
fi
info "Using config: $CONFIG"

AGENT_DIR="agents/raven"
if [ ! -f "$AGENT_DIR/system_prompt.md" ]; then
  echo "error: cannot find $AGENT_DIR/system_prompt.md — are you in the repo root?" >&2
  exit 1
fi
info "Loading orchestrator prompt: $AGENT_DIR/system_prompt.md"

# --- Prefer the compiled Tauri/Rust core if present -------------------------
if command -v cargo >/dev/null 2>&1 && [ -f Cargo.toml ]; then
  info "Building & launching the Rust core (release)..."
  exec cargo run --release -- --agent raven --config "$CONFIG"
fi

# --- Fallback: reference Python runner --------------------------------------
if command -v python3 >/dev/null 2>&1; then
  if [ -f src/runner.py ]; then
    info "Launching the Python reference runner..."
    exec python3 src/runner.py --agent raven --config "$CONFIG"
  fi
  warn "No compiled core and no src/runner.py yet."
  warn "Raven's prompt and intake questions are ready at $AGENT_DIR/."
  warn "Wire them into your LLM client of choice, or build the core (see ARCHITECTURE.md)."
  exit 0
fi

echo "error: neither cargo nor python3 is available to launch Raven." >&2
exit 1
