#!/usr/bin/env python3
"""Debt Freedom Ratio (DFR) — Sovereign Body: Ember 🔥.

DFR measures how free a community (or household) is from extractive debt
service, expressed as the share of income NOT committed to servicing debt:

    DFR = 1 - (Debt_service / Income)

where
    Debt_service = periodic obligations to external creditors over the period
                   (loan principal + interest, rents to absentee owners, ...)
    Income       = total income available to the community over the period

Interpretation:
    DFR  = 1.0  -> debt free (no income is extracted by external creditors)
    DFR  = 0.0  -> all income is consumed by debt service
    DFR  < 0.0  -> debt service exceeds income (insolvent) — clamped, but flagged

DFR is a resilience input to the Peace Efficiency Index economics realm and to
the coherence-shock early-warning workflow, because high debt loads convert
external shocks into local crises.
"""
from __future__ import annotations

from typing import Any, Dict

MIN_INCOME = 1e-6  # floor to avoid divide-by-zero


def calculate_dfr(debt_service: float, income: float) -> Dict[str, Any]:
    """Compute the Debt Freedom Ratio.

    Args:
        debt_service: periodic debt obligations (currency units, >= 0).
        income:       total income over the period (currency units, > 0).

    Returns:
        dict with keys: dfr, debt_service_ratio, insolvent (bool), inputs.
    """
    if debt_service < 0:
        raise ValueError(f"debt_service must be >= 0 (got {debt_service}).")
    if income < 0:
        raise ValueError(f"income must be >= 0 (got {income}).")

    inc = max(float(income), MIN_INCOME)
    ds_ratio = float(debt_service) / inc
    dfr_raw = 1.0 - ds_ratio
    dfr = max(0.0, dfr_raw)  # clamp reported score at 0 for the sovereignty scale

    return {
        "dfr": round(dfr, 4),
        "debt_service_ratio": round(ds_ratio, 4),
        "insolvent": dfr_raw < 0.0,
        "inputs": {"debt_service": debt_service, "income": income},
    }


def _demo() -> None:
    result = calculate_dfr(debt_service=3200, income=8000)
    print("Debt Freedom Ratio (DFR) — demo")
    print(f"  DFR                = {result['dfr']}")
    print(f"  debt_service_ratio = {result['debt_service_ratio']}")
    print(f"  insolvent          = {result['insolvent']}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        assert calculate_dfr(0, 100)["dfr"] == 1.0
        assert calculate_dfr(100, 100)["dfr"] == 0.0
        assert calculate_dfr(25, 100)["dfr"] == 0.75
        assert calculate_dfr(150, 100)["insolvent"] is True
        assert calculate_dfr(150, 100)["dfr"] == 0.0
        print("dfr_calculator self-test passed. Run with --demo for a worked example.")
