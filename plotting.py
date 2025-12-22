"""Generic plotting helpers for scripts in this repo."""

from __future__ import annotations

from typing import Iterable, Optional

import numpy as np


def plot_step(
    x: np.ndarray,
    y: np.ndarray,
    *,
    x_scale: float = 1.0,
    y_scale: float = 1.0,
    x_label: str = "x",
    y_label: str = "y",
    title: str = "",
    boundaries_x: Optional[Iterable[float]] = None,
    where: str = "post",
    show: bool = True,
) -> None:
    """Generic step plot.

    - x/y: arrays to plot
    - x_scale/y_scale: scale factors applied before plotting
    - boundaries_x: optional x positions to mark (in same units as x)
    """

    import matplotlib.pyplot as plt

    x = np.asarray(x, dtype=float) * float(x_scale)
    y = np.asarray(y, dtype=float) * float(y_scale)

    plt.figure(figsize=(9, 3))
    plt.step(x, y, where=where)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if title:
        plt.title(title)
    plt.grid(True, alpha=0.3)

    if boundaries_x:
        for boundary in boundaries_x:
            plt.axvline(float(boundary) * float(x_scale), linestyle="--", linewidth=1)

    plt.tight_layout()
    if show:
        plt.show()
    else:
        plt.close()
