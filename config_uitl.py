"""Small helpers for reading typed values from environment variables.

These functions intentionally do not call `load_dotenv()`; callers should do
that once at program startup.
"""

from __future__ import annotations

import os


_TRUE = {"1", "true", "t", "yes", "y", "on"}
_FALSE = {"0", "false", "f", "no", "n", "off"}


def get_env_str(name: str, default: str | None = None, *, strip: bool = True) -> str | None:
    """Read an env var as a string.

    Returns `default` if the variable is unset or empty.
    """

    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw.strip() if strip else raw


def get_env_int(name: str, default: int, *, base: int = 10) -> int:
    """Read an env var as an int (supports e.g. "123")."""

    raw = get_env_str(name, None)
    if raw is None:
        return int(default)
    return int(raw, base)


def get_env_float(name: str, default: float) -> float:
    """Read an env var as a float (supports e.g. "1e-3")."""

    raw = get_env_str(name, None)
    if raw is None:
        return float(default)
    return float(raw)


def get_env_bool(name: str, default: bool = False) -> bool:
    """Read an env var as a bool.

    Accepts: 1/0, true/false, yes/no, on/off (case-insensitive).
    Returns `default` if unset/empty.
    """

    raw = get_env_str(name, None)
    if raw is None:
        return bool(default)

    v = raw.lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False

    raise ValueError(
        f"Invalid boolean for {name!r}: {raw!r} (use one of: {sorted(_TRUE | _FALSE)})"
    )
