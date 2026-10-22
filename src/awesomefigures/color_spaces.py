"""Low-level color conversions used by :mod:`awesomefigures`.

The package deliberately keeps these routines small and dependency-light.
Relative luminance follows WCAG's sRGB definition; OKLab conversions follow
Björn Ottosson's published matrices.
"""

from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np

RGBLike = str | Sequence[float] | np.ndarray


def _as_rgb_array(color: RGBLike) -> np.ndarray:
    """Convert a hex string or RGB triple to an sRGB array in ``[0, 1]``."""
    if isinstance(color, str):
        value = color.strip()
        if value.startswith("#"):
            hex_value = value[1:]
            if len(hex_value) == 3:
                hex_value = "".join(ch * 2 for ch in hex_value)
            if len(hex_value) != 6:
                raise ValueError(f"Expected #RRGGBB or #RGB, got {color!r}.")
            try:
                return np.array(
                    [int(hex_value[i : i + 2], 16) / 255 for i in (0, 2, 4)],
                    dtype=float,
                )
            except ValueError as exc:
                raise ValueError(f"Invalid hex color {color!r}.") from exc

        # Follow Matplotlib's normal color syntax for named colors, Tableau
        # colors, CSS4 names, etc.  Import lazily to keep this low-level
        # module lightweight at import time.
        try:
            from matplotlib.colors import to_rgb as mpl_to_rgb

            return np.asarray(mpl_to_rgb(value), dtype=float)
        except ValueError as exc:
            raise ValueError(f"Invalid Matplotlib color {color!r}.") from exc

    arr = np.asarray(color, dtype=float)
    if arr.shape != (3,):
        raise ValueError("RGB colors must contain exactly three channels.")
    if np.any(~np.isfinite(arr)):
        raise ValueError("RGB channels must be finite.")
    if np.any((arr < 0) | (arr > 1)):
        raise ValueError("RGB channels must lie in [0, 1].")
    return arr


def to_rgb(color: RGBLike) -> np.ndarray:
    """Return an sRGB triple in ``[0, 1]``."""
    return _as_rgb_array(color).copy()


def to_hex(color: RGBLike) -> str:
    """Return ``#RRGGBB`` for an sRGB triple or hex input."""
    rgb = _as_rgb_array(color)
    values = np.clip(np.rint(rgb * 255), 0, 255).astype(int)
    return "#" + "".join(f"{value:02X}" for value in values)


def srgb_to_linear(rgb: RGBLike) -> np.ndarray:
    """Decode sRGB channels to linear-light RGB."""
    c = _as_rgb_array(rgb)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(linear_rgb: Sequence[float] | np.ndarray, *, clip: bool = False) -> np.ndarray:
    """Encode linear-light RGB as sRGB.

    Parameters
    ----------
    linear_rgb:
        Linear RGB triple. Values may be outside ``[0, 1]`` while checking
        gamut feasibility.
    clip:
        If true, clip encoded values to the sRGB gamut.
    """
    x = np.asarray(linear_rgb, dtype=float)
    if x.shape != (3,):
        raise ValueError("linear_rgb must contain exactly three channels.")
    c = np.where(
        x <= 0.0031308,
        12.92 * x,
        1.055 * np.power(np.maximum(x, 0), 1 / 2.4) - 0.055,
    )
    return np.clip(c, 0, 1) if clip else c


def relative_luminance(color: RGBLike) -> float:
    """Return WCAG relative luminance ``Y`` in ``[0, 1]``."""
    r, g, b = srgb_to_linear(color)
    return float(0.2126 * r + 0.7152 * g + 0.0722 * b)


def contrast_ratio(color_a: RGBLike, color_b: RGBLike) -> float:
    """Return the WCAG contrast ratio between two opaque sRGB colors."""
    ya = relative_luminance(color_a)
    yb = relative_luminance(color_b)
    hi, lo = max(ya, yb), min(ya, yb)
    return (hi + 0.05) / (lo + 0.05)


def oklch_to_linear_srgb(lightness: float, chroma: float, hue: float) -> np.ndarray:
    """Convert OKLCH to linear sRGB without gamut clipping.

    ``hue`` is expressed in degrees.
    """
    h = math.radians(hue % 360.0)
    a = chroma * math.cos(h)
    b = chroma * math.sin(h)

    l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_ = lightness - 0.0894841775 * a - 1.2914855480 * b

    l = l_**3
    m = m_**3
    s = s_**3

    return np.array(
        [
            4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
        ],
        dtype=float,
    )


def in_srgb_gamut(linear_rgb: Sequence[float] | np.ndarray, *, tol: float = 1e-10) -> bool:
    """Return whether linear RGB lies inside the sRGB gamut."""
    rgb = np.asarray(linear_rgb, dtype=float)
    return bool(np.all(rgb >= -tol) and np.all(rgb <= 1 + tol))


def srgb_to_oklab(color: RGBLike) -> np.ndarray:
    """Convert an sRGB color to OKLab coordinates."""
    r, g, b = srgb_to_linear(color)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l_, m_, s_ = np.cbrt([l, m, s])
    return np.array(
        [
            0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
        ],
        dtype=float,
    )


def delta_e_ok(color_a: RGBLike, color_b: RGBLike) -> float:
    """Euclidean color distance in OKLab."""
    return float(np.linalg.norm(srgb_to_oklab(color_a) - srgb_to_oklab(color_b)))
