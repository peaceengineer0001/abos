"""Peace Protocols — domain index calculators.

This package holds the 19 domain-index calculators (7 Sovereign Bodies +
12 Resource Realms). The two master metrics (Pe, CVI) and the stability
metric (Sr) live one level up in the ``math`` package.

Use :mod:`all_indexes` for a unified interface:

    from math.index_calculators.all_indexes import calculate, list_indexes
"""

from .ear_calculator import calculate_ear
from .wsi_calculator import calculate_wsi
from .lnr_calculator import calculate_lnr
from .dfr_calculator import calculate_dfr
from .hrv_calculator import coherence_ratio, coherence_from_ibi
from .all_indexes import calculate, calculate_all, list_indexes, INDEXES

__all__ = [
    "calculate_ear",
    "calculate_wsi",
    "calculate_lnr",
    "calculate_dfr",
    "coherence_ratio",
    "coherence_from_ibi",
    "calculate",
    "calculate_all",
    "list_indexes",
    "INDEXES",
]
