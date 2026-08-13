#!/usr/bin/env python3
"""
seed_demo.py — populate all six ABOS business scenarios and write demo_state.json.

The web demo panel reads ``demo_state.json``; the API also autoseeds from it.

Usage::

    python3 scripts/seed_demo.py [output_path]
"""
from __future__ import annotations

import json
import os
import sys

# Make the repo root importable when run directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abos.demo import build_demo_state, SCENARIOS  # noqa: E402


def main() -> None:
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_state.json")

    print("Seeding ABOS demo dataset …")
    state = build_demo_state()

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)

    tenants = state["tenants"]
    print(f"\n✓ Seeded {len(tenants)} tenants across {len(SCENARIOS)} business models:")
    for tid, t in tenants.items():
        pend = len(t["pending_decisions"])
        score = t["scorecard"]["score"]
        grade = t["scorecard"]["grade"]
        print(f"  • {t['name']:<34} [{t['business_type']:<21}] "
              f"score {score:>5} ({grade})  users {len(t['users'])}  "
              f"evidence {len(t['evidence'])}  pending {pend}")
    print(f"\n✓ Wrote {out_path} ({os.path.getsize(out_path):,} bytes)")


if __name__ == "__main__":
    main()
