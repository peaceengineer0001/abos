#!/usr/bin/env python3
"""Heart-Rate-Variability Coherence (HRVcoh) — Sovereign Body: River 💧.

River tracks the physiological coherence of the community's people as a
leading indicator of collective nervous-system regulation. HRV coherence is
computed from the power spectrum of an inter-beat-interval (IBI) time series
as the ratio of power concentrated in the coherence band to the surrounding
spectrum — the standard HeartMath-style coherence ratio:

    HRVcoh = P_coherence / (P_total - P_coherence)

where
    P_coherence = spectral power in the coherence band (~0.04-0.26 Hz,
                  peak near 0.1 Hz), i.e. the height of the coherence peak
    P_total     = total spectral power across the analyzed band

A higher ratio indicates a more ordered, sine-like HRV rhythm (parasympathetic
regulation, calm-alert states). The community aggregate is the mean of
individual coherence scores across consenting, privacy-tiered contributors.

This module provides two entry points:
    * coherence_ratio()      — from pre-computed band powers.
    * coherence_from_ibi()   — from a raw IBI series (uses a lightweight
                               periodogram; no third-party dependencies).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

COHERENCE_BAND = (0.04, 0.26)  # Hz
MIN_POWER = 1e-12


def coherence_ratio(p_coherence: float, p_total: float) -> Dict[str, Any]:
    """Coherence ratio from pre-computed spectral band powers.

    Args:
        p_coherence: power within the coherence band (>= 0).
        p_total:     total spectral power (>= p_coherence, > 0).

    Returns:
        dict with keys: hrv_coherence, coherence_fraction, inputs.
    """
    if p_coherence < 0 or p_total < 0:
        raise ValueError("powers must be >= 0.")
    if p_coherence > p_total + MIN_POWER:
        raise ValueError("p_coherence cannot exceed p_total.")

    residual = max(p_total - p_coherence, MIN_POWER)
    ratio = p_coherence / residual
    return {
        "hrv_coherence": round(ratio, 4),
        "coherence_fraction": round(p_coherence / max(p_total, MIN_POWER), 4),
        "inputs": {"p_coherence": p_coherence, "p_total": p_total},
    }


def _periodogram(signal: Sequence[float], fs: float) -> List[tuple]:
    """Naive DFT periodogram -> list of (freq_hz, power). Pure Python."""
    n = len(signal)
    mean = sum(signal) / n
    centered = [s - mean for s in signal]
    spectrum = []
    # Only need frequencies up to Nyquist for a real signal.
    for k in range(1, n // 2 + 1):
        re = im = 0.0
        for t, x in enumerate(centered):
            angle = -2.0 * math.pi * k * t / n
            re += x * math.cos(angle)
            im += x * math.sin(angle)
        power = (re * re + im * im) / n
        freq = k * fs / n
        spectrum.append((freq, power))
    return spectrum


def coherence_from_ibi(ibi_ms: Sequence[float]) -> Dict[str, Any]:
    """Estimate HRV coherence from a raw inter-beat-interval series.

    Args:
        ibi_ms: inter-beat intervals in milliseconds (>= 8 samples).

    Returns:
        dict from coherence_ratio() plus the estimated sampling rate.
    """
    if len(ibi_ms) < 8:
        raise ValueError("need at least 8 IBI samples to estimate coherence.")
    mean_ibi_s = (sum(ibi_ms) / len(ibi_ms)) / 1000.0
    fs = 1.0 / mean_ibi_s  # effective sampling rate in Hz (beats/sec)

    spectrum = _periodogram(ibi_ms, fs)
    p_total = sum(p for _, p in spectrum)
    p_coh = sum(p for f, p in spectrum if COHERENCE_BAND[0] <= f <= COHERENCE_BAND[1])
    out = coherence_ratio(p_coh, p_total if p_total > 0 else MIN_POWER)
    out["sampling_rate_hz"] = round(fs, 4)
    return out


def _demo() -> None:
    result = coherence_ratio(p_coherence=0.62, p_total=1.0)
    print("HRV Coherence (HRVcoh) — demo")
    print(f"  hrv_coherence      = {result['hrv_coherence']}")
    print(f"  coherence_fraction = {result['coherence_fraction']}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    else:
        assert coherence_ratio(0.5, 1.0)["hrv_coherence"] == 1.0
        assert coherence_ratio(0.0, 1.0)["hrv_coherence"] == 0.0
        # With ~800 ms mean IBI the effective sampling rate is ~1.25 Hz, so a
        # rhythm with a period of ~12 samples lands near 0.1 Hz — inside the
        # coherence band — and should read as highly coherent.
        sine = [800 + 40 * math.sin(2 * math.pi * i / 12.0) for i in range(96)]
        coh = coherence_from_ibi(sine)
        assert coh["hrv_coherence"] > 0.5, coh
        print("hrv_calculator self-test passed. Run with --demo for a worked example.")
