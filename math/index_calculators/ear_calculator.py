#!/usr/bin/env python3
"""Energy Autonomy Ratio (EAR) — Resource Realm: Energy (Sol 🌞).

EAR measures what fraction of a community's energy *demand* is met by
locally-generated, regenerative supply:

    EAR = E_local_regen / E_demand

where
    E_local_regen = locally generated regenerative energy over the period
                    (solar, wind, micro-hydro, biogas, ...) in kWh
    E_demand      = total energy demand of the community over the period in kWh

Interpretation:
    EAR >= 1.0  -> net energy sovereign (produces at least as much as it uses)
    EAR  = 0.0  -> fully dependent on imported / centralized energy

EAR feeds the Peace Efficiency Index as the "energy" realm ratio (R/D),
with R = E_local_regen and D = E_demand.
"""
from __future__ import annotations

from typing import Any, Dict

MIN_DEMAND = 1e-6  # floor to avoid divide-by-zero


def calculate_ear(e_local_regen: float, e_demand: float) -> Dict[str, Any]:
    """Compute the Energy Autonomy Ratio.

    Args:
        e_local_regen: locally generated regenerative energy (kWh, >= 0).
        e_demand:      total community energy demand (kWh, > 0).

    Returns:
        dict with keys: ear, sovereign (bool), deficit_kwh, inputs.
    """
    if e_local_regen < 0:
        raise ValueError(f"e_local_regen must be >= 0 (got {e_local_regen}).")
    if e_demand < 0:
        raise ValueError(f"e_demand must be >= 0 (got {e_demand}).")

    demand = max(float(e_demand), MIN_DEMAND)
    ear = float(e_local_regen) / demand
    deficit = max(0.0, float(e_demand) - float(e_local_regen))

    return {
        "ear": round(ear, 4),
        "sovereign": ear >= 1.0,
        "deficit_kwh": round(deficit, 4),
        "inputs": {"e_local_regen": e_local_regen, "e_demand": e_demand},
    }


def _demo() -> None:
    result = calculate_ear(e_local_regen=4200, e_demand=5800)
    print("Energy Autonomy Ratio (EAR) — demo")
    print(f"  EAR         = {result['ear']}")
    print(f"  sovereign   = {result['sovereign']}")
    print(f"  deficit_kwh = {result['deficit_kwh']}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        assert calculate_ear(100, 100)["ear"] == 1.0
        assert calculate_ear(0, 100)["ear"] == 0.0
        assert calculate_ear(150, 100)["sovereign"] is True
        assert calculate_ear(50, 100)["deficit_kwh"] == 50.0
        print("ear_calculator self-test passed. Run with --demo for a worked example.")
