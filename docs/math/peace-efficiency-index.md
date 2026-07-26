# 📊 The Peace Efficiency Index (Pe)

The **Peace Efficiency Index (Pe)** is one of the two master metrics of the Peace Protocols (the other is the [Community Vitality Index](community-vitality-index.md)). It answers a single question: *How much of what this community needs does it regenerate for itself, relative to how much it depends on centralized, extractive provisioning?*

Raven calculates Pe by summing the regenerative-over-dependency ratio across all **12 Resource Realms**.

---

## The Formula

```
Pe = Σ (Rᵢ / Dᵢ)     for i = 1 .. 12
```

| Symbol | Meaning |
|---|---|
| **Rᵢ** | Regenerative output of realm *i* (kWh of local energy, liters of harvested water, kcal of local food, etc.) |
| **Dᵢ** | Dependency factor of realm *i* on centralized / imported provisioning (**Dᵢ > 0**) |
| **i = 1..12** | the 12 Resource Realms: Energy, Water, Food, Health, Shelter, Waste, Education, Communication, Transportation, Manufacturing, Economics, Governance |

**Direction:** Pe **rises** when local regenerative output (Rᵢ) rises **or** when dependency (Dᵢ) falls. Both levers matter — you can raise Pe by producing more locally *or* by needing less from the outside.

---

## The 12 Realm Terms

Each Resource-Realm agent computes its own `Rᵢ / Dᵢ` term and publishes it as a Kind `30102` Domain Index event. Raven sums the 12 terms.

| i | Realm | Agent | Index | Term |
|---|---|---|---|---|
| 1 | Energy | Sol | EAR | E_local / E_dependency |
| 2 | Water | Tide | WSI | W_regen / W_dependency |
| 3 | Food | Root | LNR | Food_local / Food_dependency |
| 4 | Health | Heal | WAI | care_regen / care_dependency |
| 5 | Shelter | Haven | HIS | units_regen / units_dependency |
| 6 | Waste | Cycle | CI | reused / discarded |
| 7 | Education | Lore | KLI | empowered / dependency |
| 8 | Communication | Mesh | FFR | unrestricted / restricted |
| 9 | Transportation | Passage | MAF | sustainable / dependency |
| 10 | Manufacturing | Forge | RPR | local_prod / import_dependency |
| 11 | Economics | Thrive | AFI | value_created / debt_issued |
| 12 | Governance | Council | JCI | equity_decisions / dependency |

---

## Derivation & Interpretation

Each term `Rᵢ / Dᵢ` is a **dimensionless sovereignty ratio** for one realm:

- **Rᵢ / Dᵢ = 1** → the realm regenerates exactly as much as it depends on. Break-even sovereignty.
- **Rᵢ / Dᵢ > 1** → the realm is a **net regenerator** (produces surplus sovereignty).
- **Rᵢ / Dᵢ < 1** → the realm is **net dependent** (vulnerable to supply shocks).

Because Pe is a **sum of 12 ratios**, a fully break-even community scores **Pe = 12**. Scores above 12 indicate net-regenerative sovereignty overall; scores below 12 indicate net dependency. Raven reports both the total Pe and the per-realm breakdown so you can see exactly where the weakness (the "fuel barge") is.

> **Why a sum, not an average?** Summing preserves the signal from strong realms and makes the total responsive to improvement in *any* realm — every sovereignty gain, anywhere, moves the master metric. Raven also reports the **normalized** form `Pe / 12` when a 0–1 style score is more intuitive for a given scope.

---

## Guarding Against Division Blow-Up

Since `Dᵢ` is a denominator, the calculator enforces **Dᵢ > 0** and clamps extreme ratios so a single near-zero dependency can't dominate the sum. See the implementation for the exact clamping and validation rules.

---

## Implementation Guide

The reference calculator is [`math/pe_calculator.py`](../../math/pe_calculator.py). It accepts the 12 realm inputs and returns the Pe score plus the per-realm breakdown.

```python
from math.pe_calculator import calculate_pe

realms = {
    "energy":         {"R": 4200,  "D": 5800},   # EAR term
    "water":          {"R": 900,   "D": 1100},
    "food":           {"R": 300,   "D": 2200},
    "health":         {"R": 6,     "D": 10},
    "shelter":        {"R": 1,     "D": 1},
    "waste":          {"R": 70,    "D": 30},
    "education":      {"R": 4,     "D": 6},
    "communication":  {"R": 8,     "D": 2},
    "transportation": {"R": 3000,  "D": 9000},
    "manufacturing":  {"R": 2,     "D": 8},
    "economics":      {"R": 1.2,   "D": 1.0},     # AFI term
    "governance":     {"R": 5,     "D": 5},
}

result = calculate_pe(realms)
print(result["pe"])           # total Peace Efficiency Index
print(result["normalized"])   # pe / 12
print(result["breakdown"])    # per-realm ratios, sorted by leverage
```

Run the built-in demo:

```bash
python3 math/pe_calculator.py --demo
```

---

## How Pe Connects to the Rest of the System

- **Cross-realm leverage:** raising Sol's EAR often raises Tide's WSI, Root's LNR, and Passage's MAF simultaneously (energy is upstream of water pumping, food preservation, and mobility). Raven surfaces these couplings so you optimize the highest-leverage realm first.
- **Feeds CVI:** the aggregate dependency term `De` in the [CVI](community-vitality-index.md) is derived from the same `Dᵢ` values used here.
- **Feeds the Stability Theorem:** each realm's ratio corresponds to a sovereignty score `sᵢ`; raising Pe is how the 6D loop pushes the system toward the [Abundance Equilibrium](stability-theorem.md).
