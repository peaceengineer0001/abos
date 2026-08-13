"""
abos.nostr.relay
================

Relay connectivity for the ABOS workspace bus. Two backends implement the same
:class:`RelayBackend` interface so the same agent code runs against a live relay
in production and against an in-memory relay in the demo / tests:

* :class:`WebsocketRelay` — a real NIP-01 client (``EVENT`` / ``REQ`` / ``EOSE``
  frames over a ``wss://`` connection). Uses the ``websockets`` dependency that
  peace-protocols already ships.
* :class:`LocalRelay` — an in-process relay that stores signed events and serves
  subscriptions synchronously. This is what the deterministic demo and the
  FastAPI backend use so the pitch runs with zero external infrastructure, while
  every event is still a real signed Nostr event.

Relay URLs default to the peace-protocols convention (``ws://localhost:4736``,
see ``agents/raven/config.toml``) and can be overridden per environment.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

from .events import NostrEvent


DEFAULT_RELAYS = [
    "ws://localhost:4736",          # peace-protocols local relay convention
    "wss://relay.damus.io",         # public fallback relays
    "wss://nos.lol",
]


class RelayBackend:
    """Interface every relay backend implements."""

    def publish(self, event: NostrEvent) -> bool:  # pragma: no cover - iface
        raise NotImplementedError

    def query(self, **filters: Any) -> List[NostrEvent]:  # pragma: no cover
        raise NotImplementedError

    def subscribe(self, callback: Callable[[NostrEvent], None], **filters: Any) -> str:
        raise NotImplementedError


class LocalRelay(RelayBackend):
    """In-process relay: stores signed events, serves filtered subscriptions.

    Events must pass :meth:`NostrEvent.verify` to be accepted — so even the demo
    relay enforces real signatures.
    """

    def __init__(self) -> None:
        self._events: List[NostrEvent] = []
        self._subs: Dict[str, tuple] = {}
        self._sub_counter = 0

    # -- write side --------------------------------------------------------- #
    def publish(self, event: NostrEvent) -> bool:
        if not event.verify():
            raise ValueError(f"rejected event {event.id[:12]}: invalid signature")
        self._events.append(event)
        for _sid, (cb, filt) in list(self._subs.items()):
            if self._matches(event, filt):
                cb(event)
        return True

    # -- read side ---------------------------------------------------------- #
    def query(self, **filters: Any) -> List[NostrEvent]:
        out = [e for e in self._events if self._matches(e, filters)]
        out.sort(key=lambda e: e.created_at, reverse=True)
        limit = filters.get("limit")
        return out[:limit] if limit else out

    def subscribe(self, callback: Callable[[NostrEvent], None], **filters: Any) -> str:
        self._sub_counter += 1
        sid = f"sub{self._sub_counter}"
        self._subs[sid] = (callback, filters)
        # Replay matching history immediately (EOSE semantics).
        for e in self.query(**filters):
            callback(e)
        return sid

    def unsubscribe(self, sid: str) -> None:
        self._subs.pop(sid, None)

    @staticmethod
    def _matches(event: NostrEvent, filt: Dict[str, Any]) -> bool:
        if not filt:
            return True
        kinds = filt.get("kinds")
        if kinds and event.kind not in kinds:
            return False
        authors = filt.get("authors")
        if authors and event.pubkey not in authors:
            return False
        # tag filters: #e, #p, #t, #d, #tenant
        for key, vals in filt.items():
            if not key.startswith("#"):
                continue
            tagname = key[1:]
            evt_vals = [t[1] for t in event.tags if len(t) >= 2 and t[0] == tagname]
            if not any(v in evt_vals for v in vals):
                return False
        return True

    def all_events(self) -> List[NostrEvent]:
        return list(self._events)


class WebsocketRelay(RelayBackend):
    """Real NIP-01 relay client over ``websockets`` (production backend).

    Kept synchronous-friendly with short-lived connections so it can be called
    from the FastAPI request path or the demo without an event loop already
    running. For high-throughput deployments, swap in a persistent connection.
    """

    def __init__(self, url: str = DEFAULT_RELAYS[0], timeout: float = 5.0) -> None:
        self.url = url
        self.timeout = timeout

    def publish(self, event: NostrEvent) -> bool:
        import asyncio

        async def _run() -> bool:
            import websockets

            async with websockets.connect(self.url, open_timeout=self.timeout) as ws:
                await ws.send(json.dumps(["EVENT", event.to_dict()]))
                try:
                    resp = await asyncio.wait_for(ws.recv(), timeout=self.timeout)
                    data = json.loads(resp)
                    return not (data[0] == "OK" and data[2] is False)
                except asyncio.TimeoutError:
                    return True

        return asyncio.run(_run())

    def query(self, **filters: Any) -> List[NostrEvent]:
        import asyncio

        async def _run() -> List[NostrEvent]:
            import websockets

            sub_id = "abos-q"
            nostr_filter = {k: v for k, v in filters.items() if v is not None}
            async with websockets.connect(self.url, open_timeout=self.timeout) as ws:
                await ws.send(json.dumps(["REQ", sub_id, nostr_filter]))
                collected: List[NostrEvent] = []
                while True:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=self.timeout)
                    except asyncio.TimeoutError:
                        break
                    msg = json.loads(raw)
                    if msg[0] == "EVENT" and msg[1] == sub_id:
                        d = msg[2]
                        collected.append(
                            NostrEvent(
                                pubkey=d["pubkey"], kind=d["kind"], content=d["content"],
                                tags=d.get("tags", []), created_at=d["created_at"],
                                id=d["id"], sig=d["sig"],
                            )
                        )
                    elif msg[0] == "EOSE" and msg[1] == sub_id:
                        break
                return collected

        return asyncio.run(_run())

    def subscribe(self, callback: Callable[[NostrEvent], None], **filters: Any) -> str:
        # Live streaming subscribe is deployment-specific; for the pilot we
        # poll via query(). Returns a synthetic id for interface parity.
        for e in self.query(**filters):
            callback(e)
        return "ws-poll"


def get_relay(mode: str = "local", url: Optional[str] = None) -> RelayBackend:
    """Factory: ``local`` (default, in-process) or ``ws`` (live relay)."""
    if mode == "ws":
        return WebsocketRelay(url or DEFAULT_RELAYS[0])
    return LocalRelay()
