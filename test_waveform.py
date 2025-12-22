"""Moku:Go AWG script (selectable waveform).

Waveform generation lives in `waveforms.py`.
Device programming/run helpers live in `moku_awg.py`.
"""

from __future__ import annotations

import numpy as np
from dotenv import load_dotenv
import os
from moku_awg import program_awg_indefinitely
from plotting import plot_step
from config_uitl import get_env_bool, get_env_float, get_env_int, get_env_str
from waveforms import (
    RamseyParams,
    SquareWaveParams,
    build_gaussian_ramsey_lut,
    build_square_lut,
)


def _build_selected_waveform(waveform: str, *, N: int):
    """Return (t_s, lut, f_rep, bounds, title)."""

    key = str(waveform).strip().lower()

    match key:
        case "gaussian" | "gaussian_ramsey" | "ramsey" | "gaussian-ramsey":
            params = RamseyParams(
                t_pi2_s=get_env_float("T_PI2_S", 100e-9),
                tau_s=get_env_float("TAU_S", 4.9e-6),
            )
            sigma_frac = get_env_float("SIGMA_FRAC", 0.25)
            amp = get_env_float("WAVE_AMP", 1.0)

            t_s, lut, f_rep, bounds = build_gaussian_ramsey_lut(
                params,
                N=int(N),
                sigma_frac=float(sigma_frac),
                amp=float(amp),
            )
            title = f"Gaussian τ–π/2–τ–π/2 (f_rep={f_rep/1e3:.2f} kHz)"
            return t_s, lut, f_rep, bounds, title

        case "square" | "sq":
            params = SquareWaveParams(
                f_rep_hz=get_env_float("F_REP_HZ", 1e3),
                duty=get_env_float("DUTY", 0.5),
                high=get_env_float("HIGH", 1.0),
                low=get_env_float("LOW", -1.0),
            )
            t_s, lut, f_rep, bounds = build_square_lut(params, N=int(N))
            title = f"Square wave (f_rep={f_rep/1e3:.2f} kHz, duty={params.duty:.3f})"
            return t_s, lut, f_rep, bounds, title

        case _:
            raise ValueError(
                "Unsupported WAVEFORM. Use one of: gaussian_ramsey, square. "
                f"Got: {waveform!r}"
            )


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    # read MOKU_IP from .env or set it here directly
    load_dotenv()
    MOKU_IP = get_env_str("MOKU_IP", "169.254.77.89")   # your device ip address
    CHANNEL = get_env_int("CHANNEL", 1)
    VPP = get_env_float("VPP", 1.0)
    N = get_env_int("N", 2048)

    waveform = get_env_str("WAVEFORM", "gaussian_ramsey") or "gaussian_ramsey"

    # Build waveform LUT (Look Up Table)
    t_s, lut, f_rep, bounds, title = _build_selected_waveform(waveform, N=int(N))

    print(f"Repetition frequency = {f_rep/1e3:.3f} kHz")

    # Optional plot
    PLOT = get_env_bool("PLOT_WAVEFORMS", True)
    if PLOT:
        plot_step(
            t_s,
            lut,
            x_scale=1e6,
            y_scale=(VPP / 2.0),
            x_label="Time (µs)",
            y_label="Voltage (V)",
            title=title,
            boundaries_x=bounds,
        )

    # A) Fire-and-forget, relinquish immediately (wave keeps running):
    program_awg_indefinitely(
        MOKU_IP,
        channel=CHANNEL,
        lut=lut,
        f_rep_hz=f_rep,
        vpp=VPP,
        sample_rate="Auto",
    )


if __name__ == "__main__":
    main()
