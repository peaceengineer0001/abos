"""
ABOS — Agentic Business Operating System
=======================================

ABOS extends the peace-protocols Agent Zero + Nostr foundation into a governed,
multi-tenant business operating system: 11 BOSS specialist agents across four
streams (govern / run / grow / decide) that turn *evidence in* into *governed
action out*, with humans in control of every high-impact decision.

Public surface:
    abos.core      — governance core (agents, policy, evidence, scorecard, approval)
    abos.agents    — the 11 specialists + the Council factory
    abos.nostr     — real secp256k1 keypairs, NIP-01 events, NIP-28 workspace bus
    abos.templates — 6 business-model configurations
    abos.tenant    — the per-tenant runtime that binds it all together
    abos.api       — the FastAPI backend
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
