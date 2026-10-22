"""Nice-bound scientific axes with geometry-aware line-marker placement.

This module never modifies samples, interpolation knots, splines, or line paths.
It chooses outward-facing tick-aligned view limits and suppresses only markers
that would visually collide with axis edges. Call after plotting, or activate
set_style("elegante") for automatic application on rendering.
"""
from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np
from matplotlib.axes import Axes


NICE_STEPS = (1.0, 2.0, 2.5, 5.0, 10.0)


def nice_tick_bounds(
    low: float,
    high: float,
    *,
    target_ticks: int = 6,
    steps: Sequence[float] = NICE_STEPS,
    padding: float = 0.0,
    force_zero: bool = False,
) -> tuple[float, float, np.ndarray]:
    """Find readable, evenly spaced ticks including both view endpoints.

    Each candidate step is m*10**k with m from steps. The selected step
    minimizes a trade-off between unused axis space and tick-count error.
    Unlike MaxNLocator, endpoints and visible tick labels always coincide.
    """
    if not (math.isfinite(low) and math.isfinite(high)):
        raise ValueError("Axis bounds must be finite.")
    if not isinstance(target_ticks, int) or not 2 <= target_ticks <= 30:
        raise ValueError("target_ticks must be an integer in [2, 30].")
    if not math.isfinite(padding) or padding < 0:
        raise ValueError("padding must be nonnegative and finite.")
    if not steps or any(not math.isfinite(m) or m <= 0 for m in steps):
        raise ValueError("steps must contain positive finite numbers.")
    a, b = sorted((float(low), float(high)))
    if force_zero:
        a, b = min(a, 0.0), max(b, 0.0)
    if a == b:
        delta = max(abs(a) * 0.05, 1e-9)
        a -= delta
        b += delta
    span = b - a
    a -= span * padding
    b += span * padding
    span = b - a
    rough = span / (target_ticks - 1)
    power = math.floor(math.log10(rough))
    best = None
    for exponent in range(power - 2, power + 3):
        for mantissa in steps:
            step = float(mantissa * 10.0 ** exponent)
            if not math.isfinite(step) or step <= 0:
                continue
            # Round with a small tolerance to avoid a spurious extra tick at
            # exact multiples (e.g. data ending at 100.00000000000001).
            tol = 1e-11
            first = math.floor(a / step + tol)
            last = math.ceil(b / step - tol)
            count = last - first + 1
            if count < 2 or count > max(2 * target_ticks + 4, 35):
                continue
            lower, upper = first * step, last * step
            unused = max(0, a - lower) + max(0, upper - b)
            # Unused range costs more than a one-tick deviation: this
            # rewards exact endpoint alignment for data like [0, 100].
            score = 5.0 * unused / span + 0.16 * abs(count - target_ticks)
            tie = (score, abs(count - target_ticks), step)
            if best is None or tie < best[0]:
                best = (tie, lower, upper, count, step)
    if best is None:
        raise ValueError("Cannot build suitable ticks from these parameters.")
    _, lower, upper, count, step = best
    ticks = lower + np.arange(count, dtype=float) * step
    ticks[0], ticks[-1] = lower, upper
    ticks[np.isclose(ticks, 0, atol=abs(step) * 1e-12)] = 0.0
    return float(lower), float(upper), ticks


def _same_markevery(a, b) -> bool:
    """Compare marker specifications, including NumPy integer arrays."""
    try:
        return bool(np.array_equal(np.asarray(a, dtype=object),
                                   np.asarray(b, dtype=object)))
    except (TypeError, ValueError):
        return False


def _marker_candidates(line, xy: np.ndarray, vertices: np.ndarray,
                       ax: Axes) -> np.ndarray | None:
    """Resolve Matplotlib marker sampling into source indices.

    Integer markevery settings retain their original eligible subset, which
    is then thinned. Float settings are based on physical screen path length,
    as in Matplotlib; unsupported configurations remain untouched.
    """
    n = len(xy)
    source = getattr(line, "_awesomefigures_marker_source",
                     line.get_markevery())
    if source is None:
        return np.arange(n, dtype=int)
    if isinstance(source, (int, np.integer)) and not isinstance(source, bool):
        return np.arange(0, n, int(source), dtype=int) if source > 0 else None
    if isinstance(source, slice):
        return np.arange(n, dtype=int)[source]
    if isinstance(source, tuple) and len(source) == 2:
        offset, step = source
        if all(isinstance(v, (int, np.integer)) and not isinstance(v, bool)
               for v in source):
            return (np.arange(int(offset), n, int(step), dtype=int)
                    if step > 0 else None)
        if all(isinstance(v, (float, int, np.floating, np.integer))
               for v in source) and step > 0:
            start_distance = float(offset)
            stride_fraction = float(step)
        else:
            return None
    elif isinstance(source, (float, np.floating)) and source > 0:
        start_distance, stride_fraction = 0., float(source)
    elif isinstance(source, (list, np.ndarray)):
        values = np.asarray(source)
        if values.ndim != 1:
            return None
        if values.dtype.kind in "iu":
            return np.arange(n, dtype=int)[values]
        if values.dtype.kind == "b" and len(values) == n:
            return np.flatnonzero(values)
        return None
    else:
        return None

    # Fractional markevery values measure diagonal-normalized screen distance.
    finite = np.isfinite(vertices).all(axis=1)
    segment = np.linalg.norm(np.diff(vertices, axis=0), axis=1)
    segment[~(finite[1:] & finite[:-1])] = 0.
    arclength = np.r_[0., np.cumsum(segment)]
    diagonal = math.hypot(ax.bbox.width, ax.bbox.height)
    stride = stride_fraction * diagonal
    if not math.isfinite(stride) or stride <= 0:
        return None
    targets = np.arange(start_distance * diagonal, arclength[-1] + 1e-9,
                        stride)
    if len(targets) > n * 2:
        targets = targets[:n * 2]
    return np.unique(np.clip(np.searchsorted(arclength, targets),
                             0, n - 1).astype(int))


def _line_marker_indices(
    line, ax: Axes, *, inset_pt: float, count: int, spacing_pt: float
) -> None:
    """Thin visible line markers in physical display space, not data space.

    Redundant marker encodings remain legible on very densely sampled splines.
    The Line2D path and original data points are left strictly unchanged.
    Marker-only observations are intentionally preserved as data.
    """
    marker = line.get_marker()
    if marker is None or str(marker).lower() in {"none", "", " ", "nan"}:
        return
    if not line.get_visible() or str(line.get_linestyle()).lower() in {
        "none", "", " "
    }:
        return
    x = np.asarray(line.get_xdata(orig=False))
    y = np.asarray(line.get_ydata(orig=False))
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y) or not len(x):
        return
    try:
        xy = np.column_stack((x.astype(float), y.astype(float)))
    except (TypeError, ValueError):
        return

    current = line.get_markevery()
    previous = getattr(line, "_awesomefigures_elegant_applied", None)
    if (not hasattr(line, "_awesomefigures_elegant_applied")
            or not _same_markevery(current, previous)):
        line._awesomefigures_marker_source = current

    vertices = ax.transData.transform(xy)
    candidates = _marker_candidates(line, xy, vertices, ax)
    if candidates is None or not len(candidates):
        return
    candidates = np.unique(candidates.astype(int))
    # Full marker radius and edge stroke, plus configurable breathing room.
    inset = (inset_pt + line.get_markersize() / 2.
             + line.get_markeredgewidth() / 2.) * ax.figure.dpi / 72.
    bbox = ax.bbox
    screen = vertices[candidates]
    valid = (
        np.isfinite(screen).all(axis=1)
        & (screen[:, 0] >= bbox.x0 + inset)
        & (screen[:, 0] <= bbox.x1 - inset)
        & (screen[:, 1] >= bbox.y0 + inset)
        & (screen[:, 1] <= bbox.y1 - inset)
    )
    candidates, screen = candidates[valid], screen[valid]
    if not len(candidates):
        selected = []
    else:
        # Sample evenly over the longest occupied *screen* axis. This avoids
        # excessive symbols on highly oversampled or nonuniform spline grids.
        span = np.ptp(screen, axis=0)
        dimension = int(np.argmax(span))
        order = np.argsort(screen[:, dimension], kind="stable")
        candidates = candidates[order]
        screen = screen[order]
        # At least spacing_pt between marker centres, in physical points.
        spacing_px = spacing_pt * ax.figure.dpi / 72.
        room = max(1, 1 + int(span[dimension] // spacing_px))
        target_count = min(count, room, len(candidates))
        targets = np.linspace(screen[0, dimension],
                              screen[-1, dimension], target_count)
        chosen = []
        for target in targets:
            nearest = np.argsort(
                np.abs(screen[:, dimension] - target), kind="stable"
            )
            for j in nearest:
                point = screen[j]
                if all(np.linalg.norm(point - q) >= spacing_px - 1e-7
                       for q in chosen):
                    chosen.append(point)
                    break
        selected = sorted(
            int(candidates[np.argmin(
                np.linalg.norm(screen - point, axis=1)
            )])
            for point in chosen
        )

    line.set_markevery(selected)
    line._awesomefigures_elegant_applied = selected


def thin_line_markers(
    ax: Axes, *, marker_inset_pt: float = 6.0,
    marker_count: int = 7, marker_min_spacing_pt: float = 38.0
) -> Axes:
    """Space all line markers across an Axes; do not change the line curves.

    Called by both 'heri' and 'elegante' at export. For individual axes it may
    also be called directly after plotting. Marker-only observation plots and
    Matplotlib scatter collections remain unchanged.
    """
    if not isinstance(ax, Axes):
        raise TypeError("ax must be a Matplotlib Axes.")
    if (not math.isfinite(marker_inset_pt) or marker_inset_pt < 0
            or not math.isfinite(marker_min_spacing_pt)
            or marker_min_spacing_pt <= 0
            or not isinstance(marker_count, int) or marker_count < 1):
        raise ValueError(
            "marker_inset_pt must be nonnegative; marker_count and "
            "marker_min_spacing_pt must be positive."
        )
    if ax.name != "rectilinear":
        return ax
    # Ensure transforms use the final autoscaled limits. In the Heri preset,
    # unlike Elegante, Matplotlib may defer autoscaling until Axes.draw().
    # Without this, pixels measured before draw differ from the final canvas.
    ax.get_xlim()
    ax.get_ylim()
    for line in ax.lines:
        _line_marker_indices(
            line, ax, inset_pt=marker_inset_pt,
            count=marker_count, spacing_pt=marker_min_spacing_pt
        )
    return ax


def apply_elegant_axes(
    ax: Axes,
    *,
    target_xticks: int = 6,
    target_yticks: int = 5,
    marker_inset_pt: float = 6.0,
    marker_count: int = 7,
    marker_min_spacing_pt: float = 38.0,
    force_zero: bool = False,
    padding: float = 0.0,
) -> Axes:
    """Align endpoint ticks with spines and keep line markers inside the axes.

    Intended for standard linear numeric Cartesian axes. Nonlinear, categorical,
    dates, shared/twinned, inverted, and 3D axes are left unchanged. Explicit
    manual xlim/ylim settings are respected. Scatter points are never hidden.
    The line itself is *never* clipped or shortened by marker placement.
    """
    if not isinstance(ax, Axes):
        raise TypeError("ax must be a Matplotlib Axes.")
    if (not math.isfinite(marker_inset_pt) or marker_inset_pt < 0
            or not isinstance(marker_count, int) or marker_count < 1
            or not math.isfinite(marker_min_spacing_pt)
            or marker_min_spacing_pt <= 0):
        raise ValueError("Marker spacing/count must be positive, inset nonnegative.")
    if not math.isfinite(padding) or padding < 0:
        raise ValueError("padding must be nonnegative and finite.")
    # Keep the user's tick preferences for subsequent automatic renders.
    ax._awesomefigures_elegant_options = dict(
        target_xticks=target_xticks, target_yticks=target_yticks,
        marker_inset_pt=marker_inset_pt, marker_count=marker_count,
        marker_min_spacing_pt=marker_min_spacing_pt,
        force_zero=force_zero, padding=padding,
    )
    if (ax.name != "rectilinear"
            or ax.get_xscale() != "linear" or ax.get_yscale() != "linear"
            or ax.xaxis.get_converter() is not None or ax.yaxis.get_converter() is not None
            or ax.xaxis.get_inverted() or ax.yaxis.get_inverted()
            or len(ax.get_shared_x_axes().get_siblings(ax)) > 1
            or len(ax.get_shared_y_axes().get_siblings(ax)) > 1):
        return ax

    def apply_one(axis, data, target):
        if not axis._get_autoscale_on():
            return
        lo, hi = (float(data[0]), float(data[1]))
        if not (math.isfinite(lo) and math.isfinite(hi)):
            return
        # For a scatter-only plot, preserve fully visible boundary points.
        # The next nice tick lies outside the extremal data position.
        extra = padding
        if ax.collections and not ax.lines:
            extra = max(extra, 0.015)
        start, stop, ticks = nice_tick_bounds(
            lo, hi, target_ticks=target, padding=extra, force_zero=force_zero
        )
        axis.set_ticks(ticks)
        if axis.axis_name == "x":
            ax.set_xlim(start, stop, auto=True)
        else:
            ax.set_ylim(start, stop, auto=True)

    apply_one(ax.xaxis, ax.dataLim.intervalx, target_xticks)
    apply_one(ax.yaxis, ax.dataLim.intervaly, target_yticks)
    thin_line_markers(
        ax, marker_inset_pt=marker_inset_pt,
        marker_count=marker_count, marker_min_spacing_pt=marker_min_spacing_pt
    )
    return ax
