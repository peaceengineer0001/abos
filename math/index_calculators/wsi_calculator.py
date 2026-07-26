#!/usr/bin/env python3
"""Water Sovereignty Index (WSI) — Resource Realm: Water (Tide 🌊).

WSI measures how much of a community's water consumption is met by locally
captured / regenerated water that stays within the local hydrological cycle:

    WSI = W_regen / W_consumed

where
    W_regen     = locally captured or regenerated water over the period
                  (rainwater harvest, treated greywater reuse, managed
                  aquifer recharge, ...) in liters
    W_consumed  = total water consumed by the community over the period in liters

Interpretation:
    WSI >= 1.0  -> water sovereign (captures/regenerates at least what it uses)
    WSI  = 0.0  -> fully dependent on imported / extracted water

WSI feeds the Peace Efficiency Index as the "water" realm ratio (R/D),
with R = W_regen and D = W_consumed.
"""
from __future__ import annotations

from typing import Any, Dict

MIN_CONSUMED = 1e-6  # floor to avoid divide-by-zero


def calculate_wsi(w_regen: float, w_consumed: float) -> Dict[str, Any]:
    """Compute the Water Sovereignty Index.

    Args:
        w_regen:    locally captured/regenerated water (liters, >= 0).
        w_consumed: total community water consumption (liters, > 0).

    Returns:
        dict with keys: wsi, sovereign (bool), deficit_liters, inputs.
    """
    if w_regen < 0:
        raise ValueError(f"w_regen must be >= 0 (got {w_regen}).")
    if w_consumed < 0:
        raise ValueError(f"w_consumed must be >= 0 (got {w_consumed}).")

    consumed = max(float(w_consumed), MIN_CONSUMED)
    wsi = float(w_regen) / consumed
    deficit = max(0.0, float(w_consumed) - float(w_regen))

    return {
        "wsi": round(wsi, 4),
        "sovereign": wsi >= 1.0,
        "deficit_liters": round(deficit, 4),
        "inputs": {"w_regen": w_regen, "w_consumed": w_consumed},
    }


def _demo() -> None:
    result = calculate_wsi(w_regen=900, w_consumed=1100)
    print("Water Sovereignty Index (WSI) — demo")
    print(f"  WSI            = {result['wsi']}")
    print(f"  sovereign      = {result['sovereign']}")
    print(f"  deficit_liters = {result['deficit_liters']}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        assert calculate_wsi(100, 100)["wsi"] == 1.0
        assert calculate_wsi(0, 100)["wsi"] == 0.0
        assert calculate_wsi(150, 100)["sovereign"] is True
        assert calculate_wsi(60, 100)["deficit_liters"] == 40.0
        print("wsi_calculator self-test passed. Run with --demo for a worked example.")
