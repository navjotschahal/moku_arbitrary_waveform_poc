"""Moku:Go Arbitrary Waveform Generator (AWG) control helpers."""

from __future__ import annotations

import numpy as np
from moku.instruments import ArbitraryWaveformGenerator


def program_awg_indefinitely(
    moku_ip: str,
    *,
    channel: int,
    lut: np.ndarray,
    f_rep_hz: float,
    vpp: float,
    sample_rate: str | float = "Auto",
) -> None:
    """Program the AWG, then relinquish ownership immediately.

    The waveform continues running indefinitely on the device.
    """

    awg = ArbitraryWaveformGenerator(moku_ip, force_connect=True)
    try:
        awg.generate_waveform(
            channel=int(channel),
            sample_rate=sample_rate,
            lut_data=np.asarray(lut).tolist(),
            frequency=float(f_rep_hz),
            amplitude=float(vpp),
        )
        print(
            f"AWG CH{int(channel)} running indefinitely: "
            f"f_rep={float(f_rep_hz)/1e3:.3f} kHz, Vpp={float(vpp):.3f} V"
        )
        print("Relinquishing ownership now (GUI/other apps can take control).")
    finally:
        awg.relinquish_ownership()
        print("Ownership relinquished.")
