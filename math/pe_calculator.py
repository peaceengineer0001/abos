#!/usr/bin/env python3
"""Peace Efficiency Index (Pe) calculator.

The Peace Efficiency Index is the first of the two master metrics of the
Peace Protocols. It sums the regenerative-over-dependency ratio across the
12 Resource Realms:

    Pe = Σ (Rᵢ / Dᵢ)   for i = 1 .. 12

where
    Rᵢ = regenerative output of realm i (kWh, liters, kcal, decisions, ...)
    Dᵢ = dependency factor of realm i on centralized/imported provisioning (Dᵢ > 0)

A fully break-even community (every Rᵢ / Dᵢ == 1) scores Pe = 12.
The normalized form Pe / 12 gives an intuitive 0..1-style score around 1.0.

See docs/math/peace-efficiency-index.md for the full derivation.
"""
from __future__ import annotations

from typing import Dict, Any

# The 12 Resource Realms, in canonical order (i = 1 .. 12).
REALMS = [
    "energy",          # Sol   — EAR
    "water",           # Tide  — WSI
    "food",            # Root  — LNR
    "health",          # Heal  — WAI
    "shelter",         # Haven — HIS
    "waste",           # Cycle — CI
    "education",       # Lore  — KLI
    "communication",   # Mesh  — FFR
    "transportation",  # Passage — MAF
    "manufacturing",   # Forge — RPR
    "economics",       # Thrive — AFI
    "governance",      # Council — JCI
]

# Guard rails: a near-zero dependency must not let one realm dominate the sum.
MIN_DEPENDENCY = 1e-6      # floor for Dᵢ to avoid divide-by-zero
MAX_RATIO = 10.0          # clamp any single realm ratio to a sane maximum


def _validate_realm(name: str, values: Dict[str, float]) -> None:
    if "R" not in values or "D" not in values:
        raise ValueError(f"Realm '{name}' must provide both 'R' and 'D'.")
    r, d = values["R"], values["D"]
    if r < 0:
        raise ValueError(f"Realm '{name}': regenerative output R must be >= 0 (got {r}).")
    if d < 0:
        raise ValueError(f"Realm '{name}': dependency D must be >= 0 (got {d}).")


def calculate_pe(realms: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Compute the Peace Efficiency Index from 12 realm inputs.

    Args:
        realms: mapping of realm name -> {"R": regenerative_output, "D": dependency}.
                All 12 canonical realms should be present; missing realms are
                treated as fully dependent (ratio 0) and flagged.

    Returns:
        dict with keys:
            pe          - total Peace Efficiency Index (sum of 12 ratios)
            normalized  - pe / 12 (0..1-style score; 1.0 == break-even everywhere)
            breakdown   - list of per-realm dicts sorted ascending by ratio
                          (lowest ratio first = highest-leverage "fuel barge")
            missing     - list of canonical realms not supplied
    """
    breakdown = []
    missing = []
    total = 0.0

    for name in REALMS:
        if name not in realms:
            missing.append(name)
            breakdown.append({"realm": name, "R": 0.0, "D": 0.0, "ratio": 0.0})
            continue
        _validate_realm(name, realms[name])
        r = float(realms[name]["R"])
        d = max(float(realms[name]["D"]), MIN_DEPENDENCY)
        ratio = min(r / d, MAX_RATIO)
        total += ratio
        breakdown.append({"realm": name, "R": r, "D": d, "ratio": round(ratio, 4)})

    # Sort by ratio ascending so the weakest (highest-leverage) realm is first.
    breakdown_sorted = sorted(breakdown, key=lambda x: x["ratio"])

    return {
        "pe": round(total, 4),
        "normalized": round(total / len(REALMS), 4),
        "breakdown": breakdown_sorted,
        "missing": missing,
    }


def _demo() -> None:
    realms = {
        "energy":         {"R": 4200, "D": 5800},
        "water":          {"R": 900,  "D": 1100},
        "food":           {"R": 300,  "D": 2200},
        "health":         {"R": 6,    "D": 10},
        "shelter":        {"R": 1,    "D": 1},
        "waste":          {"R": 70,   "D": 30},
        "education":      {"R": 4,    "D": 6},
        "communication":  {"R": 8,    "D": 2},
        "transportation": {"R": 3000, "D": 9000},
        "manufacturing":  {"R": 2,    "D": 8},
        "economics":      {"R": 1.2,  "D": 1.0},
        "governance":     {"R": 5,    "D": 5},
    }
    result = calculate_pe(realms)
    print("Peace Efficiency Index (Pe) — demo")
    print(f"  Pe          = {result['pe']}")
    print(f"  normalized  = {result['normalized']}  (1.0 = break-even everywhere)")
    print("  Highest-leverage realms (lowest ratio first):")
    for row in result["breakdown"][:3]:
        print(f"    {row['realm']:<15} ratio={row['ratio']}  (R={row['R']} / D={row['D']})")
    if result["missing"]:
        print(f"  missing realms: {result['missing']}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        # Minimal self-test.
        even = {r: {"R": 1, "D": 1} for r in REALMS}
        res = calculate_pe(even)
        assert res["pe"] == 12.0, res
        assert res["normalized"] == 1.0, res
        print("pe_calculator self-test passed. Run with --demo for a worked example.")
