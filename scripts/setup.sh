#!/usr/bin/env bash
#
# setup.sh — bootstrap a local Peace Protocols development environment.
#
# Idempotent: safe to re-run. Verifies toolchains, pulls the block/buzz
# submodule, copies example configs into place, and runs the math self-tests.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

info()  { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
warn()  { printf '\033[1;33m[warn]\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m[ ok ]\033[0m %s\n' "$*"; }

# --- 1. Toolchain checks ----------------------------------------------------
info "Checking toolchains..."
check_tool() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "$1 found ($($1 --version 2>&1 | head -n1))"
  else
    warn "$1 not found — $2"
  fi
}
check_tool python3 "required for the math indexes (>=3.9)"
check_tool git     "required for submodules and version control"
check_tool cargo   "required to build the Tauri/Rust core (install via https://rustup.rs)"
check_tool node    "required for the desktop UI (install Node >=18)"

# --- 2. Submodules ----------------------------------------------------------
if [ -f .gitmodules ]; then
  info "Syncing git submodules (block/buzz)..."
  git submodule update --init --recursive || warn "submodule init skipped (no network or not a git checkout)"
fi

# --- 3. Config scaffolding --------------------------------------------------
info "Preparing local config files..."
mkdir -p .local
copy_example() {
  local src="$1" dest="$2"
  if [ -f "$src" ] && [ ! -f "$dest" ]; then
    cp "$src" "$dest"
    ok "created $dest"
  elif [ -f "$dest" ]; then
    ok "$dest already exists (left untouched)"
  fi
}
copy_example config/peace-protocols.example.toml .local/peace-protocols.toml
copy_example config/scope-config.example.toml     .local/scope-config.toml
copy_example config/llm-providers.example.toml    .local/llm-providers.toml
copy_example config/privacy-tiers.example.toml     .local/privacy-tiers.toml

# --- 4. Math self-tests -----------------------------------------------------
info "Running math self-tests..."
bash "$ROOT_DIR/scripts/run-math-tests.sh"

ok "Setup complete. Edit .local/*.toml, then run scripts/launch-raven.sh"
