"""
abos.templates
==============

Loader for the six business-model templates. Each YAML file pre-configures the
priority agents, KPIs, workflows, rubric weight overrides, required filings, and
evidence focus for a business type.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, List

import yaml

_DIR = os.path.dirname(__file__)

BUSINESS_TYPES = [
    "saas_startup",
    "boutique_agency",
    "marine_services",
    "restaurant_group",
    "retail_brand",
    "professional_services",
]


@lru_cache(maxsize=None)
def load_template(business_type: str) -> Dict[str, Any]:
    """Load and cache one business-model template."""
    if business_type not in BUSINESS_TYPES:
        raise KeyError(f"unknown business_type '{business_type}'. "
                       f"Choose from {BUSINESS_TYPES}")
    path = os.path.join(_DIR, f"{business_type}.yaml")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def list_templates() -> List[Dict[str, Any]]:
    """Return a summary of all templates (for the API / demo picker)."""
    out = []
    for bt in BUSINESS_TYPES:
        t = load_template(bt)
        out.append({
            "business_type": bt,
            "display_name": t.get("display_name", bt),
            "description": (t.get("description", "") or "").strip(),
            "kpi_count": len(t.get("kpis", [])),
            "priority_agents": t.get("priority_agents", []),
        })
    return out


def rubric_for(business_type: str) -> List[Dict[str, Any]]:
    """Return the BOSS rubric with this template's weight overrides applied
    (renormalized to sum to 1.0)."""
    from ..core.scorecard import DEFAULT_RUBRIC

    template = load_template(business_type)
    overrides = template.get("rubric_overrides", {}) or {}
    rubric = [dict(m) for m in DEFAULT_RUBRIC]
    for m in rubric:
        if m["key"] in overrides:
            m["weight"] = float(overrides[m["key"]])
    total = sum(m["weight"] for m in rubric)
    if total > 0:
        for m in rubric:
            m["weight"] = round(m["weight"] / total, 4)
    return rubric


__all__ = ["BUSINESS_TYPES", "load_template", "list_templates", "rubric_for"]
