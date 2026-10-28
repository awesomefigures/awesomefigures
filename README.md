# AwesomeFigures

## Automatic LaTeX publication from an existing figure

Configure a trusted manuscript once; your already-computed figures inherit
its measured physical dimensions and body typography. PDF export compiles PGF
through the manuscript's real TeX preamble and inspects embedded PDF fonts.
PNG/SVG and `exact=False` PDFs are explicitly marked as previews.

```python
import awesomefigures as af

with af.paper("paper/main.tex", style="elegante",
                    palette="okabe-ito", strict=True) as pub:
    fig, ax = pub.subplots()
    ax.plot(saved_x, saved_y, label="Observed trend")
    pub.savefig(fig, "paper/figures/trend.pdf", width="column")
    pub.report("paper/figures/manifest.json")
```

Install PDF auditing separately with `python -m pip install -e ".[publication]"`.
The core plotting installation still has no TeX or PDF-auditing dependencies.
See the [automatic publication guide](docs/source/automatic_publication.rst)
and [deterministic batch example](examples/automatic_publication/).
This API never reruns statistical experiments.


**Distribution:** `awesomefigures` · **Python import:** `import awesomefigures as af`

```python
import awesomefigures as af

af.set_style("elegante", palette="okabe-ito", use_tex=False)
palette = af.color_palette("tol-bright")
```

### Migration from contrastcolors

The name change is a **breaking import-path change**. Replace
`import contrastcolors as cc` with `import awesomefigures as af`
and update `cc.` calls to `af.`. The former import package is not
installed by the new distribution. Existing figures and scientific
algorithms otherwise retain their behavior.

For an existing development environment:

```bash
python -m pip uninstall -y contrastcolors
python -m pip install -e .
python -c "import awesomefigures as af; print(af.__version__)"
```

For another library or project before a PyPI release:

```bash
python -m pip install "awesomefigures @ git+https://github.com/heri-espino/Colors.git@main"
```

For reproducible use, replace `main` with a pinned release tag or immutable
commit. The GitHub repository name and Pages
URLs currently remain `Colors`; Python package and distribution names
are `awesomefigures`. Uploading to PyPI is a separate release step.


**Implementation catalogue:** [Complete feature inventory](FEATURES.md)
([Sphinx reference](docs/source/features.rst)) lists all 70 current public
exports and the separate browser, notebook, TeX and automation tools.
A CI test detects when a new public API symbol has not been documented.


`awesomefigures` builds scientific plotting palettes whose **adjacent WCAG
contrast ratios are controlled by construction** while hue can change
independently. It is designed as a small layer on top of Matplotlib, in the
same general role that palette helpers play in higher-level plotting libraries.

For relative luminance levels (Y_k) and a requested adjacent contrast ratio
(r),

[
rac{Y_k+0.05}{Y_{k+1}+0.05}=r,
qquad
Y_k=rac{Y_0+0.05}{r^k}-0.05.
]

The library then solves for an sRGB-representable OKLCH color at each requested
luminance and hue.

## Well-known built-in colour palettes

Scientific reference palettes are available by name without registration.
Their original HEX coordinates are preserved; they are **not** replaced by
the luminance-constrained OKLCH generator.

```python
import awesomefigures as af

af.available_named_palettes()
af.color_palette("okabe-ito", as_hex=True)
af.plot_scheme("tol-high-contrast")
af.set_style("elegante", palette="tol-bright", use_tex=False)

# Sequential and diverging colormaps for ordered values:
image = ax.imshow(values, cmap=af.named_colormap("cividis"))
```

Seven exact categorical sets: Okabe–Ito, Paul Tol Bright, High Contrast and
Muted, Tableau 10, ColorBrewer Set2 and Dark2. The original Matplotlib
colormaps viridis, cividis, plasma, magma, inferno and RdBu are also named
built-ins. See the [visual palette atlas](docs/source/named_palettes.rst) and
[Palette Studio](https://heri-espino.github.io/Colors/studio.html).
These schemes are useful starting points, not certifications of universal
accessibility.

## Matplotlib styles

The package provides three selectable styles: `heri`, `elegante`,
and `default`. The new **elegante** style aligns both axis endpoints
with readable ticks and keeps curve markers clear of the frame while
leaving the curve and its data intact.

```python
import numpy as np
import matplotlib.pyplot as plt
import awesomefigures as af

af.set_style("elegante", font="DejaVu Sans", use_tex=False)
x = np.linspace(0, 100, 301)
fig, ax = plt.subplots()
ax.plot(x, np.sin(x / 17), marker="o")
ax.set(xlabel="Time", ylabel="Response")
fig.savefig("elegant.pdf")
```

This finishes axes automatically at rendering. Fine-tune tick counts,
padding, zero inclusion and the minimum marker distance using
`af.apply_elegant_axes(ax, target_xticks=6, marker_inset_pt=4)`.
See the rendered [Styles guide](https://heri-espino.github.io/Colors/style.html)
for comparisons and technical limitations.

## Conda environment (Windows, macOS, and Linux)

The repository includes `environment.yml` for the **complete
AwesomeFigures development environment**. It uses `conda-forge` for
Python 3.12, NumPy, Matplotlib and Colorspacious, then installs
`awesomefigures` in editable mode with its test, documentation and
notebook extras from `pyproject.toml`.

From the **repository root** (important for the relative editable install):

```bash
git clone https://github.com/heri-espino/Colors.git
cd Colors
conda env create -f environment.yml
conda activate awesomefigures
python -m pip check
python -c "import awesomefigures as af; print(af.__version__)"
pytest
```

If the environment already exists, update it instead of creating a second one:

```bash
conda env update -n awesomefigures -f environment.yml --prune
conda activate awesomefigures
```

The environment also contains Sphinx and JupyterLab:

```bash
sphinx-build -W -b html docs/source docs/_build/html
jupyter lab
```

**Using AwesomeFigures in a different Conda project:** activate that project's
environment and install this checkout with
`python -m pip install -e /path/to/Colors`. Alternatively, install a
pinned Git commit with
`python -m pip install "awesomefigures @ git+https://github.com/heri-espino/Colors.git@<commit-sha>"`.
This does not require changing the other project's Conda environment name.
When distributing another library, declare `awesomefigures` as a dependency
after it has been published to PyPI.

The Conda YAML targets local development, not a cross-platform lockfile.
It does **not** publish anything to PyPI or run notebook generation automatically.

A manually triggered **Conda environment smoke test** workflow is available
in GitHub Actions when you want to validate an actual fresh Conda installation
without running heavyweight dependency-solving on every push.

## Windows: run the entire project with Conda

Install [Miniforge](https://github.com/conda-forge/miniforge) or Miniconda,
clone the repository, and open an initialized Conda PowerShell:

~~~powershell
git clone https://github.com/heri-espino/Colors.git
cd Colors
Set-ExecutionPolicy -Scope Process Bypass
.\tools\setup_and_run.ps1
~~~

The script creates or updates a Python 3.12 Conda environment, installs all
dependencies and the editable package, checks dependencies, runs pytest,
executes **every demo notebook**, saves generated plots inside the .ipynb
files, verifies the outputs, and builds the Sphinx website (strict warnings).

Optional flags:

~~~powershell
# Run tests and rebuild Sphinx without re-executing notebooks
.\tools\setup_and_run.ps1 -SkipNotebooks

# Run tests and serve the documentation at http://localhost:8765/
.\tools\setup_and_run.ps1 -SkipNotebooks -Serve

# Explicitly commit saved notebook results
.\tools\setup_and_run.ps1 -CommitOutputs

# Explicitly commit and push results to GitHub
.\tools\setup_and_run.ps1 -CommitOutputs -Push
~~~

Without those flags, **no changes are pushed or committed automatically**.
The generated documentation is in
`docs/_build/html/index.html`, and the notebook outputs are saved in
`docs/source/notebooks/*.ipynb`.

Launch JupyterLab with `conda run -n awesomefigures jupyter lab`.

To publish the Sphinx site, go to GitHub **Settings > Pages**, select
**GitHub Actions** as the source, and run the manual `pages` workflow.
A default Jekyll Pages deployment does not build Sphinx.

## macOS: complete LaTeX publication showcase

There is a reproducible, two-column technical presentation explaining
how WCAG luminance and OKLCH hue/chroma are selected, the palette matrix,
interactive Studio, real LaTeX fonts, physical sizes, vector vs hybrid
PDF/PGF, alpha compositing and six-way grayscale/CVD dashboards.

Requires MacTeX or compatible TeX Live and Conda or Python 3.10+.

~~~bash
git pull
./examples/latex_publication/run_macos.sh --open
~~~

The script generates the technical paper, a ContrastGrid palette illustration,
two true-vector accessibility dashboard PDFs/PGFs and a font/layout audit.
It copies the final PDF, palette figure, vector dashboard PDFs and website
PNG previews to Sphinx static assets.

After reviewing the results, the following command explicitly commits
and pushes the published demonstration PDF/PNG assets:

~~~bash
./examples/latex_publication/run_macos.sh --push
~~~

See examples/latex_publication/README.md for the complete workflow.

## Install locally

```bash
python -m pip install -e .
```

For development:

```bash
python -m pip install -e ".[dev,docs]"
pytest
```

## LaTeX publication figures: automatic document size

Match the real physical widths and nominal body font size of a trusted
LaTeX document. No PNG screenshots or pixel-based trial and error are needed.

~~~python
import awesomefigures as af

with af.latex_style("paper/main.tex", width="column") as pub:
    fig, ax = pub.subplots(height_ratio=0.65)
    ax.plot([0, 1, 2], [1, 3, 2])
    ax.set(xlabel="Time", ylabel="Response")
    print(pub.audit(fig).warnings)
    pub.savefig(fig, "paper/figures/result.pdf")

af.verify_latex_placement(
    "paper/main.tex", "paper/figures/result.pdf",
    proof_pdf="paper/figures/result_proof.pdf",
)
~~~

Include the saved PDF **without resizing** in LaTeX (plain includegraphics).
Set width="text" to span both columns. To resize an existing figure, call
af.fit_figure_to_latex(fig, af.inspect_latex("paper/main.tex")).

A suitable TeX engine must be on PATH for inspection or proof compilation.
If unavailable, pass LatexLayout.from_dimensions(columnwidth_pt=...,
textwidth_pt=..., fontsize_pt=...) instead.

Font sizes and widths are matched in physical units; identical font *glyphs*
require a configured TeX font or PGF export. The bounded fit and audit
cannot automatically resolve every legend or annotation overlap. The TeX
probe uses a temporary document and does not modify your paper's source,
but it still executes trusted LaTeX preamble macros with shell escape disabled.

To reuse the exact TeX fonts without downloading them again, inspect the
available font information and export a PGF for the manuscript itself to typeset:

~~~python
font = af.find_latex_font("paper/main.tex")
print(font.tex_font_name, font.metrics_path, font.outline_path)
with af.latex_style("paper/main.tex") as pub:
    fig, ax = pub.subplots()
    ax.plot([0, 1], [1, 2])
    pub.savefig(fig, "paper/figures/figure.pgf")
~~~

Include the PGF in the manuscript with the LaTeX command
`\\input{figures/figure.pgf}`. A TFM is font metrics, not an outline
font: no need to manually install it into Matplotlib.

See [publication guide](docs/source/publication.rst).

## Figure accessibility

The Heri Matplotlib style now defaults to different line markers and
linestyles, and repeated scatter groups get distinct markers. Use the
six-view panel to inspect an entire figure in grayscale, print stress,
deuteranopia, protanopia and tritanopia, alongside the original:

    af.show_accessibility_panel(fig)
    af.save_accessibility_panel(fig, "accessible.png")

See the accessibility documentation. Simulations are approximations.

## Interactive Palette & Plot Studio

The browser-based Studio works without a backend and offers live previews for
line plots, time series, histograms, box/violin/ridge plots, scatter,
categorical heatmaps and grouped bars.

It includes grayscale/print-stress views, hue order and identifier editing,
browser-local save/load, portable JSON import/export, and downloadable named
Python palette presets.

Open the Studio in the Sphinx site or directly at
[docs/source/_static/studio.html](docs/source/_static/studio.html).

**Named palette example:**

~~~python
import awesomefigures as af

af.register_palette(
    "paper_palette",
    hues=[55, 20, 145, 210, 290],
    ratio=1.22,
    start_luminance=0.72,
    markers=["o", "s", "^", "D", "X"],
    linestyles=["-", "--", ":", "-.", (0, (5, 2))],
)

colors = af.color_palette("paper_palette")
scheme = af.plot_scheme("paper_palette")
~~~

A Python preset registration lasts for the current process. Keep the
registration in a project module and import it to reuse it.

## Documentation

The Sphinx site now documents the complete library:

- [full implementation inventory](FEATURES.md), automatically checked
  against every public Python export;
- quickstart and installation;
- palette and ContrastGrid workflows;
- alpha compositing and apparent-color compensation;
- Heri publication style, selectable fonts, hybrid PDF export, and colormaps;
- WCAG, sRGB, OKLab/OKLCH, and gamut behavior;
- guarantees and limitations;
- end-to-end Matplotlib examples;
- interactive palette picker;
- complete public API and advanced low-level helpers.

Build it locally with:

~~~bash
python -m pip install -e ".[docs]"
sphinx-build -W -b html docs/source docs/_build/html
~~~

Open docs/_build/html/index.html in a browser.

## Quick start

For the ordinary case, supply one hue per desired color:

```python
import awesomefigures as af

colors = af.color_palette(
    hues=[55, 20, 145, 210, 290],
    ratio=1.4,
)

# Matplotlib-ready RGBA tuples
for y, color in zip(series, colors):
    plt.plot(x, y, color=color)
```

Use `contrast_palette` when you want diagnostics and metadata:

```python
palette = af.contrast_palette(
    hues=[55, 20, 145, 210, 290],
    ratio=1.4,
)

print(palette.hex)
print(palette.adjacent_contrast)
print(palette.minimum_alpha(background="white"))
```

## Publication style

The package includes the publication style used by the WTI APO paper:

~~~python
import matplotlib.pyplot as plt
import awesomefigures as af

af.set_style("heri", font="Arial")

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$f(x)$")

af.save_figure(fig, "figure.pdf")
~~~

The Heri preset matches that repository's publication figures: compact
white-grid axes, 8--9 pt typography, top/right spines removed, 600-dpi hybrid
PDF export, Paul Tol categorical colors, and the iridescent continuous map
available as af.HERI_CMAP.

The visual style and the font are independent:

~~~python
af.set_style("heri")                   # Utopia when available, STIX fallback
af.set_style("heri", font="Arial")
af.set_style("heri", font="Helvetica")
af.set_style("heri", font="STIX")
af.set_style("heri", font="DejaVu Sans")
~~~

For arbitrary fonts, use_tex="auto" renders text directly through Matplotlib so
the requested family is respected. The Utopia preset can use the Wiley-like
LaTeX stack when it is installed:

~~~python
af.set_style("heri", font="utopia", use_tex=True)
~~~

By default, ordinary lines and typography remain vector, while dense artists
such as scatter plots, heatmaps, filled contours, hexbins and 3D surfaces are
rasterized inside the PDF. This can be disabled:

~~~python
af.set_style("heri", font="Arial", rasterize=False)
~~~

For local use without changing global settings permanently:

~~~python
with af.style_context("heri", font="Arial"):
    ...
~~~

## Exploring hue combinations

The lower-level object is an (i 	imes j) hue-luminance grid:

[
C_{kell}=C(Y_k,h_ell).
]

Every color in row (k) has the same relative luminance (Y_k), while each
column corresponds to a candidate hue. Therefore any selection of one hue per
row preserves the prescribed adjacent contrast ratio.

```python
grid = af.contrast_grid(
    levels=5,
    hues=[55, 20, 145, 210, 290],
    ratio=1.4,
)

palette = grid.select([0, 1, 2, 3, 4])
grid.plot()
```

The Sphinx documentation includes an interactive picker inspired by the
workflow of tools such as Evil Martians Harmonizer. The picker lets you change
levels, contrast ratio, hues, chroma, alpha and background, click one candidate
per row, and copy the resulting `awesomefigures` Python call.

## Alpha compensation

With `preserve_apparent=True`, the library solves

[
T=alpha S+(1-alpha)B
]

for the source color (S), where (T) is the desired apparent color and (B)
is the background:

[
S=rac{T-(1-alpha)B}{alpha}.
]

If the inverse lies outside the sRGB gamut, exact reconstruction is physically
impossible at that alpha/background combination. The result reports
`feasible=False` rather than claiming the original color was preserved.

## Current features

- constant adjacent WCAG contrast ratios;
- independently selectable hue at every luminance level;
- OKLCH hue/chroma construction with automatic sRGB gamut reduction;
- alpha compensation against a known background;
- perceptual OKLab optimization when exact alpha compensation is outside sRGB;
- minimum-alpha feasibility calculation;
- Matplotlib-ready RGBA output and `ListedColormap` export;
- `color_palette`, `contrast_palette`, `plot_scheme`, `show_palette`, and
  `ContrastGrid` APIs;
- `set_style("heri")`, `style_context`, and hybrid-PDF `save_figure` helpers;
- interactive Sphinx palette picker;
- interactive Palette & Plot Studio for hue order, markers, linestyles, grayscale/print preview, alpha, style, and code export;
- tests and Sphinx builds in GitHub Actions.

## Planned

- optional APCA contrast model;
- color-vision-deficiency simulation/diagnostics;
- richer Matplotlib integration and named reusable palettes;
- package publishing after the API stabilizes.
