"""
abos.nostr
==========

The ABOS Nostr workspace layer — real secp256k1/BIP-340 keypairs, NIP-01 signed
events, NIP-28 workspace channels, and a relay abstraction with a live
websocket backend and an in-process demo backend.

Additive to the peace-protocols Nostr conventions (per-agent ``channel`` +
``[nostr_kinds]``); nothing here modifies the upstream Raven agents.
"""

from . import crypto
from .events import (
    NostrEvent,
    build_event,
    KIND_AGENT_STATUS,
    KIND_EVIDENCE,
    KIND_ANALYSIS,
    KIND_RECOMMENDATION,
    KIND_GOVERNED_DECISION,
    KIND_APPROVAL_REQUEST,
    KIND_APPROVAL_RESULT,
    KIND_SCORECARD,
    KIND_RISK_FLAG,
    KIND_POLICY_DENIAL,
    KIND_NAMES,
)
from .relay import RelayBackend, LocalRelay, WebsocketRelay, get_relay, DEFAULT_RELAYS
from .channels import WorkspaceBus, WORKSPACE_CHANNELS, Channel

__all__ = [
    "crypto", "NostrEvent", "build_event",
    "RelayBackend", "LocalRelay", "WebsocketRelay", "get_relay", "DEFAULT_RELAYS",
    "WorkspaceBus", "WORKSPACE_CHANNELS", "Channel",
    "KIND_AGENT_STATUS", "KIND_EVIDENCE", "KIND_ANALYSIS", "KIND_RECOMMENDATION",
    "KIND_GOVERNED_DECISION", "KIND_APPROVAL_REQUEST", "KIND_APPROVAL_RESULT",
    "KIND_SCORECARD", "KIND_RISK_FLAG", "KIND_POLICY_DENIAL", "KIND_NAMES",
]
