"""Matplotlib publication styles for awesomefigures.

The Heri preset follows the publication figures in
heri-espino/Bayesian-Uncertainty-in-WTI-APOs: compact Wiley-like typography,
white-grid axes, a custom categorical cycle, an iridescent continuous map,
and hybrid PDF output with only dense artists rasterized.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import shutil
import subprocess
from typing import Iterator, Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap

from .palette import color_for_luminance
from .color_spaces import to_hex
from .named_palettes import get_named_palette, named_palette


StyleName = Literal["heri", "elegante", "default", "matplotlib"]

HERI_LATEX_PREAMBLE = (
    r"\usepackage[T1]{fontenc}"
    r"\usepackage{utopia}"
    r"\usepackage[defaultmathsizes,italic]{mathastext}"
    r"\usepackage{amsmath,amssymb}"
)

# Original WTI publication categorical palette (not an official Paul Tol scheme).
HERI_PALETTE = (
    "#97001c",
    "#0083f9",
    "#00b49c",
    "#ffc600",
    "#f198ff",
)

# Paper defaults: maximize luminance separation for the first three
# categorical series, before adding intermediate gray levels for series 4-5.
# The original WTI palette remains available with palette="legacy".
_HERI_PRINT_PALETTE = tuple(
    to_hex(color_for_luminance(y, hue, chroma=0.13).rgb)
    for y, hue in zip(
        (0.50, 0.17, 0.035, 0.29, 0.085),
        (25, 150, 275, 210, 340),
    )
)

HERI_NEUTRAL = {
    "black": "#111111",
    "dark": "#3A3A3A",
    "mid": "#777777",
    "light": "#B0B0B0",
    "grid": "#D8D8D8",
}

HERI_IRIDESCENT_HEX = (
    "#FEFBE9", "#FCF7D5", "#F5F3C1", "#EAF0B5", "#DDECBF", "#D0E7CA",
    "#C2E3D2", "#B5DDD8", "#A8D8DC", "#9BD2E1", "#8DCBE4", "#81C4E7",
    "#7BBCE7", "#7EB2E4", "#88A5DD", "#9398D2", "#9B8AC4", "#9D7DB2",
    "#9A709E", "#906388", "#805770", "#684957", "#46353A",
)

HERI_BAD_DATA_COLOR = "#999999"
HERI_CMAP = LinearSegmentedColormap.from_list(
    "heri_iridescent",
    HERI_IRIDESCENT_HEX,
    N=256,
)
HERI_CMAP.set_bad(HERI_BAD_DATA_COLOR)

HERI_SAVEFIG_KWARGS = {
    "dpi": 600,
    "bbox_inches": "tight",
    "pad_inches": 0.035,
    "facecolor": "white",
    "edgecolor": "white",
    "transparent": False,
}

_RASTER_PATCHED = False
_RASTERIZE_DENSE = False
_ACCESSIBLE_SCATTER = False
_ELEGANT_ENABLED = False
_ELEGANT_DRAW_PATCHED = False


def _install_elegant_draw() -> None:
    """Finalize numeric axes immediately before visible or exported rendering.

    Matplotlib rcParams cannot express "endpoint ticks must equal view limits".
    A lightweight draw hook does this when the elegante preset is active,
    while an explicit apply_elegant_axes call also works without the preset.
    """
    global _ELEGANT_DRAW_PATCHED
    if _ELEGANT_DRAW_PATCHED or getattr(Axes, "_awesomefigures_elegant_draw", False):
        _ELEGANT_DRAW_PATCHED = True
        return
    original_draw = Axes.draw

    def draw(self, renderer):
        if _ELEGANT_ENABLED:
            from .elegant import apply_elegant_axes
            opts = getattr(self, "_awesomefigures_elegant_options", {})
            apply_elegant_axes(self, **opts)
        return original_draw(self, renderer)

    Axes.draw = draw
    Axes._awesomefigures_elegant_draw = True
    _ELEGANT_DRAW_PATCHED = True


def available_styles() -> tuple[str, ...]:
    """Return style names understood by set_style."""
    return ("heri", "elegante", "default")


def _latex_stack_available() -> bool:
    """Return whether the Wiley-like Utopia TeX stack is available."""
    if shutil.which("latex") is None:
        return False
    kpsewhich = shutil.which("kpsewhich")
    if kpsewhich is None:
        return False

    for package in ("utopia.sty", "mathastext.sty", "amsmath.sty", "amssymb.sty"):
        try:
            result = subprocess.run(
                [kpsewhich, package],
                check=False,
                capture_output=True,
                text=True,
                timeout=3,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        if result.returncode != 0 or not result.stdout.strip():
            return False
    return True


def _set_rasterized(artist):
    if hasattr(artist, "set_rasterized"):
        artist.set_rasterized(True)
    for child in getattr(artist, "collections", []):
        if hasattr(child, "set_rasterized"):
            child.set_rasterized(True)
    return artist


def _install_rasterized_defaults() -> None:
    """Rasterize dense artists conditionally while leaving ordinary lines vector."""
    global _RASTER_PATCHED
    if _RASTER_PATCHED or getattr(Axes, "_awesomefigures_rasterized_defaults", False):
        _RASTER_PATCHED = True
        return

    _RASTER_PATCHED = True
    Axes._awesomefigures_rasterized_defaults = True

    original_scatter = Axes.scatter
    original_hexbin = Axes.hexbin
    original_contourf = Axes.contourf
    original_pcolormesh = Axes.pcolormesh
    original_imshow = Axes.imshow
    original_fill_between = Axes.fill_between

    def scatter(self, *args, **kwargs):
        if _ACCESSIBLE_SCATTER and "marker" not in kwargs:
            from .api import DEFAULT_MARKERS
            index = getattr(self, "_awesomefigures_scatter_index", 0)
            kwargs["marker"] = DEFAULT_MARKERS[index % len(DEFAULT_MARKERS)]
            self._awesomefigures_scatter_index = index + 1
        if _RASTERIZE_DENSE:
            kwargs.setdefault("rasterized", True)
        return original_scatter(self, *args, **kwargs)

    def hexbin(self, *args, **kwargs):
        if _RASTERIZE_DENSE:
            kwargs.setdefault("rasterized", True)
        return original_hexbin(self, *args, **kwargs)

    def contourf(self, *args, **kwargs):
        artist = original_contourf(self, *args, **kwargs)
        return _set_rasterized(artist) if _RASTERIZE_DENSE else artist

    def pcolormesh(self, *args, **kwargs):
        if _RASTERIZE_DENSE:
            kwargs.setdefault("rasterized", True)
        return original_pcolormesh(self, *args, **kwargs)

    def imshow(self, *args, **kwargs):
        if _RASTERIZE_DENSE:
            kwargs.setdefault("rasterized", True)
        return original_imshow(self, *args, **kwargs)

    def fill_between(self, *args, **kwargs):
        artist = original_fill_between(self, *args, **kwargs)
        return _set_rasterized(artist) if _RASTERIZE_DENSE else artist

    Axes.scatter = scatter
    Axes.hexbin = hexbin
    Axes.contourf = contourf
    Axes.pcolormesh = pcolormesh
    Axes.imshow = imshow
    Axes.fill_between = fill_between

    try:
        from mpl_toolkits.mplot3d.axes3d import Axes3D
    except Exception:
        return

    if getattr(Axes3D, "_awesomefigures_rasterized_defaults", False):
        return

    Axes3D._awesomefigures_rasterized_defaults = True
    original_plot_surface = Axes3D.plot_surface
    original_plot_trisurf = Axes3D.plot_trisurf

    def plot_surface(self, *args, **kwargs):
        if _RASTERIZE_DENSE:
            kwargs.setdefault("rasterized", True)
        return original_plot_surface(self, *args, **kwargs)

    def plot_trisurf(self, *args, **kwargs):
        if _RASTERIZE_DENSE:
            kwargs.setdefault("rasterized", True)
        return original_plot_trisurf(self, *args, **kwargs)

    Axes3D.plot_surface = plot_surface
    Axes3D.plot_trisurf = plot_trisurf


def _font_rcparams(font: str, *, use_tex: bool) -> dict:
    """Return rcParams for the requested text family."""
    requested = font.strip()
    key = requested.lower()

    if use_tex:
        return {
            "font.family": "serif",
            "text.usetex": True,
            "text.latex.preamble": HERI_LATEX_PREAMBLE,
        }

    if key in {"utopia", "wiley", "wiley utopia"}:
        return {
            "font.family": "serif",
            "font.serif": ["Utopia", "STIX Two Text", "STIXGeneral", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "text.usetex": False,
        }

    if key in {"stix", "stix two text"}:
        return {
            "font.family": "serif",
            "font.serif": ["STIX Two Text", "STIXGeneral", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "text.usetex": False,
        }

    if key in {"serif", "default serif"}:
        return {
            "font.family": "serif",
            "mathtext.fontset": "stix",
            "text.usetex": False,
        }

    if key in {"sans", "sans-serif", "default sans"}:
        return {
            "font.family": "sans-serif",
            "mathtext.fontset": "stix",
            "text.usetex": False,
        }

    # Arbitrary Matplotlib font name, e.g. Arial, Helvetica, Aptos or Calibri.
    return {
        "font.family": requested,
        "mathtext.fontset": "stix",
        "text.usetex": False,
    }


def _heri_rcparams(*, font: str, use_tex: bool, palette: str) -> dict:
    """Return the WTI publication rcParams with a user-selectable font."""
    params = {
        "font.size": 8.5,
        "axes.labelsize": 8.5,
        "axes.titlesize": 9.0,
        "legend.fontsize": 7.5,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "axes.unicode_minus": False,
        "figure.dpi": 180,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.035,
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.85,
        "axes.edgecolor": HERI_NEUTRAL["dark"],
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "axes.axisbelow": True,
        "axes.grid": True,
        "grid.color": HERI_NEUTRAL["grid"],
        "grid.linewidth": 0.50,
        "grid.alpha": 0.72,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "lines.linewidth": 1.60,
        "lines.markersize": 4.5,
        "legend.frameon": False,
        "legend.borderaxespad": 0.25,
        "legend.handlelength": 1.8,
        "axes.prop_cycle": (
            mpl.cycler(color=(
                list(_HERI_PRINT_PALETTE) if palette == "print-safe" else
                list(HERI_PALETTE) if palette == "legacy" else
                named_palette(palette, as_hex=True)
            ))
            + mpl.cycler(marker=[
                ("o", "s", "^", "D", "X", "P", "v", "<", ">", "*")[i % 10]
                for i in range(
                    5 if palette in {"print-safe", "legacy"}
                    else len(get_named_palette(palette).colors)
                )
            ])
            + mpl.cycler(linestyle=[
                ("-", "--", ":", "-.", (0, (5, 2)), (0, (3, 1, 1, 1)))[i % 6]
                for i in range(
                    5 if palette in {"print-safe", "legacy"}
                    else len(get_named_palette(palette).colors)
                )
            ])
        ),
    }
    params.update(_font_rcparams(font, use_tex=use_tex))
    return params


def set_style(
    style: StyleName | str = "heri",
    *,
    font: str = "utopia",
    use_tex: bool | Literal["auto"] = "auto",
    rasterize: bool = True,
    palette: str = "print-safe",
) -> None:
    """Apply a named global Matplotlib style.

    By default, the Heri style uses a print-safe categorical cycle with
    separated luminances and redundant marker/linestyle encoding.
    Set palette="legacy" to recover the original WTI APO color cycle.
    The font is an independent choice (Arial, STIX, Utopia, etc.).

    With use_tex="auto", external LaTeX is attempted only for the Utopia font.
    Custom fonts are rendered directly by Matplotlib so their family choice is
    respected.

    With rasterize=True, only dense artists are rasterized. Ordinary plot
    lines, errorbars, axes, text, ticks, legends, and annotations remain vector.
    """
    global _RASTERIZE_DENSE, _ACCESSIBLE_SCATTER, _ELEGANT_ENABLED

    name = str(style).strip().lower()
    if name in {"default", "matplotlib"}:
        _RASTERIZE_DENSE = False
        _ACCESSIBLE_SCATTER = False
        _ELEGANT_ENABLED = False
        mpl.rcdefaults()
        return

    if name not in {"heri", "elegante"}:
        choices = ", ".join(repr(x) for x in available_styles())
        raise ValueError(f"Unknown style {style!r}. Available styles: {choices}.")

    if not isinstance(font, str) or not font.strip():
        raise ValueError("font must be a non-empty Matplotlib font-family name.")
    if palette not in ("print-safe", "legacy"):
        try:
            selected = get_named_palette(palette)
        except KeyError as exc:
            raise ValueError(
                "Unknown palette. Use 'print-safe', 'legacy', or a "
                "categorical name from available_named_palettes()."
            ) from exc
        if selected.kind != "categorical":
            raise ValueError(
                "Sequential/diverging colormaps cannot be line-cycle palettes. "
                "Use named_colormap(name) for heatmaps."
            )
        palette = selected.name

    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        plt.style.use("default")

    _install_rasterized_defaults()
    _RASTERIZE_DENSE = bool(rasterize)
    _ACCESSIBLE_SCATTER = True
    _ELEGANT_ENABLED = name == "elegante"
    if _ELEGANT_ENABLED:
        _install_elegant_draw()

    font_key = font.strip().lower()
    if use_tex == "auto":
        resolved_use_tex = (
            font_key in {"utopia", "wiley", "wiley utopia"}
            and _latex_stack_available()
        )
    elif isinstance(use_tex, bool):
        resolved_use_tex = use_tex
    else:
        raise ValueError("use_tex must be True, False, or 'auto'.")

    if resolved_use_tex and font_key not in {"utopia", "wiley", "wiley utopia"}:
        raise ValueError(
            "Custom fonts cannot be guaranteed through the Heri LaTeX stack. "
            "Use use_tex=False (or use_tex='auto') for fonts such as Arial."
        )

    params = _heri_rcparams(font=font, use_tex=resolved_use_tex, palette=palette)
    if name == "elegante":
        params.update({
            "axes.xmargin": 0.0,
            "axes.ymargin": 0.0,
            "axes.linewidth": 0.95,
            "axes.edgecolor": "#202020",
            "grid.alpha": 0.30,
            "grid.linewidth": 0.45,
        })
    mpl.rcParams.update(params)


@contextmanager
def style_context(
    style: StyleName | str = "heri",
    *,
    font: str = "utopia",
    use_tex: bool | Literal["auto"] = "auto",
    rasterize: bool = True,
    palette: str = "print-safe",
) -> Iterator[None]:
    """Temporarily apply a style and restore previous Matplotlib state."""
    global _RASTERIZE_DENSE, _ACCESSIBLE_SCATTER, _ELEGANT_ENABLED

    previous = mpl.rcParams.copy()
    previous_rasterize = _RASTERIZE_DENSE
    previous_scatter = _ACCESSIBLE_SCATTER
    previous_elegant = _ELEGANT_ENABLED
    try:
        set_style(
            style,
            font=font,
            use_tex=use_tex,
            rasterize=rasterize,
            palette=palette,
        )
        yield
    finally:
        _RASTERIZE_DENSE = previous_rasterize
        _ACCESSIBLE_SCATTER = previous_scatter
        _ELEGANT_ENABLED = previous_elegant
        mpl.rcParams.update(previous)


def panel_label(
    ax,
    label: str,
    *,
    x: float = -0.12,
    y: float = 1.05,
    **kwargs,
):
    """Add the bold A/B/C panel label used by the WTI publication figures."""
    options = {
        "transform": ax.transAxes,
        "fontweight": "bold",
        "va": "bottom",
        "ha": "left",
        "color": HERI_NEUTRAL["dark"],
    }
    options.update(kwargs)
    return ax.text(x, y, label, **options)


def save_figure(
    fig,
    path: str | Path,
    *,
    dpi: int | None = None,
    close: bool = False,
    metadata: dict | None = None,
    **kwargs,
) -> Path:
    """Save a Heri-style hybrid publication figure.

    If path has no suffix, .pdf is appended. Dense artists remain raster layers
    at 600 dpi by default while ordinary lines and typography remain vector.
    """
    target = Path(path)
    if not target.suffix:
        target = target.with_suffix(".pdf")
    target.parent.mkdir(parents=True, exist_ok=True)

    save_kwargs = dict(HERI_SAVEFIG_KWARGS)
    save_kwargs.update(kwargs)
    if dpi is not None:
        save_kwargs["dpi"] = dpi
    if metadata is not None and target.suffix.lower() == ".pdf":
        save_kwargs["metadata"] = metadata

    fig.savefig(target, **save_kwargs)
    if close:
        plt.close(fig)
    return target
