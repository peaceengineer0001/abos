"""
abos.nostr.channels
===================

The ABOS workspace bus, modelled as NIP-28 public-chat channels. Each workspace
channel (``#ops``, ``#finance``, ``#compliance``, ``#growth``, ``#decisions``)
is a Nostr channel; agents publish updates / recommendations / approval requests
into their channels and humans subscribe to read and act.

This maps the peace-protocols per-agent ``channel`` convention (e.g. Raven's
``#raven-command``) onto real NIP-28 events flowing over :mod:`abos.nostr.relay`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from . import events as ev
from .events import NostrEvent
from .relay import RelayBackend, get_relay

# The five canonical BOSS workspace channels, mapped to the 4 streams.
WORKSPACE_CHANNELS = {
    "#compliance": {"stream": "govern", "topic": "compliance", "name": "Compliance & Governance"},
    "#ops": {"stream": "run", "topic": "ops", "name": "Operations"},
    "#finance": {"stream": "run", "topic": "finance", "name": "Finance"},
    "#growth": {"stream": "grow", "topic": "growth", "name": "Growth & Client"},
    "#decisions": {"stream": "decide", "topic": "decisions", "name": "Decisions & Approvals"},
}


@dataclass
class Channel:
    channel_id: str        # Nostr event id of the kind-40 create event
    slug: str              # e.g. "#ops"
    name: str
    stream: str


class WorkspaceBus:
    """NIP-28 workspace bus over a relay backend.

    The bus is per-tenant: channel messages carry a ``["t", tenant_id]`` tag and
    a ``["stream", ...]`` tag so subscribers can filter by tenant and stream.
    """

    def __init__(self, tenant_id: str, relay: Optional[RelayBackend] = None,
                 admin_privkey: Optional[str] = None) -> None:
        self.tenant_id = tenant_id
        self.relay = relay or get_relay("local")
        from . import crypto
        self.admin_privkey = admin_privkey or crypto.generate_privkey()
        self.channels: Dict[str, Channel] = {}

    # -- channel lifecycle -------------------------------------------------- #
    def ensure_channels(self) -> Dict[str, Channel]:
        """Create the five canonical workspace channels for this tenant."""
        for slug, meta in WORKSPACE_CHANNELS.items():
            if slug in self.channels:
                continue
            create = ev.build_event(
                self.admin_privkey,
                ev.KIND_CHANNEL_CREATE,
                {"name": f"{meta['name']} · {self.tenant_id}", "about": meta["name"],
                 "stream": meta["stream"]},
                tags=[["t", self.tenant_id], ["stream", meta["stream"]], ["slug", slug]],
            )
            self.relay.publish(create)
            self.channels[slug] = Channel(
                channel_id=create.id, slug=slug, name=meta["name"], stream=meta["stream"]
            )
        return self.channels

    def channel_for_stream(self, stream: str) -> Optional[Channel]:
        for ch in self.channels.values():
            if ch.stream == stream:
                return ch
        return None

    # -- posting ------------------------------------------------------------ #
    def post(self, agent_privkey: str, channel_slug: str, kind: int,
             content: Any, extra_tags: Optional[List[List[str]]] = None) -> NostrEvent:
        """Publish a signed workspace message from an agent into a channel."""
        self.ensure_channels()
        ch = self.channels.get(channel_slug)
        if ch is None:
            raise ValueError(f"unknown channel {channel_slug}")
        tags = [ev.channel_tag(ch.channel_id), ["t", self.tenant_id],
                ["stream", ch.stream], ["slug", channel_slug]]
        if extra_tags:
            tags.extend(extra_tags)
        event = ev.build_event(agent_privkey, kind, content, tags=tags)
        self.relay.publish(event)
        return event

    # -- reading ------------------------------------------------------------ #
    def feed(self, channel_slug: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Return recent workspace events (optionally one channel), newest first."""
        filters: Dict[str, Any] = {"#t": [self.tenant_id], "limit": limit}
        if channel_slug:
            filters["#slug"] = [channel_slug]
        evts = self.relay.query(**filters)
        return [e.to_dict() for e in evts]

    def subscribe(self, callback: Callable[[NostrEvent], None],
                  channel_slug: Optional[str] = None) -> str:
        filters: Dict[str, Any] = {"#t": [self.tenant_id]}
        if channel_slug:
            filters["#slug"] = [channel_slug]
        return self.relay.subscribe(callback, **filters)
