#!/usr/bin/env python3
"""Unified interface for all 19 Peace Protocols domain indexes.

Every one of the 19 domain agents (7 Sovereign Bodies + 12 Resource Realms)
owns exactly one health index. Most indexes share the same structural form —
a regenerative / sovereign numerator over a demand / total denominator, scored
toward 1.0 — so this module exposes a single registry and a uniform
``calculate(index_key, numerator, denominator)`` entry point, while delegating
to the dedicated, well-tested calculators where richer logic exists
(EAR, WSI, LNR, DFR, HRV).

Registry key -> metadata:
    key         short code used across configs and Nostr events
    name        human-readable index name
    agent       owning agent (spirit name)
    tier        "sovereign_body" or "resource_realm"
    numerator   what the numerator measures
    denominator what the denominator measures
    bounded01   True if the score is naturally clamped to [0, 1]

The two master metrics (Pe, CVI) and the stability metric (Sr) live in the
parent ``math`` package (pe_calculator, cvi_calculator, sr_calculator); this
module composes the 19 *domain* indexes that feed them.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

# Import the dedicated calculators (package-relative, with a flat fallback so
# the module also runs when executed directly from its own directory).
try:  # pragma: no cover - import plumbing
    from .ear_calculator import calculate_ear
    from .wsi_calculator import calculate_wsi
    from .lnr_calculator import calculate_lnr
    from .dfr_calculator import calculate_dfr
    from .hrv_calculator import coherence_ratio
except ImportError:  # pragma: no cover
    from ear_calculator import calculate_ear
    from wsi_calculator import calculate_wsi
    from lnr_calculator import calculate_lnr
    from dfr_calculator import calculate_dfr
    from hrv_calculator import coherence_ratio


MIN_DENOM = 1e-6
MAX_RATIO = 10.0


# ---------------------------------------------------------------------------
# Index registry: all 19 domain indexes.
# ---------------------------------------------------------------------------
INDEXES: Dict[str, Dict[str, Any]] = {
    # ---- 7 Sovereign Bodies -------------------------------------------------
    "Sc": {
        "name": "Security Coherence", "agent": "Starfire", "tier": "sovereign_body",
        "numerator": "de-escalated / prevented harm events",
        "denominator": "total threat events", "bounded01": True,
    },
    "IFE": {
        "name": "Information Fidelity & Epistemics", "agent": "Sage", "tier": "sovereign_body",
        "numerator": "verified / provenance-traced claims",
        "denominator": "total circulating claims", "bounded01": True,
    },
    "HRVcoh": {
        "name": "Heart-Rate-Variability Coherence", "agent": "River", "tier": "sovereign_body",
        "numerator": "coherence-band spectral power",
        "denominator": "residual spectral power", "bounded01": False,
    },
    "LRA": {
        "name": "Law & Rights Alignment", "agent": "Stone", "tier": "sovereign_body",
        "numerator": "rights-consistent rulings / actions",
        "denominator": "total rulings / actions", "bounded01": True,
    },
    "DFR": {
        "name": "Debt Freedom Ratio", "agent": "Ember", "tier": "sovereign_body",
        "numerator": "income free of debt service",
        "denominator": "total income", "bounded01": True,
    },
    "CCI": {
        "name": "Cultural Coherence Index", "agent": "Cedar", "tier": "sovereign_body",
        "numerator": "shared / actively-practiced cultural assets",
        "denominator": "total cultural assets at risk", "bounded01": True,
    },
    "SPR": {
        "name": "Strategic Preparedness Ratio", "agent": "Summit", "tier": "sovereign_body",
        "numerator": "scenarios with a rehearsed response",
        "denominator": "total identified scenarios", "bounded01": True,
    },
    # ---- 12 Resource Realms -------------------------------------------------
    "EAR": {
        "name": "Energy Autonomy Ratio", "agent": "Sol", "tier": "resource_realm",
        "numerator": "local regenerative energy (kWh)",
        "denominator": "total energy demand (kWh)", "bounded01": False,
    },
    "WSI": {
        "name": "Water Sovereignty Index", "agent": "Tide", "tier": "resource_realm",
        "numerator": "locally regenerated water (L)",
        "denominator": "total water consumed (L)", "bounded01": False,
    },
    "LNR": {
        "name": "Local Nutrition Ratio", "agent": "Root", "tier": "resource_realm",
        "numerator": "locally produced nutrition (kcal)",
        "denominator": "total nutrition consumed (kcal)", "bounded01": True,
    },
    "WAI": {
        "name": "Wellness & Access Index", "agent": "Heal", "tier": "resource_realm",
        "numerator": "needs met by local care capacity",
        "denominator": "total care needs", "bounded01": True,
    },
    "HIS": {
        "name": "Housing Integrity & Security", "agent": "Haven", "tier": "resource_realm",
        "numerator": "secure, healthy dwellings",
        "denominator": "total dwellings needed", "bounded01": True,
    },
    "CI": {
        "name": "Circularity Index", "agent": "Cycle", "tier": "resource_realm",
        "numerator": "material recovered / reused (kg)",
        "denominator": "total material throughput (kg)", "bounded01": True,
    },
    "KLI": {
        "name": "Knowledge & Learning Index", "agent": "Lore", "tier": "resource_realm",
        "numerator": "learners meeting learning goals",
        "denominator": "total learners", "bounded01": True,
    },
    "FFR": {
        "name": "Free Flow of Information Ratio", "agent": "Mesh", "tier": "resource_realm",
        "numerator": "reachable nodes under stress test",
        "denominator": "total nodes", "bounded01": True,
    },
    "MAF": {
        "name": "Mobility & Access Factor", "agent": "Passage", "tier": "resource_realm",
        "numerator": "trips served by local/regenerative mobility",
        "denominator": "total essential trips", "bounded01": True,
    },
    "RPR": {
        "name": "Regenerative Production Ratio", "agent": "Forge", "tier": "resource_realm",
        "numerator": "goods made from local/regenerative inputs",
        "denominator": "total goods produced", "bounded01": True,
    },
    "AFI": {
        "name": "Abundance & Fairness Index", "agent": "Thrive", "tier": "resource_realm",
        "numerator": "value circulating within the community",
        "denominator": "total value generated", "bounded01": True,
    },
    "JCI": {
        "name": "Just Coordination Index", "agent": "Council", "tier": "resource_realm",
        "numerator": "decisions with legitimate participation",
        "denominator": "total decisions", "bounded01": True,
    },
}

# Dedicated calculators wired to registry keys where they exist.
_DEDICATED: Dict[str, Callable[[float, float], Dict[str, Any]]] = {
    "EAR": lambda n, d: calculate_ear(n, d),
    "WSI": lambda n, d: calculate_wsi(n, d),
    "LNR": lambda n, d: calculate_lnr(n, d),
    "DFR": lambda n, d: calculate_dfr(d, n) if False else _dfr_adapter(n, d),
    "HRVcoh": lambda n, d: coherence_ratio(n, n + d),
}


def _dfr_adapter(income_free: float, total_income: float) -> Dict[str, Any]:
    """Adapt DFR to the numerator/denominator convention (free income / income)."""
    debt_service = max(0.0, float(total_income) - float(income_free))
    return calculate_dfr(debt_service, total_income)


def _generic_ratio(numerator: float, denominator: float, bounded01: bool) -> float:
    if numerator < 0 or denominator < 0:
        raise ValueError("numerator and denominator must be >= 0.")
    denom = max(float(denominator), MIN_DENOM)
    ratio = float(numerator) / denom
    if bounded01:
        return round(min(ratio, 1.0), 4)
    return round(min(ratio, MAX_RATIO), 4)


def list_indexes() -> Dict[str, Dict[str, Any]]:
    """Return the full registry of the 19 domain indexes."""
    return INDEXES


def calculate(index_key: str, numerator: float, denominator: float) -> Dict[str, Any]:
    """Compute any of the 19 domain indexes by key.

    Args:
        index_key:   registry key, e.g. "EAR", "DFR", "JCI".
        numerator:   the regenerative / sovereign quantity.
        denominator: the demand / total quantity.

    Returns:
        dict with: index (key), name, agent, tier, score, bounded01, inputs.
    """
    if index_key not in INDEXES:
        raise KeyError(f"Unknown index '{index_key}'. Known: {sorted(INDEXES)}")
    meta = INDEXES[index_key]

    if index_key in _DEDICATED:
        detail = _DEDICATED[index_key](numerator, denominator)
        # Normalize the various dedicated return shapes to a single score key.
        score = (
            detail.get("ear")
            or detail.get("wsi")
            or detail.get("lnr")
            or detail.get("dfr")
            or detail.get("hrv_coherence")
        )
        if score is None:
            score = _generic_ratio(numerator, denominator, meta["bounded01"])
    else:
        score = _generic_ratio(numerator, denominator, meta["bounded01"])
        detail = {"inputs": {"numerator": numerator, "denominator": denominator}}

    return {
        "index": index_key,
        "name": meta["name"],
        "agent": meta["agent"],
        "tier": meta["tier"],
        "score": score,
        "bounded01": meta["bounded01"],
        "detail": detail,
    }


def calculate_all(inputs: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Compute a batch of indexes.

    Args:
        inputs: mapping index_key -> {"numerator": x, "denominator": y}.

    Returns:
        mapping index_key -> result dict from calculate().
    """
    results = {}
    for key, vals in inputs.items():
        results[key] = calculate(key, vals["numerator"], vals["denominator"])
    return results


def _demo() -> None:
    print("Peace Protocols — 19 domain indexes registry")
    print(f"  registered indexes: {len(INDEXES)}")
    sample = {
        "EAR": {"numerator": 4200, "denominator": 5800},
        "JCI": {"numerator": 42, "denominator": 50},
        "DFR": {"numerator": 4800, "denominator": 8000},
        "HRVcoh": {"numerator": 0.62, "denominator": 0.38},
    }
    for key, res in calculate_all(sample).items():
        print(f"  {key:<7} {res['name']:<32} score={res['score']} ({res['agent']})")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        assert len(INDEXES) == 19, f"expected 19 indexes, got {len(INDEXES)}"
        # 7 sovereign bodies + 12 resource realms.
        sb = [k for k, v in INDEXES.items() if v["tier"] == "sovereign_body"]
        rr = [k for k, v in INDEXES.items() if v["tier"] == "resource_realm"]
        assert len(sb) == 7, sb
        assert len(rr) == 12, rr
        assert calculate("JCI", 25, 100)["score"] == 0.25
        assert calculate("EAR", 100, 100)["score"] == 1.0
        assert calculate("LNR", 200, 100)["score"] == 1.0  # bounded
        print("all_indexes self-test passed. Run with --demo for a worked example.")
