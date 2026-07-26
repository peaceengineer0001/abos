# 📊 The Resilience Delta (Sr)

The **Resilience Delta (Sr)** measures whether a community is getting *more* or *less* resilient over time. Where [CVI](community-vitality-index.md) is a snapshot *level* of vitality, **Sr is the net rate of change of coherence under shocks** — the signal Raven watches to know whether the community's vitality trajectory is drifting up or down.

---

## The Formula

```
Sr = ΔC_pos − ΔC_neg
```

| Symbol | Meaning |
|---|---|
| **ΔC_pos** | Coherence **gained** from positive interventions (coherence shocks Raven engineers: celebrations, shared milestones, surplus-sharing) |
| **ΔC_neg** | Coherence **lost** from negative shocks (external disruptions, conflicts, supply failures, setbacks) |
| **Sr** | Net resilience change over the measurement window |

---

## Interpretation

- **Sr > 0** → positive interventions outweigh negative shocks. The community's CVI trajectory **drifts upward**. This is the target state.
- **Sr = 0** → coherence gains and losses balance. The community holds steady but is not building resilience.
- **Sr < 0** → shocks outpace interventions. Coherence is eroding; Raven escalates and schedules corrective coherence shocks.

**Raven's mandate:** keep **Sr > 0 on average** across measurement windows. As long as the average Resilience Delta is positive, the [Stability Theorem](stability-theorem.md) guarantees the system keeps moving toward the Abundance Equilibrium.

---

## Where the Two Terms Come From

### ΔC_pos — Engineered Coherence Shocks
Raven deliberately schedules positive shocks and measures the coherence bump around each one (the change in CVI / κ in the days following the event):

- Milestone celebrations (e.g., "first debt-free member," "microgrid online")
- Community events and shared rituals (Starfire, Cedar)
- Surplus-sharing and mutual-aid distributions (Thrive, Ember)
- Synchronization moments across scope levels

Each is emitted as a Kind `30105` Coherence Shock event with an expected and a measured `delta`. See [`workflows/coherence-shock-event.yaml`](../../workflows/coherence-shock-event.yaml).

### ΔC_neg — Observed Negative Shocks
The DEFEND phase of the [6D loop](../6d-framework.md) detects negative shocks — index regressions, external disruptions, conflicts — and estimates their coherence cost from the corresponding drop in domain indices and CVI.

---

## Implementation Guide

The reference calculator is [`math/sr_calculator.py`](../../math/sr_calculator.py). It accepts lists of positive and negative coherence changes over a window and returns the net Sr plus a trajectory verdict.

```python
from math.sr_calculator import calculate_sr

result = calculate_sr(
    positive_shocks=[0.05, 0.03, 0.08],   # ΔC_pos contributions (e.g., celebrations)
    negative_shocks=[0.02, 0.06],         # ΔC_neg contributions (e.g., a supply disruption)
)

print(result["sr"])            # net Resilience Delta
print(result["delta_pos"])     # summed positive coherence
print(result["delta_neg"])     # summed negative coherence
print(result["trajectory"])    # "rising" | "steady" | "eroding"
```

Run the demo:

```bash
python3 math/sr_calculator.py --demo
```

---

## How Raven Uses Sr

1. **Weekly synthesis:** Sr is reported alongside Pe and CVI in the [weekly report](../../workflows/weekly-pe-cvi-report.yaml).
2. **Shock scheduling:** if Sr trends toward zero or negative, Raven proactively schedules coherence shocks to restore `ΔC_pos > ΔC_neg`.
3. **Early warning:** a sustained negative Sr is Raven's earliest signal that the community risks leaving the abundance basin — triggering cross-domain DEFEND coordination before any single index collapses.

---

## Relationship to the Other Metrics

| Metric | Question it answers | Time character |
|---|---|---|
| [Pe](peace-efficiency-index.md) | How resource-sovereign are we? | Level |
| [CVI](community-vitality-index.md) | How vital are we right now? | Level |
| **Sr** | Are we getting more or less resilient? | **Rate of change** |

Together, Pe and CVI tell you *where you are*; **Sr tells you where you're headed** — and gives Raven the lever (coherence shocks) to change the heading.
