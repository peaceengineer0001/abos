#!/usr/bin/env python3
"""Resilience Delta (Sr) calculator.

The Resilience Delta measures whether a community is getting more or less
resilient over a measurement window — the net rate of change of coherence
under shocks:

    Sr = ΔC_pos − ΔC_neg

where
    ΔC_pos = total coherence GAINED from positive interventions (coherence shocks
             Raven engineers: celebrations, milestones, surplus-sharing)
    ΔC_neg = total coherence LOST from negative shocks (disruptions, conflicts, setbacks)

    Sr > 0  -> resilience rising  (CVI trajectory drifts upward)  [TARGET]
    Sr = 0  -> steady
    Sr < 0  -> resilience eroding (Raven schedules corrective coherence shocks)

See docs/math/resilience-delta.md for how Raven uses this.
"""
from __future__ import annotations

from typing import List, Dict, Any

STEADY_BAND = 1e-9   # |Sr| within this band is treated as "steady"


def _validate(shocks: List[float], label: str) -> None:
    for i, s in enumerate(shocks):
        if s < 0:
            raise ValueError(
                f"{label}[{i}] = {s}: contributions must be non-negative magnitudes. "
                f"Positive and negative effects are separated into the two lists.")


def _trajectory(sr: float) -> str:
    if sr > STEADY_BAND:
        return "rising"
    if sr < -STEADY_BAND:
        return "eroding"
    return "steady"


def calculate_sr(positive_shocks: List[float],
                 negative_shocks: List[float]) -> Dict[str, Any]:
    """Compute the Resilience Delta over a window.

    Args:
        positive_shocks: list of ΔC_pos magnitudes (coherence gains), each >= 0.
        negative_shocks: list of ΔC_neg magnitudes (coherence losses), each >= 0.

    Returns:
        dict with sr, delta_pos, delta_neg, and a trajectory verdict.
    """
    _validate(positive_shocks, "positive_shocks")
    _validate(negative_shocks, "negative_shocks")
    delta_pos = sum(positive_shocks)
    delta_neg = sum(negative_shocks)
    sr = delta_pos - delta_neg
    return {
        "sr": round(sr, 4),
        "delta_pos": round(delta_pos, 4),
        "delta_neg": round(delta_neg, 4),
        "trajectory": _trajectory(sr),
        "positive_count": len(positive_shocks),
        "negative_count": len(negative_shocks),
    }


def _demo() -> None:
    print("Resilience Delta (Sr) — demo")
    result = calculate_sr(
        positive_shocks=[0.05, 0.03, 0.08],   # e.g. celebration, milestone, surplus-share
        negative_shocks=[0.02, 0.06],         # e.g. supply disruption, conflict
    )
    print(f"  ΔC_pos = {result['delta_pos']}  ({result['positive_count']} interventions)")
    print(f"  ΔC_neg = {result['delta_neg']}  ({result['negative_count']} shocks)")
    print(f"  Sr     = {result['sr']}  ->  trajectory: {result['trajectory']}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        pos = calculate_sr([0.1, 0.1], [0.05])
        assert pos["sr"] == 0.15 and pos["trajectory"] == "rising", pos
        neg = calculate_sr([0.01], [0.2])
        assert neg["trajectory"] == "eroding", neg
        steady = calculate_sr([0.1], [0.1])
        assert steady["trajectory"] == "steady", steady
        print("sr_calculator self-test passed. Run with --demo for a worked example.")
