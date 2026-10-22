"""High-level categorical chart helpers using print-friendly defaults."""
from __future__ import annotations

from collections.abc import Sequence

from .api import plot_scheme


def pie_plot(
    values: Sequence[float],
    *,
    labels: Sequence[str] | None = None,
    ax=None,
    colors=None,
    edgecolor: str = "white",
    linewidth: float = 1.5,
    **kwargs,
):
    """Draw a pie chart with clean white boundaries between wedges.

    Colors default to print-separated luminances, using a distinct hue for
    each wedge. Edge defaults are independent of Matplotlib patch styles
    and can be overridden with wedgeprops={'edgecolor': ..., ...}.

    Returns (wedges, texts), or (wedges, texts, autotexts) if autopct was
    supplied, matching matplotlib.axes.Axes.pie.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    vals = np.asarray(values, dtype=float)
    if vals.ndim != 1 or vals.size < 1 or not np.all(np.isfinite(vals)):
        raise ValueError("values must be a nonempty finite 1D sequence.")
    if np.any(vals < 0) or not np.any(vals > 0):
        raise ValueError("values must be nonnegative and contain a positive value.")
    if ax is None:
        _, ax = plt.subplots()
    if colors is None:
        hues = [(25.0 + 360.0 * i / vals.size) % 360 for i in range(vals.size)]
        colors = [style["color"] for style in plot_scheme(hues)]
    wedgeprops = {"edgecolor": edgecolor, "linewidth": linewidth}
    wedgeprops.update(kwargs.pop("wedgeprops", {}))
    kwargs.setdefault("startangle", 90)
    kwargs.setdefault("counterclock", False)
    return ax.pie(vals, labels=labels, colors=colors, wedgeprops=wedgeprops, **kwargs)
