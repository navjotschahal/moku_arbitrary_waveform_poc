"""Waveform generation helpers used by the Moku AWG scripts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


def make_time_axis(T_rep_s: float, N: int, *, endpoint: bool = False) -> np.ndarray:
    """Create a uniform time axis for one LUT period."""

    if int(N) <= 0:
        raise ValueError("N must be positive")
    T_rep_s = float(T_rep_s)
    if not np.isfinite(T_rep_s) or T_rep_s <= 0.0:
        raise ValueError("T_rep_s must be finite and > 0")
    return np.linspace(0.0, T_rep_s, int(N), endpoint=bool(endpoint))


def waveform_to_lut(
    wave: np.ndarray,
    *,
    normalize: str = "peak",
    clip: bool = True,
) -> np.ndarray:
    """Convert waveform samples into a normalized LUT in [-1, 1].

    This is waveform-agnostic: waveform generators produce `wave`, and this
    handles LUT normalization/clipping.
    """

    wave = np.asarray(wave, dtype=float)
    strategy = str(normalize).lower().strip()

    if strategy == "peak":
        peak = float(np.max(np.abs(wave))) if wave.size else 0.0
        if not np.isfinite(peak) or peak <= 0.0:
            raise ValueError("Waveform peak is zero or non-finite; cannot normalize.")
        lut = wave / peak
    elif strategy in {"none", "off", "false"}:
        lut = wave
    else:
        raise ValueError(f"Unsupported normalize strategy: {normalize!r}")

    if clip:
        lut = np.clip(lut, -1.0, 1.0)
    return lut


def gaussian_pulse(
    t_s: np.ndarray,
    *,
    t_center_s: float,
    sigma_s: float,
    amp: float = 1.0,
) -> np.ndarray:
    """Gaussian envelope pulse.
    Function is amp * exp(-0.5 * ((t - t_center) / sigma) ** 2)
    Returns array of same shape as t_s.

    t_s: time axis (seconds)
    t_center_s: center time (seconds)
    sigma_s: standard deviation (seconds)
    amp: peak amplitude
    """

    t_s = np.asarray(t_s)
    return float(amp) * np.exp(-0.5 * ((t_s - float(t_center_s)) / float(sigma_s)) ** 2)


@dataclass(frozen=True)
class RamseyParams:
    """τ–π/2–τ–π/2 (Ramsey-like) timing parameters."""

    t_pi2_s: float = 100e-9
    tau_s: float = 4.9e-6


@dataclass(frozen=True)
class SquareWaveParams:
    """Basic square wave parameters for LUT generation."""

    f_rep_hz: float = 1e3
    duty: float = 0.5
    high: float = 1.0
    low: float = -1.0


def build_gaussian_ramsey_lut(
    params: RamseyParams,
    *,
    N: int = 2048,
    sigma_frac: float = 0.25,  # sigma = sigma_frac * t_pi2
    amp: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray, float, Tuple[float, float, float, float]]:
    """Build one-period LUT for Gaussian τ–π/2–τ–π/2.

    Returns:
      t_s: time axis (seconds)
      lut: normalized LUT in [-1, 1]
      f_rep: repetition frequency (Hz)
      boundaries: (t1, t2, t3, t4) segment boundaries in seconds
    """

    t_pi2 = float(params.t_pi2_s)
    tau = float(params.tau_s)

    T_rep = 2.0 * tau + 2.0 * t_pi2
    f_rep = 1.0 / T_rep

    t_s = make_time_axis(T_rep, int(N), endpoint=False)

    # Segment boundaries
    t0 = 0.0
    t1 = t0 + tau
    t2 = t1 + t_pi2
    t3 = t2 + tau
    t4 = t3 + t_pi2  # == T_rep

    sigma = float(sigma_frac) * t_pi2

    wave = np.zeros_like(t_s)
    wave += gaussian_pulse(t_s, t_center_s=(t1 + t2) / 2.0, sigma_s=sigma, amp=amp)
    wave += gaussian_pulse(t_s, t_center_s=(t3 + t4) / 2.0, sigma_s=sigma, amp=amp)

    lut = waveform_to_lut(wave, normalize="peak", clip=True)

    return t_s, lut, f_rep, (t1, t2, t3, t4)


def build_square_lut(
    params: SquareWaveParams,
    *,
    N: int = 2048,
    normalize: str = "peak",
) -> Tuple[np.ndarray, np.ndarray, float, Tuple[float]]:
    """Build one-period LUT for a basic square wave.

    Returns:
      t_s: time axis (seconds)
      lut: normalized LUT in [-1, 1]
      f_rep: repetition frequency (Hz)
      boundaries: (t_high_end,) where the waveform transitions high→low
    """

    f_rep = float(params.f_rep_hz)
    if not np.isfinite(f_rep) or f_rep <= 0.0:
        raise ValueError("f_rep_hz must be finite and > 0")
    duty = float(params.duty)
    if not np.isfinite(duty) or duty < 0.0 or duty > 1.0:
        raise ValueError("duty must be in [0, 1]")

    T_rep = 1.0 / f_rep
    t_s = make_time_axis(T_rep, int(N), endpoint=False)

    t_high_end = duty * T_rep
    wave = np.where(t_s < t_high_end, float(params.high), float(params.low))
    lut = waveform_to_lut(wave, normalize=str(normalize), clip=True)

    return t_s, lut, f_rep, (t_high_end,)
