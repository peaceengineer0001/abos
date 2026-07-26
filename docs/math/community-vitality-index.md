# 📊 The Community Vitality Index (CVI)

The **Community Vitality Index (CVI)** is the second master metric of the Peace Protocols (alongside the [Peace Efficiency Index](peace-efficiency-index.md)). Where Pe measures *resource sovereignty* across the 12 realms, CVI measures the **lived vitality** of the community — the balance between the forces that generate life and the forces that deplete it.

Raven calculates CVI by synthesizing data from across the 7 Sovereign Bodies and 12 Resource Realms.

---

## The Formula

```
CVI = (H + Dg + F) / (S + Db + De)
```

### Numerator — Vitality Drivers

| Symbol | Name | Meaning | Sourced from |
|---|---|---|---|
| **H** | Health | Preventive + regenerative health capacity | Heal (WAI) |
| **Dg** | Dignity | Cultural integrity + social inclusion | Cedar (CCI) + Summit (SPR) |
| **F** | Freedom | Political agency + economic autonomy | Summit (SPR) + Ember (DFR) |

### Denominator — Depletion Drivers

| Symbol | Name | Meaning | Sourced from |
|---|---|---|---|
| **S** | Scarcity | Inverse of resource autonomy | Stone (LRA) + realm sovereignty scores |
| **Db** | Debt burden | Financial extraction load | Ember (DFR) |
| **De** | Dependency | Aggregate of all realm dependency factors | Σ Dᵢ across the 12 realms |

---

## Interpretation

CVI is a **ratio of vitality to depletion**:

- **CVI > 1** → the community generates more vitality than it loses. It is **thriving** and trending toward abundance.
- **CVI = 1** → break-even. Vitality drivers exactly offset depletion drivers.
- **CVI < 1** → depletion outpaces vitality. The community is **extracting from itself** and needs intervention.

Because vitality and depletion are each sums of three commensurable inputs, CVI is robust to a single weak signal: a community can be low on Health but still thrive if Dignity and Freedom are strong and Scarcity, Debt, and Dependency are low.

---

## How the Six Inputs Are Derived

Raven does not ask for CVI inputs directly — it **synthesizes** them from the domain agents' indices, each normalized to a comparable scale:

```
H  = WAI                              (Heal)          # 0..1 preventive/regen care ratio
Dg = mean(CCI, SPR)                   (Cedar, Summit) # cultural + participation
F  = mean(SPR, DFR)                   (Summit, Ember) # political + economic freedom
S  = 1 − LRA                          (Stone)         # scarcity = inverse resource autonomy
Db = 1 − DFR                          (Ember)         # debt burden = inverse debt freedom
De = mean(Dᵢ_norm) over 12 realms     (all realms)    # normalized aggregate dependency
```

This means **every domain agent contributes to CVI**, directly or indirectly — which is why Raven can trace any change in CVI back to a specific realm or body and recommend the highest-leverage next action.

---

## Guarding Against Division Blow-Up

The denominator `(S + Db + De)` is clamped to a small positive floor (`ε`) so that a near-zero-depletion community produces a large-but-finite CVI rather than a divide-by-zero. All six inputs are validated to be non-negative before the ratio is computed.

---

## Implementation Guide

The reference calculator is [`math/cvi_calculator.py`](../../math/cvi_calculator.py).

```python
from math.cvi_calculator import calculate_cvi

result = calculate_cvi(
    H=0.62,    # Health (WAI)
    Dg=0.55,   # Dignity (mean CCI, SPR)
    F=0.48,    # Freedom (mean SPR, DFR)
    S=0.40,    # Scarcity (1 - LRA)
    Db=0.30,   # Debt burden (1 - DFR)
    De=0.50,   # Dependency (mean normalized Dᵢ)
)

print(result["cvi"])          # the Community Vitality Index
print(result["status"])       # "thriving" | "break-even" | "depleting"
print(result["breakdown"])    # numerator / denominator components
```

You can also let Raven derive the six inputs from raw domain indices:

```python
from math.cvi_calculator import derive_cvi_from_indices

result = derive_cvi_from_indices(
    WAI=0.62, CCI=0.58, SPR=0.52, DFR=0.70, LRA=0.60,
    realm_dependencies=[0.4, 0.5, 0.6, 0.5, 0.4, 0.3, 0.5, 0.2, 0.6, 0.7, 0.5, 0.5],
)
print(result["cvi"], result["status"])
```

Run the demo:

```bash
python3 math/cvi_calculator.py --demo
```

---

## CVI and the Resilience Delta

CVI is a *level*; the [Resilience Delta (Sr)](resilience-delta.md) is its *rate of change* under shocks. Raven engineers positive **coherence shocks** (celebrations, shared milestones, surplus-sharing) to keep `Sr > 0` on average, which drives the CVI trajectory upward over time — the operational path toward the [Abundance Equilibrium](stability-theorem.md).
