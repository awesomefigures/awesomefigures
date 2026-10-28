"""Publication-scale Matplotlib figures fitted to a trusted LaTeX document.

A short LaTeX probe reads dimensions after the document preamble. The probe
does not compile the manuscript body and does not alter the original .tex file.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import math
import re
import shutil
import subprocess
import tempfile
import warnings
from typing import Iterator, Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.text import Text

from .style import save_figure, style_context

TEX_PT_PER_INCH = 72.27
_ENGINE = ("pdflatex", "xelatex", "lualatex")
_BEGIN_DOCUMENT = re.compile(r"(?m)^[ \t]*\\begin\s*\{\s*document\s*\}")
_DIMENSION = re.compile(
    r"CCLAYOUT:(COLUMN|TEXT|FONT|BASELINE|FAMILY|FONTNAME)=([^\r\n]+)"
)


class LatexProbeError(RuntimeError):
    """Raised when the trusted LaTeX preamble cannot be measured."""


@dataclass(frozen=True)
class LatexLayout:
    """Physical LaTeX layout measured in TeX points (72.27 pt per inch).

    Use inspect_latex for real documents, or from_dimensions if LaTeX is not
    installed yet. Family/fontname are informative; see the PGF font note.
    """

    columnwidth_pt: float
    textwidth_pt: float
    fontsize_pt: float
    baselineskip_pt: float | None = None
    font_family: str = "unknown"
    font_name: str = "unknown"

    def __post_init__(self) -> None:
        values = (self.columnwidth_pt, self.textwidth_pt, self.fontsize_pt)
        if not all(math.isfinite(x) and x > 0 for x in values):
            raise ValueError("All LaTeX dimensions and font size must be positive and finite.")
        if self.columnwidth_pt > self.textwidth_pt * 1.001:
            raise ValueError("columnwidth cannot exceed textwidth.")
        if self.baselineskip_pt is not None and (
            not math.isfinite(self.baselineskip_pt) or self.baselineskip_pt <= 0
        ):
            raise ValueError("baselineskip must be a positive point measurement.")

    @classmethod
    def from_dimensions(
        cls,
        *,
        columnwidth_pt: float,
        textwidth_pt: float,
        fontsize_pt: float,
        baselineskip_pt: float | None = None,
        font_family: str = "unknown",
        font_name: str = "unknown",
    ) -> "LatexLayout":
        """Create a layout without a local TeX installation."""
        return cls(
            columnwidth_pt=columnwidth_pt,
            textwidth_pt=textwidth_pt,
            fontsize_pt=fontsize_pt,
            baselineskip_pt=baselineskip_pt,
            font_family=font_family,
            font_name=font_name,
        )

    def width_pt(self, width: Literal["column", "text", "page"] | float = "column") -> float:
        """Return an insertion width in TeX points, or a custom width in inches."""
        if width == "column":
            return self.columnwidth_pt
        if width in ("text", "page"):
            return self.textwidth_pt
        if isinstance(width, bool) or not isinstance(width, (int, float)):
            raise ValueError("width must be 'column', 'text', or a number of inches.")
        if not math.isfinite(width) or width <= 0:
            raise ValueError("width in inches must be positive.")
        return float(width) * TEX_PT_PER_INCH

    def width_inches(self, width: Literal["column", "text", "page"] | float = "column") -> float:
        """Return the chosen width in physical inches."""
        return self.width_pt(width) / TEX_PT_PER_INCH


def _latex_preamble(source: str) -> str:
    """Keep source up to the first uncommented begin-document command."""
    # Ignore comment-only lines and inline comments in source.
    uncommented = "\n".join(
        line.split("%", 1)[0] if not re.search(r"(?<!\\)\\%", line) else line
        for line in source.splitlines()
    )
    match = _BEGIN_DOCUMENT.search(uncommented)
    if match is None:
        raise LatexProbeError("Could not find an uncommented begin{document} command.")
    return uncommented[:match.start()]


def _measurement_source(
    preamble: str, *, graphics: Path | None = None, graphics_width: str = "column"
) -> str:
    """Compile a minimal probe using the manuscript's actual preamble."""
    commands = [
        r"\begin{document}",
        r"\makeatletter",
        r"\typeout{CCLAYOUT:COLUMN=\the\columnwidth}",
        r"\typeout{CCLAYOUT:TEXT=\the\textwidth}",
        r"\typeout{CCLAYOUT:FONT=\f@size pt}",
        r"\typeout{CCLAYOUT:BASELINE=\the\baselineskip}",
        r"\typeout{CCLAYOUT:FAMILY=\f@family}",
        r"\typeout{CCLAYOUT:FONTNAME=\fontname\font}",
        r"\makeatother",
    ]
    if graphics is not None:
        # Require graphicx in the probe preamble even if the source omitted it.
        # This probe is a standalone publication-size insertion proof.
        escaped = graphics.resolve().as_posix().replace("\\", "/")
        if graphics_width not in ("column", "text"):
            raise ValueError("graphics_width must be 'column' or 'text'.")
        # Measure the original PDF's physical size without hiding a mismatch
        # behind includegraphics[width=...]. The standalone proof also shows
        # regular document text to allow a side-by-side typography inspection.
        commands.extend([
            r"\newsavebox{\ccfigurebox}",
            r"\sbox{\ccfigurebox}{\includegraphics{" + escaped + "}}",
            r"\typeout{CCLAYOUT:FIGURE=\the\wd\ccfigurebox}",
        ])
        if graphics_width == "text":
            commands.append(r"\onecolumn")
        commands.extend([
            r"\par\noindent Reference manuscript text at the normal body font size.",
            r"\par\medskip\noindent\usebox{\ccfigurebox}",
            r"\par",
        ])
    commands.append(r"\end{document}")
    if graphics is not None:
        preamble = preamble + "\n" + r"\usepackage{graphicx}"
    return preamble + "\n" + "\n".join(commands) + "\n"


def _run_tex(
    document_source: str,
    *,
    source_dir: Path,
    engine: str,
    timeout: int,
    output_pdf: Path | None = None,
) -> str:
    if engine not in _ENGINE:
        raise ValueError(f"engine must be one of {_ENGINE}.")
    exe = shutil.which(engine)
    if exe is None:
        raise LatexProbeError(
            f"{engine} is unavailable. Install a TeX distribution or provide "
            "a LatexLayout.from_dimensions(...) instead."
        )
    if timeout < 1:
        raise ValueError("timeout must be positive.")
    with tempfile.TemporaryDirectory(prefix="cc_latex_") as tmp:
        directory = Path(tmp)
        tex = directory / "awesomefigures_probe.tex"
        tex.write_text(document_source, encoding="utf-8")
        command = [
            exe, "-interaction=nonstopmode", "-halt-on-error",
            "-no-shell-escape", f"-output-directory={directory}",
            str(tex),
        ]
        try:
            completed = subprocess.run(
                command, cwd=source_dir, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                check=False, timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise LatexProbeError(f"LaTeX probe timed out after {timeout} seconds.") from exc
        except OSError as exc:
            raise LatexProbeError(f"Unable to launch {engine}: {exc}") from exc
        log = completed.stdout
        logfile = directory / "awesomefigures_probe.log"
        if logfile.is_file():
            log += "\n" + logfile.read_text(encoding="utf-8", errors="replace")
        if completed.returncode != 0:
            tail = "\n".join(log.splitlines()[-22:])
            raise LatexProbeError(f"LaTeX probe failed. Last log lines:\n{tail}")
        if output_pdf is not None:
            pdf = directory / "awesomefigures_probe.pdf"
            if not pdf.is_file():
                raise LatexProbeError("LaTeX finished without creating a PDF proof.")
            output_pdf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf, output_pdf)
        return log


def _parse_layout_log(log: str) -> LatexLayout:
    values: dict[str, str] = {}
    for key, value in _DIMENSION.findall(log):
        values[key] = value.strip()
    needed = ("COLUMN", "TEXT", "FONT")
    if not all(name in values for name in needed):
        raise LatexProbeError(
            "LaTeX compiled, but did not report its column/text/font dimensions."
        )

    def pt(name: str) -> float:
        match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", values[name])
        if match is None:
            raise LatexProbeError(f"Invalid TeX measurement {name}: {values[name]!r}")
        return float(match.group(0))

    return LatexLayout(
        columnwidth_pt=pt("COLUMN"),
        textwidth_pt=pt("TEXT"),
        fontsize_pt=pt("FONT"),
        baselineskip_pt=pt("BASELINE") if "BASELINE" in values else None,
        font_family=values.get("FAMILY", "unknown"),
        font_name=values.get("FONTNAME", "unknown"),
    )


def inspect_latex(
    tex_file: str | Path,
    *,
    engine: Literal["pdflatex", "xelatex", "lualatex"] = "pdflatex",
    timeout: int = 60,
) -> LatexLayout:
    """Measure an actual trusted LaTeX document by compiling its preamble.

    Reads columnwidth, textwidth, normal font size and font identity at
    begin-document time. Executes LaTeX on a temporary source with shell
    escape disabled, never edits or compiles the manuscript body. TeX source
    may still load local files, packages or run TeX macros: only use trusted
    documents. A TeX installation must be on PATH.
    """
    source = Path(tex_file).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    preamble = _latex_preamble(source.read_text(encoding="utf-8-sig"))
    log = _run_tex(
        _measurement_source(preamble),
        source_dir=source.parent, engine=engine, timeout=timeout,
    )
    return _parse_layout_log(log)



@dataclass(frozen=True)
class LatexFontInfo:
    """Information about font resources accessible through the TeX installation.

    A TFM stores font *metrics*, not the letter outlines. When outline_path
    is None, using PGF inside the manuscript is still the reliable way to
    typeset the figure with the manuscript's exact TeX font.
    """

    family_code: str
    tex_font_name: str
    outline_path: Path | None
    metrics_path: Path | None
    source: str

    @property
    def has_font_file(self) -> bool:
        return self.outline_path is not None


def _kpsewhich(filename: str) -> Path | None:
    """Ask TeX's file database for one resource without scanning directories."""
    executable = shutil.which("kpsewhich")
    if executable is None:
        return None
    try:
        result = subprocess.run(
            [executable, filename], capture_output=True, text=True,
            check=False, timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    # Usually one absolute filename, but use only the first non-empty line.
    path = Path(result.stdout.strip().splitlines()[0])
    return path if path.is_file() else None


def find_latex_font(
    tex_file: str | Path,
    *,
    engine: Literal["pdflatex", "xelatex", "lualatex"] = "pdflatex",
    timeout: int = 60,
) -> LatexFontInfo:
    """Inspect the TeX font and locate available files without downloads.

    Reports the font identifier from the document's normal body text.
    For Type 1 / traditional LaTeX fonts, kpsewhich often finds a TFM
    metrics file, even when a matching outline file cannot be identified
    automatically. For XeLaTeX/LuaLaTeX it may find an OTF/TTF font file.
    Returning a metrics path is not proof that Matplotlib can use the font.
    """
    layout = inspect_latex(tex_file, engine=engine, timeout=timeout)
    font_name = layout.font_name.strip()
    # XeTeX/LuaTeX can print [path/font.otf]:mode=... as \fontname.
    outline: Path | None = None
    bracket = re.match(r"^\[([^\]]+\.(?:otf|ttf|ttc))\]", font_name, re.IGNORECASE)
    if bracket:
        candidate = Path(bracket.group(1))
        if candidate.is_file():
            outline = candidate.resolve()
        else:
            outline = _kpsewhich(candidate.name)
    tex_name = font_name.split()[0] if font_name else "unknown"
    # The simplest form is "cmr10 at 10.0pt" or "pplr7t at 10.0pt".
    clean_name = re.sub(r"[^A-Za-z0-9_.-]", "", tex_name)
    metrics: Path | None = None
    if clean_name:
        if outline is None:
            for ext in ("otf", "ttf", "ttc", "pfb"):
                outline = _kpsewhich(f"{clean_name}.{ext}")
                if outline is not None:
                    break
        metrics = _kpsewhich(f"{clean_name}.tfm")
    source = (
        "font outlines found in TeX" if outline else
        "TeX metrics found; outline file not identified" if metrics else
        "font identifier available; TeX file location unresolved"
    )
    return LatexFontInfo(
        family_code=layout.font_family,
        tex_font_name=layout.font_name,
        outline_path=outline, metrics_path=metrics, source=source,
    )


@dataclass(frozen=True)
class FigureAudit:
    """Physical measurements and warnings at the intended LaTeX insertion size."""

    expected_width_pt: float
    output_width_pt: float
    body_font_pt: float
    smallest_text_pt: float | None
    smallest_line_pt: float | None
    warnings: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.warnings


def audit_figure(
    fig: mpl.figure.Figure,
    layout: LatexLayout,
    *,
    width: Literal["column", "text", "page"] | float = "column",
    minimum_text_pt: float = 7.0,
    minimum_line_pt: float = 0.4,
    width_tolerance_pt: float = 0.5,
) -> FigureAudit:
    """Check effective text/line sizes and approximate clipped labels.

    Matplotlib text/line sizes are PDF points; physical sizes are converted
    to the requested LaTeX insertion width. This cannot certify aesthetic
    quality or detect every collision/overlap.
    """
    if minimum_text_pt <= 0 or minimum_line_pt <= 0 or width_tolerance_pt < 0:
        raise ValueError("Audit thresholds must be positive (tolerance nonnegative).")
    expected = layout.width_pt(width)
    actual = fig.get_size_inches()[0] * TEX_PT_PER_INCH
    scale = expected / actual
    issues: list[str] = []
    if abs(actual - expected) > width_tolerance_pt:
        issues.append(f"Figure width {actual:.2f} pt differs from target {expected:.2f} pt.")

    sizes: list[float] = []
    for text in fig.findobj(match=Text):
        if text.get_visible() and text.get_text().strip():
            sizes.append(text.get_fontsize() * scale)
    smallest_text = min(sizes) if sizes else None
    if smallest_text is not None and smallest_text < minimum_text_pt:
        issues.append(
            f"Smallest text is {smallest_text:.2f} pt at insertion; "
            f"minimum requested is {minimum_text_pt:.2f} pt."
        )

    lines = [
        line.get_linewidth() * scale
        for ax in fig.axes for line in ax.lines if line.get_visible()
    ]
    smallest_line = min(lines) if lines else None
    if smallest_line is not None and smallest_line < minimum_line_pt:
        issues.append(
            f"Smallest plotted line is {smallest_line:.2f} pt at insertion; "
            f"minimum requested is {minimum_line_pt:.2f} pt."
        )

    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bbox = fig.bbox
        margin = 3.0
        # Do not inspect the complete Artist tree for clipping: Matplotlib
        # keeps hidden/internal tick Text objects at off-canvas coordinates.
        # Restrict the check to explicitly displayed titles, axis labels,
        # annotations and legends.
        visible_labels = []
        for ax in fig.axes:
            visible_labels.extend((ax.title, ax.xaxis.label, ax.yaxis.label))
            visible_labels.extend(ax.texts)
            legend = ax.get_legend()
            if legend is not None and legend.get_visible():
                visible_labels.extend(legend.get_texts())
        if getattr(fig, "_suptitle", None) is not None:
            visible_labels.append(fig._suptitle)
        for text in visible_labels:
            if not text.get_visible() or not text.get_text().strip():
                continue
            bounds = text.get_window_extent(renderer=renderer)
            if (bounds.x0 < bbox.x0 - margin or bounds.y0 < bbox.y0 - margin
                    or bounds.x1 > bbox.x1 + margin or bounds.y1 > bbox.y1 + margin):
                issues.append("A text label extends beyond the figure canvas.")
                break
    except (AttributeError, RuntimeError, ValueError):
        # Some interactive/vector canvases do not expose pixel renderers.
        pass
    return FigureAudit(
        expected_width_pt=expected, output_width_pt=actual,
        body_font_pt=layout.fontsize_pt,
        smallest_text_pt=smallest_text, smallest_line_pt=smallest_line,
        warnings=tuple(issues),
    )


@dataclass(frozen=True)
class FitResult:
    """Outcome of a bounded layout-fitting attempt."""

    iterations: int
    audit: FigureAudit
    figure_width_inches: float
    figure_height_inches: float

    @property
    def passed(self) -> bool:
        return self.audit.passed


def fit_figure_to_latex(
    fig: mpl.figure.Figure,
    layout: LatexLayout,
    *,
    width: Literal["column", "text", "page"] | float = "column",
    height_ratio: float | None = None,
    reference_fontsize_pt: float | None = None,
    minimum_text_pt: float = 7.0,
    max_iterations: int = 3,
) -> FitResult:
    """Resize an existing figure and its texts to the LaTeX insertion size.

    Text hierarchy is preserved relative to reference_fontsize_pt, defaulting
    to the active Matplotlib font size on first call. Tight layout and small
    height increases attempt to resolve clipping; overlapping data/legends
    still require manual design decisions. Repeated calls do not compound
    text scaling: the original text sizes are cached on the figure.
    """
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1.")
    if height_ratio is not None and (not math.isfinite(height_ratio) or height_ratio <= 0):
        raise ValueError("height_ratio must be positive.")
    size = tuple(fig.get_size_inches())
    new_width = layout.width_inches(width)
    ratio = height_ratio if height_ratio is not None else size[1] / size[0]
    fig.set_size_inches(new_width, new_width * ratio, forward=True)
    baseline = getattr(fig, "_awesomefigures_text_baseline", None)
    if baseline is None:
        reference = reference_fontsize_pt or float(mpl.rcParams["font.size"])
        if not math.isfinite(reference) or reference <= 0:
            raise ValueError("reference_fontsize_pt must be positive.")
        baseline = [(text, text.get_fontsize() / reference) for text in fig.findobj(match=Text)]
        fig._awesomefigures_text_baseline = baseline
    for text, relative_size in baseline:
        text.set_fontsize(layout.fontsize_pt * relative_size)

    audit = None
    for attempt in range(1, max_iterations + 1):
        if not fig.get_constrained_layout():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                try:
                    fig.tight_layout(pad=0.55)
                except (ValueError, RuntimeError):
                    pass
        audit = audit_figure(
            fig, layout, width=width, minimum_text_pt=minimum_text_pt
        )
        if audit.passed:
            break
        if not any("extends beyond" in issue for issue in audit.warnings):
            break
        fig.set_size_inches(
            new_width, fig.get_size_inches()[1] * 1.10, forward=True
        )
    assert audit is not None
    return FitResult(
        iterations=attempt, audit=audit,
        figure_width_inches=fig.get_size_inches()[0],
        figure_height_inches=fig.get_size_inches()[1],
    )


@dataclass
class PublicationStyle:
    """A measured document-aware plotting configuration.

    Produced by latex_style as a context-managed object. Use subplots(),
    fit(), audit() and savefig(). Its default PDF save preserves physical
    figure dimensions; bbox_inches='tight' would otherwise change the width.
    """

    layout: LatexLayout
    width: Literal["column", "text", "page"] | float = "column"
    height_ratio: float = 0.65
    minimum_text_pt: float = 7.0
    tex_engine: str = "pdflatex"

    def subplots(self, *, height_ratio: float | None = None, **kwargs):
        """Create a Matplotlib figure already sized to its LaTeX slot."""
        ratio = self.height_ratio if height_ratio is None else height_ratio
        if not math.isfinite(ratio) or ratio <= 0:
            raise ValueError("height_ratio must be positive.")
        kwargs.setdefault("figsize", (self.layout.width_inches(self.width),
                                     self.layout.width_inches(self.width) * ratio))
        kwargs.setdefault("layout", "constrained")
        return plt.subplots(**kwargs)

    def audit(self, fig: mpl.figure.Figure) -> FigureAudit:
        """Check physical font and graphic dimensions before export."""
        return audit_figure(
            fig, self.layout, width=self.width, minimum_text_pt=self.minimum_text_pt
        )

    def fit(self, fig: mpl.figure.Figure, **kwargs) -> FitResult:
        """Resize an existing figure, preserving relative font hierarchy."""
        return fit_figure_to_latex(
            fig, self.layout, width=self.width,
            minimum_text_pt=self.minimum_text_pt, **kwargs,
        )


    def savefig_pgf(
        self, fig: mpl.figure.Figure, filename: str | Path, *,
        dpi: int = 600, **kwargs,
    ) -> Path:
        """Save a vector PGF picture to be typeset by the manuscript's LaTeX.

        This does not require the manuscript font to be installed in Windows.
        Include as a PGF input in the original LaTeX manuscript.
        For exact font matching, PGF must be typeset in that document; the
        standalone preview in Matplotlib may use approximate font metrics.
        """
        target = Path(filename).with_suffix(".pgf")
        target.parent.mkdir(parents=True, exist_ok=True)
        options = {"bbox_inches": None, "pad_inches": 0, "dpi": dpi, **kwargs}
        with mpl.rc_context({
            "pgf.texsystem": self.tex_engine,
            "pgf.rcfonts": False,
            # Explicit bbox_inches=None is treated by Matplotlib as
            # "use savefig.bbox from rcParams". Heri defaults to "tight",
            # which silently shrinks the exported physical width.
            # Override the rcParam itself so the TeX column size is exact.
            "savefig.bbox": None,
            "savefig.pad_inches": 0,
        }):
            fig.savefig(target, format="pgf", **options)
        return target

    def savefig(
        self, fig: mpl.figure.Figure, filename: str | Path, *,
        audit: bool = True, dpi: int = 600, **kwargs,
    ) -> Path:
        """Export exact physical dimensions; PGF allows native LaTeX fonts.

        For PDF, SVG, PNG: dimensions stay exact because tight cropping is
        disabled. PGF can be included with LaTeX input{...}, using the
        manuscript's own fonts when processed by TeX.
        """
        if audit:
            report = self.audit(fig)
            if not report.passed:
                warnings.warn(
                    "Publication figure audit: " + " ".join(report.warnings),
                    UserWarning, stacklevel=2,
                )
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".pdf")
        path.parent.mkdir(parents=True, exist_ok=True)
        opts = {"bbox_inches": None, "pad_inches": 0, "dpi": dpi, **kwargs}
        if path.suffix.lower() == ".pgf":
            self.savefig_pgf(
                fig, path, **{key: value for key, value in opts.items() if key != "dpi"},
                dpi=dpi,
            )
        else:
            # The general Heri preset deliberately uses tight cropping.
            # Publication mode must override that *rcParam*, not merely
            # pass bbox_inches=None, since Matplotlib treats None as a
            # request to fall back to rcParams["savefig.bbox"].
            with mpl.rc_context({"savefig.bbox": None, "savefig.pad_inches": 0}):
                save_figure(fig, path, **opts)
        return path


@contextmanager
def latex_style(
    tex_file: str | Path | LatexLayout,
    *,
    width: Literal["column", "text", "page"] | float = "column",
    engine: Literal["pdflatex", "xelatex", "lualatex"] = "pdflatex",
    font: str = "auto",
    height_ratio: float = 0.65,
    minimum_text_pt: float = 7.0,
    rasterize: bool = True,
    style: Literal["heri", "elegante"] = "heri",
    palette: str = "print-safe",
    axis_label_scale: float = 1.0,
    axis_label_weight: str = "normal",
    timeout: int = 60,
) -> Iterator[PublicationStyle]:
    """Context-manage publication-sized figures using LaTeX measurements.

    Font sizes match the body text in *points*: axis labels default to body
    size and normal weight; ticks/legends 80% and panel titles 100%.
    Customize axis_label_scale and axis_label_weight when needed.
    font='auto' infers serif/sans
    from the LaTeX family code, but does NOT guarantee identical glyphs.
    For exact document font rendering, export a PGF and input it in LaTeX.
    """
    if not math.isfinite(axis_label_scale) or axis_label_scale <= 0:
        raise ValueError("axis_label_scale must be positive and finite.")
    if not isinstance(axis_label_weight, str) or not axis_label_weight.strip():
        raise ValueError("axis_label_weight must be a nonempty font weight.")
    layout = (
        tex_file if isinstance(tex_file, LatexLayout)
        else inspect_latex(tex_file, engine=engine, timeout=timeout)
    )
    if font == "auto":
        code = layout.font_family.lower()
        family = "sans-serif" if code.startswith(("phv", "lmss", "cmss", "qhv")) else "serif"
    else:
        family = font
    with style_context(style, palette=palette, font=family, use_tex=False, rasterize=rasterize):
        mpl.rcParams.update({
            "font.size": layout.fontsize_pt,
            "font.weight": "normal",
            "axes.labelsize": axis_label_scale * layout.fontsize_pt,
            "axes.labelweight": axis_label_weight,
            "axes.titlesize": layout.fontsize_pt,
            "xtick.labelsize": 0.8 * layout.fontsize_pt,
            "ytick.labelsize": 0.8 * layout.fontsize_pt,
            "legend.fontsize": 0.8 * layout.fontsize_pt,
            "figure.titlesize": layout.fontsize_pt,
            "figure.figsize": (layout.width_inches(width),
                               layout.width_inches(width) * height_ratio),
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        })
        yield PublicationStyle(
            layout=layout, width=width,
            height_ratio=height_ratio, minimum_text_pt=minimum_text_pt,
            tex_engine=engine,
        )


def verify_latex_placement(
    tex_file: str | Path,
    figure_pdf: str | Path,
    *,
    proof_pdf: str | Path | None = None,
    width: Literal["column", "text"] = "column",
    tolerance_pt: float = 0.75,
    engine: Literal["pdflatex", "xelatex", "lualatex"] = "pdflatex",
    timeout: int = 60,
) -> LatexLayout:
    """Compile a one-page proof with unscaled PDF at the intended TeX width.

    Verifies the insertion width in TeX points rather than silently resizing
    the PDF. The proof includes reference manuscript body text for comparison.
    For full-width two-column figures, select width='text'.
    This does not analyze float placement in the full manuscript.
    """
    source = Path(tex_file).expanduser().resolve()
    figure = Path(figure_pdf).expanduser().resolve()
    if figure.suffix.lower() != ".pdf":
        raise ValueError("verify_latex_placement currently requires a PDF figure.")
    if not source.is_file() or not figure.is_file():
        raise FileNotFoundError("Both TeX source and exported PDF must exist.")
    preamble = _latex_preamble(source.read_text(encoding="utf-8-sig"))
    log = _run_tex(
        _measurement_source(preamble, graphics=figure, graphics_width=width),
        source_dir=source.parent, engine=engine, timeout=timeout,
        output_pdf=Path(proof_pdf).expanduser().resolve() if proof_pdf else None,
    )
    layout = _parse_layout_log(log)
    if width not in ("column", "text"):
        raise ValueError("width must be 'column' or 'text'.")
    if not math.isfinite(tolerance_pt) or tolerance_pt < 0:
        raise ValueError("tolerance_pt must be non-negative and finite.")
    found = re.search(r"CCLAYOUT:FIGURE=([0-9.]+)pt", log)
    if found is None:
        raise LatexProbeError("The LaTeX proof did not measure the inserted PDF width.")
    observed = float(found.group(1))
    expected = layout.width_pt(width)
    if abs(observed - expected) > tolerance_pt:
        raise LatexProbeError(
            f"Figure has width {observed:.2f} TeX pt, "
            f"but {width} width is {expected:.2f} TeX pt. "
            "Export at the target physical width instead of scaling on insertion."
        )
    return layout
