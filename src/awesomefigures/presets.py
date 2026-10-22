"""Named palette presets for repeatable Matplotlib figure styling.

Registrations are in-memory for the active Python process. To persist a
palette, put its register_palette call into a Python module and import it
when initializing a project.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import math
import re

from .contrast import luminance_ladder


@dataclass(frozen=True)
class PalettePreset:
    """Immutable specification of a contrast-controlled plotting palette."""

    name: str
    hues: tuple[float, ...]
    ratio: float
    start_luminance: float
    chroma: float
    markers: tuple[str, ...] | None = None
    linestyles: tuple[object, ...] | None = None


_PRESETS: dict[str, PalettePreset] = {}
_VALID_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,47}$")


def register_palette(
    name: str,
    *,
    hues: Sequence[float],
    ratio: float = 1.5,
    start_luminance: float = 0.95,
    chroma: float = 0.13,
    markers: Sequence[str] | None = None,
    linestyles: Sequence[object] | None = None,
    overwrite: bool = False,
) -> PalettePreset:
    """Register a palette by name for later use by color_palette/plot_scheme.

    Registration lasts for the current Python process. Export the registration
    code to a project module and import that module to reuse it later.
    Existing names require overwrite=True to avoid accidental replacement.
    """
    if not isinstance(name, str) or not _VALID_NAME.fullmatch(name):
        raise ValueError("name must be a valid identifier (letters, digits, underscores; max 48 chars).")
    if isinstance(hues, (str, bytes)):
        raise ValueError("hues must be a sequence of numeric hue angles.")
    try:
        hue_values = tuple(float(value) for value in hues)
    except (TypeError, ValueError) as exc:
        raise ValueError("hues must be a sequence of numeric hue angles.") from exc
    if not hue_values or not all(math.isfinite(h) for h in hue_values):
        raise ValueError("hues must contain finite numeric angles.")

    ratio = float(ratio)
    start_luminance = float(start_luminance)
    chroma = float(chroma)
    if not all(map(math.isfinite, (ratio, start_luminance, chroma))):
        raise ValueError("ratio, start_luminance and chroma must be finite.")
    if chroma < 0:
        raise ValueError("chroma must be non-negative.")
    luminance_ladder(len(hue_values), ratio, start_luminance=start_luminance)

    marker_values = None if markers is None else tuple(markers)
    line_values = None if linestyles is None else tuple(linestyles)
    if marker_values is not None and (not marker_values or any(not isinstance(m, str) or not m for m in marker_values)):
        raise ValueError("markers must contain non-empty Matplotlib marker strings.")
    if line_values is not None and not line_values:
        raise ValueError("linestyles must contain at least one Matplotlib linestyle.")

    if name in _PRESETS and not overwrite:
        raise ValueError(f"Palette {name!r} already exists; pass overwrite=True to replace.")
    preset = PalettePreset(
        name, hue_values, ratio, start_luminance, chroma,
        marker_values, line_values,
    )
    _PRESETS[name] = preset
    return preset


def get_palette(name: str) -> PalettePreset:
    """Return an in-process named palette specification."""
    try:
        return _PRESETS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown palette {name!r}; import its registration module first.") from exc


def available_palettes() -> tuple[str, ...]:
    """Return names of palettes registered in the current process."""
    return tuple(sorted(_PRESETS))
