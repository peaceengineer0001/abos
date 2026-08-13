"""
abos.nostr.events
=================

NIP-01 event construction/signing plus the ABOS custom event-kind registry.

Every message an ABOS agent puts on the workspace bus is a real, signed Nostr
event: ``id`` is the SHA-256 of the canonical serialization and ``sig`` is a
BIP-340 Schnorr signature over that id (verifiable with
:func:`abos.nostr.crypto.schnorr_verify`).

The custom kinds extend the peace-protocols ``[nostr_kinds]`` block
(30100–30105 are reserved by Raven for Pe/CVI). ABOS claims the 31xxx range for
the Business Operating System workspace layer.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import crypto

# --------------------------------------------------------------------------- #
# ABOS Nostr event kinds (parametrized replaceable / regular)
# --------------------------------------------------------------------------- #
KIND_TEXT_NOTE = 1              # NIP-01 plain note (fallback / human posts)
KIND_CHANNEL_CREATE = 40       # NIP-28 create channel
KIND_CHANNEL_METADATA = 41     # NIP-28 channel metadata
KIND_CHANNEL_MESSAGE = 42      # NIP-28 channel message (workspace posts)

# ABOS BOSS workspace kinds (31xxx range — additive to Raven's 301xx)
KIND_AGENT_STATUS = 31000      # agent heartbeat / status
KIND_EVIDENCE = 31001          # evidence submitted to the loop
KIND_ANALYSIS = 31002          # ChiefAnalyst aggregation output
KIND_RECOMMENDATION = 31003    # specialist recommendation
KIND_GOVERNED_DECISION = 31004 # decision object (pending / resolved)
KIND_APPROVAL_REQUEST = 31005  # human-approval request
KIND_APPROVAL_RESULT = 31006   # approve / deny result with reason
KIND_SCORECARD = 31007         # BOSS 7-metric rubric scorecard
KIND_RISK_FLAG = 31008         # risk / red-flag escalation
KIND_POLICY_DENIAL = 31009     # deterministic denial (authority/evidence)

KIND_NAMES = {
    KIND_TEXT_NOTE: "text_note",
    KIND_CHANNEL_CREATE: "channel_create",
    KIND_CHANNEL_METADATA: "channel_metadata",
    KIND_CHANNEL_MESSAGE: "channel_message",
    KIND_AGENT_STATUS: "agent_status",
    KIND_EVIDENCE: "evidence",
    KIND_ANALYSIS: "analysis",
    KIND_RECOMMENDATION: "recommendation",
    KIND_GOVERNED_DECISION: "governed_decision",
    KIND_APPROVAL_REQUEST: "approval_request",
    KIND_APPROVAL_RESULT: "approval_result",
    KIND_SCORECARD: "scorecard",
    KIND_RISK_FLAG: "risk_flag",
    KIND_POLICY_DENIAL: "policy_denial",
}


@dataclass
class NostrEvent:
    """A NIP-01 event. ``id``/``sig`` are filled by :meth:`finalize`."""

    pubkey: str
    kind: int
    content: str
    tags: List[List[str]] = field(default_factory=list)
    created_at: int = field(default_factory=lambda: int(time.time()))
    id: str = ""
    sig: str = ""

    def _serialize(self) -> str:
        # Canonical NIP-01 serialization for id computation.
        return json.dumps(
            [0, self.pubkey, self.created_at, self.kind, self.tags, self.content],
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def compute_id(self) -> str:
        return hashlib.sha256(self._serialize().encode("utf-8")).hexdigest()

    def finalize(self, privkey_hex: str) -> "NostrEvent":
        """Compute id and Schnorr-sign the event."""
        self.id = self.compute_id()
        self.sig = crypto.schnorr_sign(bytes.fromhex(self.id), privkey_hex)
        return self

    def verify(self) -> bool:
        if self.id != self.compute_id():
            return False
        return crypto.schnorr_verify(bytes.fromhex(self.id), self.pubkey, self.sig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pubkey": self.pubkey,
            "created_at": self.created_at,
            "kind": self.kind,
            "kind_name": KIND_NAMES.get(self.kind, str(self.kind)),
            "tags": self.tags,
            "content": self.content,
            "sig": self.sig,
        }


def build_event(
    privkey_hex: str,
    kind: int,
    content: Any,
    tags: Optional[List[List[str]]] = None,
    created_at: Optional[int] = None,
) -> NostrEvent:
    """Build, sign and return a finalized NostrEvent.

    ``content`` may be a str or any JSON-serializable object (dicts are dumped).
    """
    pubkey = crypto.get_public_key(privkey_hex)
    if not isinstance(content, str):
        content = json.dumps(content, separators=(",", ":"), ensure_ascii=False)
    ev = NostrEvent(
        pubkey=pubkey,
        kind=kind,
        content=content,
        tags=tags or [],
        created_at=created_at or int(time.time()),
    )
    return ev.finalize(privkey_hex)


def channel_tag(channel_id: str) -> List[str]:
    """NIP-28 root reference tag for a channel message."""
    return ["e", channel_id, "", "root"]
