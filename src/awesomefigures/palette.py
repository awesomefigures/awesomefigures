"""Contrast-controlled hue/luminance grids and palettes."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable, Sequence

import numpy as np

from .alpha import AlphaCompensation, compensate_alpha
from .color_spaces import (
    contrast_ratio,
    in_srgb_gamut,
    linear_to_srgb,
    oklch_to_linear_srgb,
    relative_luminance,
    to_hex,
)
from .contrast import luminance_ladder


@dataclass(frozen=True)
class ColorCell:
    """One color in a :class:`ContrastGrid`."""

    rgb: np.ndarray
    hue: float
    target_luminance: float
    actual_luminance: float
    requested_chroma: float
    actual_chroma: float
    oklch_lightness: float

    @property
    def hex(self) -> str:
        return to_hex(self.rgb)


@dataclass(frozen=True)
class RenderedColor:
    """A palette color prepared for a specific alpha/background context."""

    target: ColorCell
    compensation: AlphaCompensation

    @property
    def rgba(self) -> tuple[float, float, float, float]:
        r, g, b = self.compensation.source_rgb
        return float(r), float(g), float(b), self.compensation.alpha


class Palette(Sequence[ColorCell]):
    """Ordered colors selected from distinct luminance levels."""

    def __init__(self, cells: Iterable[ColorCell]):
        self._cells = tuple(cells)
        if not self._cells:
            raise ValueError("A palette must contain at least one color.")

    def __getitem__(self, index):
        return self._cells[index]

    def __len__(self) -> int:
        return len(self._cells)

    @property
    def hex(self) -> list[str]:
        return [cell.hex for cell in self._cells]

    @property
    def rgb(self) -> list[tuple[float, float, float]]:
        return [tuple(map(float, cell.rgb)) for cell in self._cells]

    @property
    def luminances(self) -> np.ndarray:
        return np.array([cell.actual_luminance for cell in self._cells])

    @property
    def adjacent_contrast(self) -> np.ndarray:
        return np.array(
            [contrast_ratio(self[i].rgb, self[i + 1].rgb) for i in range(len(self) - 1)]
        )

    def render(
        self,
        *,
        alpha: float = 1.0,
        background: str | Sequence[float] = "#FFFFFF",
        preserve_apparent: bool = True,
        alpha_strategy: str = "perceptual",
    ) -> list[RenderedColor]:
        """Prepare colors for rendering over ``background``.

        If ``preserve_apparent`` is true, source RGB is pre-compensated so the
        composited result approaches the opaque target color.
        """
        rendered: list[RenderedColor] = []
        for cell in self:
            if preserve_apparent:
                compensation = compensate_alpha(
                    cell.rgb,
                    alpha=alpha,
                    background=background,
                    strategy=alpha_strategy,
                )
            else:
                from .alpha import composite
                from .color_spaces import to_rgb

                source = cell.rgb.copy()
                displayed = composite(source, background, alpha)
                compensation = AlphaCompensation(
                    target_rgb=cell.rgb.copy(),
                    source_rgb=source,
                    displayed_rgb=displayed,
                    background_rgb=to_rgb(background),
                    alpha=float(alpha),
                    feasible=True,
                    strategy="clip",
                )
            rendered.append(RenderedColor(target=cell, compensation=compensation))
        return rendered

    def mpl_colors(
        self,
        *,
        alpha: float = 1.0,
        background: str | Sequence[float] = "#FFFFFF",
        preserve_apparent: bool = True,
        alpha_strategy: str = "perceptual",
    ) -> list[tuple[float, float, float, float]]:
        """Return RGBA tuples ready for Matplotlib."""
        return [
            item.rgba
            for item in self.render(
                alpha=alpha,
                background=background,
                preserve_apparent=preserve_apparent,
                alpha_strategy=alpha_strategy,
            )
        ]

    def minimum_alpha(
        self, *, background: str | Sequence[float] = "#FFFFFF"
    ) -> float:
        """Smallest shared alpha that can preserve every target color exactly."""
        from .alpha import minimum_alpha

        return max(minimum_alpha(cell.rgb, background=background) for cell in self)

    def as_cmap(self, *, name: str = "awesomefigures"):
        """Return a Matplotlib ``ListedColormap``."""
        from matplotlib.colors import ListedColormap

        return ListedColormap(self.rgb, name=name)


class ContrastGrid:
    r"""A matrix whose rows have fixed luminance and columns have fixed hue.

    Any palette that chooses one cell from each row inherits the same adjacent
    contrast ratios, independently of which hue is chosen in each row.
    """

    def __init__(
        self,
        cells: Sequence[Sequence[ColorCell]],
        *,
        ratio: float,
        hues: Sequence[float],
        luminances: Sequence[float],
    ):
        self._cells = tuple(tuple(row) for row in cells)
        self.ratio = float(ratio)
        self.hues = tuple(float(h % 360) for h in hues)
        self.luminances = np.asarray(luminances, dtype=float)

    @property
    def shape(self) -> tuple[int, int]:
        return len(self._cells), len(self._cells[0])

    def __getitem__(self, index):
        return self._cells[index]

    @property
    def hex(self) -> list[list[str]]:
        return [[cell.hex for cell in row] for row in self._cells]

    def select(self, hue_indices: Sequence[int]) -> Palette:
        """Select one hue index per luminance level."""
        if len(hue_indices) != len(self._cells):
            raise ValueError(
                f"Expected {len(self._cells)} hue indices, got {len(hue_indices)}."
            )
        cells = []
        for row, hue_index in zip(self._cells, hue_indices, strict=True):
            cells.append(row[hue_index])
        return Palette(cells)

    def diagonal(self) -> Palette:
        """Select a cyclic diagonal through the grid."""
        n_hues = len(self.hues)
        return self.select([i % n_hues for i in range(len(self._cells))])

    def plot(self, *, ax=None, annotate: bool = True):
        """Visualize the hue-luminance grid using Matplotlib."""
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle

        if ax is None:
            _, ax = plt.subplots(figsize=(1.6 * len(self.hues), 1.1 * len(self._cells)))

        rows, cols = self.shape
        for i, row in enumerate(self._cells):
            for j, cell in enumerate(row):
                ax.add_patch(Rectangle((j, rows - 1 - i), 1, 1, facecolor=cell.rgb, edgecolor="white"))
                if annotate:
                    y = cell.actual_luminance
                    # Choose by the actual WCAG contrast with this cell.
                    # A fixed Y threshold of 0.35 could pick white against
                    # midtone backgrounds and fail small-label readability.
                    black_contrast = contrast_ratio(cell.rgb, "black")
                    white_contrast = contrast_ratio(cell.rgb, "white")
                    text_color = "black" if black_contrast >= white_contrast else "white"
                    # Keep the visible #RRGGBB notation in both Matplotlib
                    # PDF and native PGF. An unescaped "#" makes TeX abort
                    # during backend_pgf's text measurement. Plain "\\#"
                    # instead displays a literal backslash in non-TeX PDF.
                    # MathText's escaped hash works in both exporters.
                    tex_safe_hex = r"$\#$" + cell.hex[1:]
                    ax.text(
                        j + 0.5, rows - 0.5 - i, tex_safe_hex,
                        ha="center", va="center", color=text_color, fontsize=8,
                    )

        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")
        ax.set_xticks(np.arange(cols) + 0.5, [f"{h:.0f}\u00b0" for h in self.hues])
        ax.set_yticks(
            np.arange(rows) + 0.5,
            [f"Y={y:.3f}" for y in self.luminances[::-1]],
        )
        ax.set_xlabel("Hue")
        ax.set_ylabel("Relative luminance")
        for spine in ax.spines.values():
            spine.set_visible(False)
        return ax


def _luminance_from_linear(rgb: np.ndarray) -> float:
    return float(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])


def _solve_lightness(target_luminance: float, chroma: float, hue: float) -> tuple[float, np.ndarray]:
    """Solve OKLCH lightness for a target WCAG luminance at fixed C and h."""
    lo, hi = 0.0, 1.0
    for _ in range(64):
        mid = (lo + hi) / 2
        rgb_linear = oklch_to_linear_srgb(mid, chroma, hue)
        y = _luminance_from_linear(rgb_linear)
        if y < target_luminance:
            lo = mid
        else:
            hi = mid
    lightness = (lo + hi) / 2
    linear = oklch_to_linear_srgb(lightness, chroma, hue)
    return lightness, linear


def color_for_luminance(
    target_luminance: float,
    hue: float,
    *,
    chroma: float = 0.13,
) -> ColorCell:
    """Generate an sRGB color at a requested luminance and hue.

    Chroma is reduced only as much as required to remain in the sRGB gamut.
    """
    if not 0 <= target_luminance <= 1:
        raise ValueError("target_luminance must lie in [0, 1].")
    if chroma < 0:
        raise ValueError("chroma must be >= 0.")

    lightness, linear = _solve_lightness(target_luminance, chroma, hue)
    actual_chroma = chroma

    if not in_srgb_gamut(linear):
        lo, hi = 0.0, chroma
        best = (0.0, *_solve_lightness(target_luminance, 0.0, hue))
        for _ in range(48):
            mid = (lo + hi) / 2
            l_mid, rgb_mid = _solve_lightness(target_luminance, mid, hue)
            if in_srgb_gamut(rgb_mid):
                lo = mid
                best = (mid, l_mid, rgb_mid)
            else:
                hi = mid
        actual_chroma, lightness, linear = best

    rgb = linear_to_srgb(linear, clip=True)
    actual_y = relative_luminance(rgb)
    return ColorCell(
        rgb=rgb,
        hue=float(hue % 360),
        target_luminance=float(target_luminance),
        actual_luminance=actual_y,
        requested_chroma=float(chroma),
        actual_chroma=float(actual_chroma),
        oklch_lightness=float(lightness),
    )


def contrast_grid(
    *,
    levels: int,
    hues: Sequence[float],
    ratio: float = 1.5,
    start_luminance: float = 0.95,
    chroma: float = 0.13,
) -> ContrastGrid:
    """Construct a hue-luminance grid with constant adjacent contrast.

    Parameters
    ----------
    levels:
        Number of luminance levels (rows).
    hues:
        Hue angles in degrees (columns).
    ratio:
        Desired WCAG contrast ratio between adjacent rows.
    start_luminance:
        Relative luminance of the lightest row.
    chroma:
        Requested OKLCH chroma. It is automatically reduced near gamut edges.
    """
    if len(hues) == 0:
        raise ValueError("At least one hue is required.")
    luminances = luminance_ladder(levels, ratio, start_luminance=start_luminance)
    cells = [
        [color_for_luminance(y, hue, chroma=chroma) for hue in hues]
        for y in luminances
    ]
    return ContrastGrid(cells, ratio=ratio, hues=hues, luminances=luminances)
