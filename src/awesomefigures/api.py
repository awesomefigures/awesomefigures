"""High-level Seaborn-like public helpers."""

from __future__ import annotations

from collections.abc import Sequence

from .palette import Palette, color_for_luminance
from .color_spaces import contrast_ratio
from .contrast import luminance_ladder, print_safe_luminances
from .presets import get_palette
from .named_palettes import available_named_palettes, named_palette, get_named_palette


def contrast_palette(
    hues: Sequence[float] | str,
    *,
    ratio: float | None = None,
    start_luminance: float | None = None,
    chroma: float | None = None,
) -> Palette:
    """Build one contrast-controlled color per supplied hue.

    Hue hues[k] is assigned to luminance level Y_k. Therefore a list
    of five hues directly produces a five-color palette whose adjacent WCAG
    contrast ratios are ratio.

    Parameters
    ----------
    hues:
        Hue angles in OKLCH degrees. The number of hues determines the number
        of colors.
    ratio:
        Desired WCAG contrast ratio between adjacent colors.
    start_luminance:
        Relative luminance of the first (lightest) color.
    chroma:
        Requested OKLCH chroma. Chroma is reduced automatically when necessary
        to remain inside sRGB.
    """
    if isinstance(hues, str):
        if hues.strip().lower() in available_named_palettes() or hues.strip().lower() in {"colorblind", "wong", "okabe_ito", "okabeito", "set2", "dark2", "tableau10", "rd-bu"}:
            raise ValueError(
                "contrast_palette() constructs a WCAG luminance ladder, whereas "
                "named historical palettes preserve their original RGB colours. "
                "Use color_palette(name) or named_palette(name) instead."
            )
        preset = get_palette(hues)
        hues = preset.hues
        ratio = preset.ratio if ratio is None else ratio
        start_luminance = preset.start_luminance if start_luminance is None else start_luminance
        chroma = preset.chroma if chroma is None else chroma
    ratio = 1.5 if ratio is None else ratio
    start_luminance = 0.95 if start_luminance is None else start_luminance
    chroma = 0.13 if chroma is None else chroma
    if len(hues) == 0:
        raise ValueError("At least one hue is required.")
    ys = luminance_ladder(
        len(hues),
        ratio,
        start_luminance=start_luminance,
    )
    return Palette(
        color_for_luminance(y, hue, chroma=chroma)
        for y, hue in zip(ys, hues, strict=True)
    )


def color_palette(
    hues: Sequence[float] | str,
    *,
    ratio: float | None = None,
    start_luminance: float | None = None,
    chroma: float | None = None,
    alpha: float = 1.0,
    background: str | Sequence[float] = "white",
    preserve_apparent: bool = True,
    alpha_strategy: str = "perceptual",
    as_hex: bool = False,
    n: int | None = None,
):
    """Return plotting-ready colors from a contrast-controlled palette.

    This is the convenience function intended for ordinary Matplotlib usage,
    analogous to a palette constructor in a plotting library.

    By default it returns Matplotlib-ready RGBA tuples. Set as_hex=True for
    opaque hexadecimal target colors; in that mode alpha-related arguments are
    not applied.
    """
    if isinstance(hues, str):
        try:
            get_named_palette(hues)
        except KeyError:
            pass
        else:
            if any(value is not None for value in (ratio, start_luminance, chroma)):
                raise ValueError(
                    "Named historical palettes preserve their exact HEX values; "
                    "ratio/start_luminance/chroma cannot be applied. "
                    "Pass hue angles to generate a contrast-controlled palette."
                )
            return named_palette(
                hues, n=n, alpha=alpha, background=background,
                preserve_apparent=preserve_apparent,
                alpha_strategy=alpha_strategy, as_hex=as_hex,
            )
    if n is not None:
        raise ValueError("n is only valid for a built-in named palette; hue lists define their size.")
    p = contrast_palette(
        hues,
        ratio=ratio,
        start_luminance=start_luminance,
        chroma=chroma,
    )
    if as_hex:
        return p.hex
    return p.mpl_colors(
        alpha=alpha,
        background=background,
        preserve_apparent=preserve_apparent,
        alpha_strategy=alpha_strategy,
    )


def show_palette(
    hues: Sequence[float] | str,
    *,
    ratio: float | None = None,
    start_luminance: float | None = None,
    chroma: float | None = None,
    alpha: float = 1.0,
    background: str | Sequence[float] = "white",
    preserve_apparent: bool = True,
    alpha_strategy: str = "perceptual",
    ax=None,
    n: int | None = None,
):
    """Draw a compact Matplotlib swatch preview and return its axes."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    from .alpha import composite
    from .color_spaces import to_rgb

    hex_codes = color_palette(
        hues, ratio=ratio, start_luminance=start_luminance, chroma=chroma,
        as_hex=True, n=n,
    )
    rendered = color_palette(
        hues, ratio=ratio, start_luminance=start_luminance, chroma=chroma,
        alpha=alpha, background=background,
        preserve_apparent=preserve_apparent,
        alpha_strategy=alpha_strategy, n=n,
    )
    if ax is None:
        _, ax = plt.subplots(figsize=(max(4.0, len(hex_codes) * 1.25), 1.7))
    for i, (code, rgba) in enumerate(zip(hex_codes, rendered)):
        ax.add_patch(Rectangle(
            (i, 0), 1, 1, facecolor=rgba, edgecolor="none"
        ))
        displayed_rgb = composite(rgba[:3], background, rgba[3])
        text_color = (
            "black" if contrast_ratio(displayed_rgb, "black")
            >= contrast_ratio(displayed_rgb, "white") else "white"
        )
        ax.text(i + .5, .5, code, ha="center", va="center",
                color=text_color, fontsize=9, family="monospace")

    ax.set_xlim(0, len(hex_codes))
    ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.axis("off")
    return ax


DEFAULT_MARKERS = ("o", "s", "^", "D", "X", "P", "v", "<", ">", "*")
DEFAULT_LINESTYLES = ("-", "--", ":", "-.", (0, (5, 2)), (0, (3, 1, 1, 1)))


def plot_scheme(
    hues: Sequence[float] | str,
    *,
    ratio: float | None = None,
    start_luminance: float | None = None,
    chroma: float | None = None,
    alpha: float = 1.0,
    background: str | Sequence[float] = "white",
    preserve_apparent: bool = True,
    alpha_strategy: str = "perceptual",
    markers: Sequence[str] | None = None,
    linestyles: Sequence[object] | None = None,
    n: int | None = None,
) -> list[dict]:
    """Return Matplotlib style dictionaries for redundant series encoding.

    Each returned dictionary contains color, marker, and linestyle. Colors are
    generated by the contrast-controlled palette system, while marker and line
    styles cycle independently. With no explicitly specified luminance or
    contrast ratio, hues are assigned *adaptive print-safe luminances*:
    two or three series have much wider gray-scale separation than five.
    Explicit values and named presets are never overridden. The result
    also uses different marker and line styles for redundant encoding.

    Parameters
    ----------
    hues:
        Hue angle for each desired series.
    markers:
        Optional marker sequence. Defaults to a set of distinct Matplotlib
        markers and cycles if shorter than the hue list.
    linestyles:
        Optional line-style sequence. Defaults to a mix of solid, dashed,
        dotted, dash-dot, and custom dash patterns and cycles if shorter than
        the hue list.
    """
    builtin = False
    if isinstance(hues, str):
        try:
            get_named_palette(hues)
            builtin = True
        except KeyError:
            pass
    preset = get_palette(hues) if isinstance(hues, str) and not builtin else None
    # Adaptive paper defaults: with only 2-3 series, distribute luminances
    # across the available range instead of giving them almost equal grays.
    # Any explicit ratio/start or registered preset retains its own contract.
    if not builtin and preset is None and ratio is None and start_luminance is None:
        count = len(hues)
        if count:
            luminances = print_safe_luminances(count)
            start_luminance = float(luminances[0])
            if count >= 2:
                ratio = float(
                    ((luminances[0] + .05) / (luminances[-1] + .05)) ** (1 / (count - 1))
                )
            else:
                ratio = 1.0
    colors = color_palette(
        hues,
        ratio=ratio,
        start_luminance=start_luminance,
        chroma=chroma,
        alpha=alpha,
        background=background,
        preserve_apparent=preserve_apparent,
        alpha_strategy=alpha_strategy,
        n=n,
    )
    if markers is None and preset is not None:
        markers = preset.markers
    if linestyles is None and preset is not None:
        linestyles = preset.linestyles
    marker_values = tuple(DEFAULT_MARKERS if markers is None else markers)
    line_values = tuple(DEFAULT_LINESTYLES if linestyles is None else linestyles)
    if not marker_values:
        raise ValueError("markers must contain at least one marker.")
    if not line_values:
        raise ValueError("linestyles must contain at least one style.")

    return [
        {
            "color": color,
            "marker": marker_values[i % len(marker_values)],
            "linestyle": line_values[i % len(line_values)],
        }
        for i, color in enumerate(colors)
    ]


def scatter_scheme(hues: Sequence[float] | str, **kwargs) -> list[dict]:
    """Return distinct colors and group markers to pass into Axes.scatter.

    Line styles are omitted since Matplotlib scatter does not accept them.
    Registered palettes and plot_scheme parameters are fully supported.
    """
    return [
        {"color": item["color"], "marker": item["marker"]}
        for item in plot_scheme(hues, **kwargs)
    ]
