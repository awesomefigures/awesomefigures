"""True-vector accessibility dashboards for line and grouped-scatter plots.

Unlike screenshot-based accessibility panels, these dashboards reconstruct
Matplotlib Line2D and PathCollection artists as vector primitives. Text and
markers remain scalable in PDF/PGF. Transformations are approximate color-
vision simulations, not accessibility certification. Currently supports
one source Axes with lines and/or scatter collections; all other plot artist
types must use the raster preview API.
"""
from __future__ import annotations

from collections.abc import Sequence
from math import ceil

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from matplotlib.colors import to_rgba
from matplotlib.ticker import MaxNLocator
import numpy as np
from colorspacious import cspace_convert

from .accessibility import DEFAULT_ACCESSIBILITY_MODES, _CVD_TYPES


def _color_view(color, mode: str, severity: float) -> tuple[float, ...]:
    """Convert an artist's color while retaining alpha (and vector shapes)."""
    rgba = np.asarray(to_rgba(color), dtype=float)
    rgb = rgba[:3]
    if mode == "original":
        pass
    elif mode in ("grayscale", "print"):
        linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
        y = float(np.dot(linear, [.2126, .7152, .0722]))
        gray = 12.92 * y if y <= .0031308 else 1.055 * y ** (1 / 2.4) - .055
        if mode == "print":
            gray = round(np.clip(.5 + .68 * (gray - .5), 0, 1) * 8) / 8
        rgb = np.repeat(gray, 3)
    elif mode in _CVD_TYPES:
        rgb = cspace_convert(rgb, {
            "name": "sRGB1+CVD",
            "cvd_type": _CVD_TYPES[mode],
            "severity": float(severity),
        }, "sRGB1")
    else:
        raise ValueError(f"Unknown viewing mode: {mode}")
    return tuple(float(x) for x in np.r_[np.clip(rgb, 0, 1), rgba[3]])


def _color_array(colors, mode: str, severity: float) -> np.ndarray:
    colors = np.asarray(colors, dtype=float)
    if not len(colors):
        return colors.copy()
    return np.asarray([_color_view(color, mode, severity) for color in colors])


def _replot_lines(source, destination, mode: str, severity: float):
    legend_handles = []
    for original in source.lines:
        if not original.get_visible():
            continue
        color = _color_view(original.get_color(), mode, severity)
        mfc = original.get_markerfacecolor()
        mec = original.get_markeredgecolor()
        mfc = original.get_color() if mfc == "auto" else mfc
        mec = original.get_color() if mec == "auto" else mec
        markerface = (
            "none" if mfc == "none" else _color_view(mfc, mode, severity)
        )
        markeredge = (
            "none" if mec == "none" else _color_view(mec, mode, severity)
        )
        (line,) = destination.plot(
            original.get_xdata(), original.get_ydata(),
            color=color, alpha=original.get_alpha(),
            linestyle=original.get_linestyle(),
            linewidth=original.get_linewidth(),
            marker=original.get_marker(),
            markersize=original.get_markersize(),
            markerfacecolor=markerface,
            markeredgecolor=markeredge,
            markeredgewidth=original.get_markeredgewidth(),
            markevery=original.get_markevery(),
            label=original.get_label(),
            zorder=original.get_zorder(),
            rasterized=False,
        )
        if not line.get_label().startswith("_"):
            legend_handles.append(line)
    return legend_handles


def _replot_scatter(source, destination, mode: str, severity: float):
    """Redraw scatter using Matplotlib's marker-size and data transforms.

    Constructing PathCollection directly skips the marker-size transform,
    so small scatter markers expand into enormous filled polygons in PGF.
    The source's normalized marker Path may be passed to Axes.scatter.
    """
    legend_handles = []
    for original in source.collections:
        if not isinstance(original, PathCollection):
            raise NotImplementedError(
                "Vector dashboard supports PathCollection scatter artists only."
            )
        if not original.get_visible():
            continue

        paths = original.get_paths()
        if len(paths) != 1:
            raise NotImplementedError(
                "Vector dashboard expects one marker path per scatter collection."
            )
        offsets = original.get_offsets()
        if len(offsets) == 0:
            continue

        faces = _color_array(original.get_facecolors(), mode, severity)
        original_edges = original.get_edgecolors()
        edges = _color_array(original_edges, mode, severity)

        # White separator strokes are a geometric cue, not a hue.
        if len(edges):
            whites = np.all(np.isclose(original_edges[:, :3], 1.0), axis=1)
            edges[whites, :3] = 1.0

        clone = destination.scatter(
            offsets[:, 0], offsets[:, 1],
            s=original.get_sizes(),
            marker=paths[0],
            facecolors=faces if len(faces) else "none",
            edgecolors=edges if len(edges) else "none",
            linewidths=original.get_linewidths(),
            label=original.get_label(),
            zorder=original.get_zorder(),
            rasterized=False,
        )
        if not clone.get_label().startswith("_"):
            legend_handles.append(clone)
    return legend_handles


def show_vector_accessibility_panel(
    source: mpl.figure.Figure,
    *,
    modes: Sequence[str] = DEFAULT_ACCESSIBILITY_MODES,
    ncols: int = 2,
    figsize: tuple[float, float] | None = None,
    title_fontsize: float = 10.0,
    axis_label_fontsize: float = 10.0,
    tick_fontsize: float = 8.0,
    legend_fontsize: float = 8.0,
    severity: float = 100.0,
) -> tuple[mpl.figure.Figure, np.ndarray]:
    """Rebuild a multi-view dashboard as true Matplotlib vector graphics.

    The source must contain exactly one Axes with lines and/or
    Axes.scatter PathCollections. Unsupported artists raise explicitly;
    no raster snapshots are used. For PGF export, include the resulting PGF
    in the same LaTeX document for *exact* font glyphs.

    Each axis label is set in physical points, independent of subplot width.
    Use figsize=(layout.width_inches("text"), height_inches) and include
    the PDF/PGF without any includegraphics width/height scaling.
    """
    if len(source.axes) != 1:
        raise ValueError("Vector accessibility dashboards need one source Axes.")
    ax = source.axes[0]
    if not ax.lines and not ax.collections:
        raise ValueError("Source axes has no line or scatter artists.")
    if ax.images or ax.patches or ax.containers:
        raise NotImplementedError(
            "Image, patch and container artists are not supported by the "
            "vector replotter. Use show_accessibility_panel for these plots."
        )
    if not modes or ncols < 1:
        raise ValueError("Supply a nonempty sequence of modes and ncols >= 1.")
    if not np.isfinite(severity) or not 0 <= severity <= 100:
        raise ValueError("severity must be in [0, 100].")
    for size in (title_fontsize, axis_label_fontsize, tick_fontsize, legend_fontsize):
        if not np.isfinite(size) or size <= 0:
            raise ValueError("All font sizes must be finite and positive.")
    for mode in modes:
        if mode not in DEFAULT_ACCESSIBILITY_MODES:
            raise ValueError(f"Unsupported mode: {mode}")

    cols = min(ncols, len(modes))
    rows = ceil(len(modes) / cols)
    if figsize is None:
        figsize = (3.25 * cols, 2.9 * rows)
    panel, matrix = plt.subplots(rows, cols, figsize=figsize, squeeze=False)
    panel.set_facecolor("white")
    axes = matrix.ravel()
    handles = []
    for index, mode in enumerate(modes):
        dest = axes[index]
        # Match the old 9-level print-stress diagnostic: paper white is
        # mapped to 0.875 gray, without rasterizing the dashboard.
        dest.set_facecolor(
            _color_view("white", "print", severity) if mode == "print" else "white"
        )
        dest.set_axisbelow(True)
        dest.grid(True, alpha=.24, linewidth=.5)
        local_handles = _replot_lines(ax, dest, mode, severity)
        local_handles += _replot_scatter(ax, dest, mode, severity)
        if index == 0:
            handles = local_handles
        dest.set_xlim(ax.get_xlim())
        dest.set_ylim(ax.get_ylim())
        dest.set_xlabel(
            ax.get_xlabel(), fontsize=axis_label_fontsize, fontweight="normal"
        )
        dest.set_ylabel(
            ax.get_ylabel(), fontsize=axis_label_fontsize, fontweight="normal"
        )
        dest.tick_params(axis="both", labelsize=tick_fontsize, length=2.5)
        dest.xaxis.set_major_locator(MaxNLocator(nbins=4))
        dest.yaxis.set_major_locator(MaxNLocator(nbins=4))
        dest.set_title(
            {"print": "Print stress"}.get(mode, mode.capitalize()),
            fontsize=title_fontsize, fontweight="normal", pad=6,
        )
        for edge in ("top", "right"):
            dest.spines[edge].set_visible(False)
    for dest in axes[len(modes):]:
        dest.set_visible(False)

    labeled = [h for h in handles if not h.get_label().startswith("_")]
    if labeled:
        panel.legend(
            labeled, [h.get_label() for h in labeled],
            loc="upper center", bbox_to_anchor=(.5, .993),
            ncol=min(3, len(labeled)), frameon=False,
            fontsize=legend_fontsize, markerscale=1,
            columnspacing=.9, handlelength=1.8,
        )
    # A fixed-size dashboard is *not* subsequently scaled in the manuscript.
    # Make room for one shared legend and all original-size labels.
    panel.subplots_adjust(
        left=.105 if cols == 2 else .09, right=.977,
        # A 3 x 2 dashboard at true manuscript text width is compact:
        # a 7.2% bottom margin clips its 10 pt x-axis labels in PGF/PDF.
        # Preserve the physical text size; allocate adequate space instead.
        top=.91, bottom=.12 if rows == 2 else .06,
        wspace=.40 if cols == 3 else .34,
        hspace=.54 if rows == 2 else .57,
    )
    return panel, axes
