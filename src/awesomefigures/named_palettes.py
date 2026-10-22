"""Historically established palettes with their original sRGB coordinates.

Unlike contrast_grid(), these palettes are *not* adjusted to a desired WCAG
luminance ladder. Reproducing the published color specification is the
contract. Continuous palettes are delegated to Matplotlib colormaps.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

import matplotlib as mpl
import numpy as np
from matplotlib.colors import ListedColormap, to_hex, to_rgba, to_rgb

from .alpha import compensate_alpha

PaletteKind = Literal["categorical", "sequential", "diverging"]


@dataclass(frozen=True)
class NamedPalette:
    """Built-in palette metadata; `colors` is None for continuous maps."""

    name: str
    kind: PaletteKind
    source: str
    description: str
    colors: tuple[str, ...] | None = None
    matplotlib_cmap: str | None = None


_LIBRARY: dict[str, NamedPalette] = {
    "okabe-ito": NamedPalette(
        "okabe-ito", "categorical",
        "https://jfly.uni-koeln.de/color/",
        "Okabe–Ito Color Universal Design, seven chromatic colours and black.",
        ("#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2",
         "#D55E00", "#CC79A7", "#000000"),
    ),
    "tol-bright": NamedPalette(
        "tol-bright", "categorical", "https://sronpersonalpages.nl/~pault/",
        "Paul Tol qualitative bright scheme.",
        ("#4477AA", "#EE6677", "#228833", "#CCBB44",
         "#66CCEE", "#AA3377", "#BBBBBB"),
    ),
    "tol-high-contrast": NamedPalette(
        "tol-high-contrast", "categorical",
        "https://sronpersonalpages.nl/~pault/",
        "Paul Tol three-category high-contrast scheme; useful in grayscale.",
        ("#004488", "#DDAA33", "#BB5566"),
    ),
    "tol-muted": NamedPalette(
        "tol-muted", "categorical", "https://sronpersonalpages.nl/~pault/",
        "Paul Tol muted scheme, nine categorical colours.",
        ("#332288", "#88CCEE", "#44AA99", "#117733", "#999933",
         "#DDCC77", "#CC6677", "#882255", "#AA4499"),
    ),
    "tableau-10": NamedPalette(
        "tableau-10", "categorical",
        "https://www.tableau.com/blog/colors-upgrade-tableau-10-56782",
        "Tableau 10 qualitative cycle, not a universal CVD guarantee.",
        ("#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
         "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"),
    ),
    "brewer-set2": NamedPalette(
        "brewer-set2", "categorical", "https://colorbrewer2.org/",
        "ColorBrewer Set2 qualitative set (8 colours).",
        ("#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3",
         "#A6D854", "#FFD92F", "#E5C494", "#B3B3B3"),
    ),
    "brewer-dark2": NamedPalette(
        "brewer-dark2", "categorical", "https://colorbrewer2.org/",
        "ColorBrewer Dark2 qualitative set (8 colours).",
        ("#1B9E77", "#D95F02", "#7570B3", "#E7298A",
         "#66A61E", "#E6AB02", "#A6761D", "#666666"),
    ),
    "viridis": NamedPalette(
        "viridis", "sequential", "https://matplotlib.org/stable/users/explain/colors/colormaps.html",
        "Perceptually uniform sequential Matplotlib map.", matplotlib_cmap="viridis",
    ),
    "cividis": NamedPalette(
        "cividis", "sequential", "https://matplotlib.org/stable/users/explain/colors/colormaps.html",
        "Sequential map designed with colour-vision deficiencies in mind.",
        matplotlib_cmap="cividis",
    ),
    "plasma": NamedPalette(
        "plasma", "sequential", "https://matplotlib.org/stable/users/explain/colors/colormaps.html",
        "Perceptually uniform sequential Matplotlib map.", matplotlib_cmap="plasma",
    ),
    "magma": NamedPalette(
        "magma", "sequential", "https://matplotlib.org/stable/users/explain/colors/colormaps.html",
        "Perceptually uniform sequential Matplotlib map.", matplotlib_cmap="magma",
    ),
    "inferno": NamedPalette(
        "inferno", "sequential", "https://matplotlib.org/stable/users/explain/colors/colormaps.html",
        "Perceptually uniform sequential Matplotlib map.", matplotlib_cmap="inferno",
    ),
    "rdbu": NamedPalette(
        "rdbu", "diverging", "https://colorbrewer2.org/",
        "ColorBrewer red/blue diverging map as supplied by Matplotlib.",
        matplotlib_cmap="RdBu",
    ),
}

_ALIASES = {"okabe_ito": "okabe-ito", "okabeito": "okabe-ito",
            "colorblind": "okabe-ito", "wong": "okabe-ito",
            "tableau10": "tableau-10", "set2": "brewer-set2",
            "dark2": "brewer-dark2", "rd-bu": "rdbu"}


def _normalize(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Palette name must be a string.")
    return _ALIASES.get(name.strip().lower(), name.strip().lower())


def available_named_palettes(
    kind: PaletteKind | None = None,
) -> tuple[str, ...]:
    """Return all preinstalled exact-HEX or Matplotlib colormap names."""
    if kind is not None and kind not in {"categorical", "sequential", "diverging"}:
        raise ValueError("kind must be categorical, sequential, diverging, or None.")
    return tuple(name for name, entry in _LIBRARY.items()
                 if kind is None or entry.kind == kind)


def get_named_palette(name: str) -> NamedPalette:
    """Get metadata, provenance and exact colors of a known built-in palette."""
    key = _normalize(name)
    try:
        return _LIBRARY[key]
    except KeyError as exc:
        raise KeyError(
            f"Unknown built-in palette {name!r}. "
            f"Choose from {', '.join(available_named_palettes())}."
        ) from exc


def named_palette(
    name: str,
    n: int | None = None,
    *,
    alpha: float = 1.0,
    background: str = "white",
    preserve_apparent: bool = True,
    alpha_strategy: str = "perceptual",
    as_hex: bool = False,
) -> list[str] | list[tuple[float, float, float, float]]:
    """Return original named colours, with optional background-aware opacity.

    Categorical schemes preserve *exact* source hex values and their order.
    Requesting more categories than exist raises instead of silently recycling
    ambiguous colours. Continuous schemes sample Matplotlib's original map
    at n evenly spaced locations; n defaults to 7.

    as_hex=True returns opaque source HEX (ignores alpha/appearance options).
    With alpha<1 and preserve_apparent=True, compensation may change the
    *source* RGB to approach the target after compositing. The hex reference
    remains unchanged, and exact recovery may be physically impossible.
    """
    palette = get_named_palette(name)
    if n is not None and (not isinstance(n, int) or isinstance(n, bool) or n < 1):
        raise ValueError("n must be a positive integer.")
    if not math.isfinite(alpha) or not 0 < alpha <= 1:
        raise ValueError("alpha must lie in (0, 1].")
    if palette.colors is not None:
        count = len(palette.colors) if n is None else n
        if count > len(palette.colors):
            raise ValueError(
                f"Palette {palette.name!r} contains only {len(palette.colors)} "
                "categorical colours; do not silently repeat categories."
            )
        hex_colors = list(palette.colors[:count])
    else:
        count = 7 if n is None else n
        cmap = mpl.colormaps[palette.matplotlib_cmap]
        # For diverging maps one colour should represent a meaningful midpoint.
        hex_colors = [to_hex(cmap(v), keep_alpha=False).upper()
                      for v in np.linspace(0.0, 1.0, count)]
    if as_hex:
        return hex_colors
    if alpha == 1.0:
        return [(*to_rgb(color), 1.0) for color in hex_colors]
    output = []
    for color in hex_colors:
        if preserve_apparent:
            compensated = compensate_alpha(
                color, alpha=alpha, background=background,
                strategy=alpha_strategy,
            )
            output.append(tuple(map(float, compensated.source_rgb)) + (alpha,))
        else:
            output.append((*to_rgb(color), alpha))
    return output


def named_colormap(name: str):
    """Return a continuous original Matplotlib map or categorical ListedColormap."""
    palette = get_named_palette(name)
    if palette.matplotlib_cmap is not None:
        return mpl.colormaps[palette.matplotlib_cmap]
    return ListedColormap(palette.colors, name=palette.name)
