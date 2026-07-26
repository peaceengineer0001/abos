#!/usr/bin/env python3
"""Community Vitality Index (CVI) calculator.

The Community Vitality Index is the second master metric of the Peace Protocols.
It is the ratio of vitality drivers to depletion drivers:

    CVI = (H + Dg + F) / (S + Db + De)

Numerator (vitality drivers):
    H  = Health   (preventive + regenerative care)      <- Heal (WAI)
    Dg = Dignity  (cultural integrity + inclusion)       <- Cedar (CCI) + Summit (SPR)
    F  = Freedom  (political agency + economic autonomy)  <- Summit (SPR) + Ember (DFR)

Denominator (depletion drivers):
    S  = Scarcity     (inverse of resource autonomy)      <- Stone (1 - LRA)
    Db = Debt burden  (financial extraction)              <- Ember (1 - DFR)
    De = Dependency   (aggregate realm dependency)        <- mean normalized Dᵢ

See docs/math/community-vitality-index.md for the full derivation.
"""
from __future__ import annotations

from typing import Dict, Any, List

# Floor for the denominator so a near-zero-depletion community yields a large but
# finite CVI rather than a divide-by-zero.
EPSILON = 1e-6


def _require_nonneg(**values: float) -> None:
    for k, v in values.items():
        if v is None:
            raise ValueError(f"CVI input '{k}' is required.")
        if v < 0:
            raise ValueError(f"CVI input '{k}' must be >= 0 (got {v}).")


def _status(cvi: float) -> str:
    if cvi > 1.0:
        return "thriving"
    if abs(cvi - 1.0) < 1e-9:
        return "break-even"
    return "depleting"


def calculate_cvi(H: float, Dg: float, F: float,
                  S: float, Db: float, De: float) -> Dict[str, Any]:
    """Compute the Community Vitality Index from its six synthesized inputs.

    Returns a dict with the cvi value, status, and numerator/denominator breakdown.
    """
    _require_nonneg(H=H, Dg=Dg, F=F, S=S, Db=Db, De=De)
    numerator = H + Dg + F
    denominator = max(S + Db + De, EPSILON)
    cvi = numerator / denominator
    return {
        "cvi": round(cvi, 4),
        "status": _status(cvi),
        "numerator": round(numerator, 4),
        "denominator": round(denominator, 4),
        "breakdown": {
            "vitality": {"H": H, "Dg": Dg, "F": F},
            "depletion": {"S": S, "Db": Db, "De": De},
        },
    }


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def derive_cvi_from_indices(WAI: float, CCI: float, SPR: float, DFR: float,
                            LRA: float, realm_dependencies: List[float]) -> Dict[str, Any]:
    """Derive the six CVI inputs from raw domain indices, then compute CVI.

    This is how Raven computes CVI in practice — it never asks for H/Dg/F/S/Db/De
    directly, it synthesizes them from the domain agents' normalized indices.

    Args:
        WAI: Wellness Autonomy Index (Heal), 0..1
        CCI: Cultural Continuity Index (Cedar), 0..1
        SPR: Sovereignty Participation Ratio (Summit), 0..1
        DFR: Debt Freedom Ratio (Ember), 0..1  (clamped to >= 0)
        LRA: Local Resource Autonomy (Stone), 0..1
        realm_dependencies: list of normalized dependency factors (0..1) per realm.
    """
    dfr = max(DFR, 0.0)  # DFR can be negative in raw form; clamp for the vitality synthesis
    H = WAI
    Dg = _mean([CCI, SPR])
    F = _mean([SPR, dfr])
    S = 1.0 - LRA
    Db = 1.0 - dfr
    De = _mean(realm_dependencies)
    result = calculate_cvi(H=H, Dg=Dg, F=F, S=S, Db=Db, De=De)
    result["derived_inputs"] = {"H": round(H, 4), "Dg": round(Dg, 4), "F": round(F, 4),
                                 "S": round(S, 4), "Db": round(Db, 4), "De": round(De, 4)}
    return result


def _demo() -> None:
    print("Community Vitality Index (CVI) — demo")
    direct = calculate_cvi(H=0.62, Dg=0.55, F=0.48, S=0.40, Db=0.30, De=0.50)
    print(f"  direct:  CVI = {direct['cvi']}  ({direct['status']})")

    derived = derive_cvi_from_indices(
        WAI=0.62, CCI=0.58, SPR=0.52, DFR=0.70, LRA=0.60,
        realm_dependencies=[0.4, 0.5, 0.6, 0.5, 0.4, 0.3, 0.5, 0.2, 0.6, 0.7, 0.5, 0.5],
    )
    print(f"  derived: CVI = {derived['cvi']}  ({derived['status']})")
    print(f"           inputs = {derived['derived_inputs']}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        # Break-even self-test: numerator == denominator -> CVI == 1.0
        res = calculate_cvi(H=0.5, Dg=0.5, F=0.5, S=0.5, Db=0.5, De=0.5)
        assert res["cvi"] == 1.0 and res["status"] == "break-even", res
        thriving = calculate_cvi(H=0.9, Dg=0.9, F=0.9, S=0.2, Db=0.2, De=0.2)
        assert thriving["status"] == "thriving", thriving
        print("cvi_calculator self-test passed. Run with --demo for a worked example.")
