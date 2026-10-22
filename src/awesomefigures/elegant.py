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


def _line_marker_indices(line, ax: Axes, *, inset_pt: float, count: int) -> None:
    """Only reposition visible markers; retain the entire unchanged line."""
    marker = line.get_marker()
    if marker is None or str(marker).lower() in {"none", "", " ", "nan"}:
        return
    if not line.get_visible():
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
    previous = getattr(line, "_awesomefigures_elegant_applied", object())
    if current != previous:
        line._awesomefigures_elegant_source = current
    source = getattr(line, "_awesomefigures_elegant_source", current)

    if source is None:
        candidates = np.arange(len(x), dtype=int)
    elif isinstance(source, (int, np.integer)) and not isinstance(source, bool):
        if source <= 0:
            return
        candidates = np.arange(0, len(x), int(source), dtype=int)
    elif isinstance(source, slice):
        candidates = np.arange(len(x))[source]
    elif (isinstance(source, tuple) and len(source) == 2
          and all(isinstance(v, (int, np.integer)) for v in source)):
        offset, stride = source
        if stride <= 0:
            return
        candidates = np.arange(int(offset), len(x), int(stride), dtype=int)
    elif isinstance(source, (list, np.ndarray, tuple)):
        values = np.asarray(source)
        if values.ndim != 1 or values.dtype.kind not in "iu":
            return  # Preserve float/arc-length or other Matplotlib conventions.
        candidates = np.arange(len(x))[values]
    else:
        return

    if not len(candidates):
        return
    vertices = ax.transData.transform(xy[candidates])
    bbox = ax.bbox
    # Diameter of matplotlib Line2D markers is measured in typographic points.
    clearance = (inset_pt + line.get_markersize() / 2.0
                 + line.get_markeredgewidth() / 2.0) * ax.figure.dpi / 72.0
    interior = (
        np.isfinite(vertices).all(axis=1)
        & (vertices[:, 0] >= bbox.x0 + clearance)
        & (vertices[:, 0] <= bbox.x1 - clearance)
        & (vertices[:, 1] >= bbox.y0 + clearance)
        & (vertices[:, 1] <= bbox.y1 - clearance)
    )
    accepted = np.asarray(candidates)[interior]
    if source is None and len(accepted) > count:
        # Sparse equally distributed *visible* marker locations for dense
        # spline sampling. Data and line interpolation are untouched.
        accepted = accepted[np.unique(np.linspace(
            0, len(accepted) - 1, count, dtype=int
        ))]
    selected = accepted.astype(int).tolist()
    line.set_markevery(selected)
    line._awesomefigures_elegant_applied = selected


def apply_elegant_axes(
    ax: Axes,
    *,
    target_xticks: int = 6,
    target_yticks: int = 5,
    marker_inset_pt: float = 4.0,
    marker_count: int = 9,
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
            or not isinstance(marker_count, int) or marker_count < 1):
        raise ValueError("marker_inset_pt and marker_count must be nonnegative/positive.")
    if not math.isfinite(padding) or padding < 0:
        raise ValueError("padding must be nonnegative and finite.")
    # Keep the user's tick preferences for subsequent automatic renders.
    ax._awesomefigures_elegant_options = dict(
        target_xticks=target_xticks, target_yticks=target_yticks,
        marker_inset_pt=marker_inset_pt, marker_count=marker_count,
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
    for line in ax.lines:
        _line_marker_indices(line, ax, inset_pt=marker_inset_pt, count=marker_count)
    return ax
