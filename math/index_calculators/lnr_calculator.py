#!/usr/bin/env python3
"""Local Nutrition Ratio (LNR) — Resource Realm: Food (Root 🌱).

LNR measures what fraction of a community's caloric / nutritional intake is
produced within its own local foodshed:

    LNR = Food_local / Food_total

where
    Food_local = nutrition produced within the local foodshed over the period
                 (kcal, or kg of produce converted to kcal)
    Food_total = total nutrition consumed by the community over the period (kcal)

Interpretation:
    LNR  = 1.0  -> fully locally nourished
    LNR  = 0.0  -> fully dependent on imported food

LNR feeds the Peace Efficiency Index as the "food" realm ratio (R/D),
with R = Food_local and D = Food_total. LNR is naturally bounded to [0, 1]
because local production cannot exceed total consumption in this ratio; a
community producing an export surplus is measured separately.
"""
from __future__ import annotations

from typing import Any, Dict

MIN_TOTAL = 1e-6  # floor to avoid divide-by-zero


def calculate_lnr(food_local: float, food_total: float) -> Dict[str, Any]:
    """Compute the Local Nutrition Ratio.

    Args:
        food_local: locally produced nutrition (kcal, >= 0).
        food_total: total nutrition consumed (kcal, > 0).

    Returns:
        dict with keys: lnr, import_dependency, imported_kcal, inputs.
    """
    if food_local < 0:
        raise ValueError(f"food_local must be >= 0 (got {food_local}).")
    if food_total < 0:
        raise ValueError(f"food_total must be >= 0 (got {food_total}).")

    total = max(float(food_total), MIN_TOTAL)
    lnr = min(float(food_local) / total, 1.0)
    imported = max(0.0, float(food_total) - float(food_local))

    return {
        "lnr": round(lnr, 4),
        "import_dependency": round(1.0 - lnr, 4),
        "imported_kcal": round(imported, 4),
        "inputs": {"food_local": food_local, "food_total": food_total},
    }


def _demo() -> None:
    result = calculate_lnr(food_local=300, food_total=2200)
    print("Local Nutrition Ratio (LNR) — demo")
    print(f"  LNR               = {result['lnr']}")
    print(f"  import_dependency = {result['import_dependency']}")
    print(f"  imported_kcal     = {result['imported_kcal']}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        assert calculate_lnr(100, 100)["lnr"] == 1.0
        assert calculate_lnr(0, 100)["lnr"] == 0.0
        assert calculate_lnr(25, 100)["import_dependency"] == 0.75
        assert calculate_lnr(25, 100)["imported_kcal"] == 75.0
        print("lnr_calculator self-test passed. Run with --demo for a worked example.")
