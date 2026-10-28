Capability inventory
====================

**Canonical feature catalogue for the implemented version of** ``awesomefigures``.
This page is based on the actual public names exported by
``src/awesomefigures/__init__.py``. A regression test checks that every
public symbol appears here: when the Python API grows, the inventory must be
updated with it.

The package is a layer on top of Matplotlib, not a replacement plotting engine.
Most chart families come from Matplotlib; ``awesomefigures`` supplies
palettes, identifiers, publication styles, diagnostics, or wrappers.

.. contents:: Jump to a capability
   :local:
   :depth: 1

Famous built-in palettes and Matplotlib colormaps
-------------------------------------------------

Built-in categorical palettes retain their original RGB codes and are ready to
use without registration: **Okabe–Ito (alias colorblind/Wong)**, Paul Tol Bright,
High Contrast and Muted, Tableau 10, ColorBrewer Set2 and Dark2. Named sequential
and diverging maps are supplied through Matplotlib: viridis, cividis, plasma,
magma, inferno and RdBu. Exact RGB palettes are kept separate from the
WCAG-constructed hue/luminance grid. They work through ``color_palette``,
``plot_scheme``, ``scatter_scheme``, and the ``palette`` argument of
``set_style``/``style_context``. The :doc:`named_palettes` gallery documents
provenance, correct use and examples.

**Public exports:** ``NamedPalette``, ``available_named_palettes``,
``get_named_palette``, ``named_palette``, ``named_colormap``.

Palette construction and contrast
---------------------------------

Specify hues, an optional adjacent WCAG contrast ratio, a starting relative luminance, and chroma. The implementation solves representable sRGB colours by adjusting OKLCH lightness and, when necessary, chroma. A ContrastGrid exposes the rows of equal luminance and columns of hue; Palette objects provide colors, rendered RGBA, contrasts and Matplotlib colormaps.

**Public exports:** ``contrast_palette``, ``color_palette``, ``show_palette``, ``contrast_grid``, ``color_for_luminance``, ``luminance_ladder``, ``luminance_contrast``, ``print_safe_luminances``, ``Palette``, ``ContrastGrid``, ``ColorCell``, ``RenderedColor``.

Line and scatter encoding
-------------------------

Create color/marker/line-style dictionaries for Matplotlib. The no-override default spreads relative luminances adaptively for a small number of series; explicit constraints and named presets take precedence.

**Public exports:** ``plot_scheme``, ``scatter_scheme``, ``DEFAULT_MARKERS``, ``DEFAULT_LINESTYLES``.

Preset registry
---------------

Give a design a name, including its hue order, optional alpha-related contrast settings, markers and line styles. Registrations exist in the current Python process; load a preset module at startup to reuse it.

**Public exports:** ``PalettePreset``, ``register_palette``, ``get_palette``, ``available_palettes``.

Alpha and background compositing
--------------------------------

Check how an RGBA source color appears over a chosen background; find a feasible opacity, and precompensate foreground values where an exact match is possible. Transparent marks can otherwise lose apparent color contrast.

**Public exports:** ``AlphaCompensation``, ``compensate_alpha``, ``composite``, ``minimum_alpha``.

Color conversions and diagnostics
---------------------------------

Convert Matplotlib/RGB colors, calculate relative luminance and WCAG contrast of opaque colors, or compare colors in OKLab. Color contrast alone is not a certification of distinguishability.

**Public exports:** ``to_rgb``, ``to_hex``, ``relative_luminance``, ``contrast_ratio``, ``srgb_to_oklab``, ``delta_e_ok``.

Automated journal publication and batch reports
-----------------------------------------------

Document-aware publication extends existing LaTeX inspection and PGF APIs.
One context caches manuscript measurements and exports PDF (TeX-exact by
default), SVG or PNG previews with physical-width, embedded-font and text
audits. Every batch gets a JSON and Markdown manifest. The API accepts
already-computed figures and never runs statistical experiments. The
:doc:`automatic_publication` guide explains limitations and installation.

**Public exports:** ``Publication``, ``paper``,
``PublicationError``, ``ExportRecord``, ``clear_publication_cache``.

Matplotlib styling and exports
------------------------------

Choose among the Heri publication style, the **elegante** tick-aligned
scientific style, and Matplotlib defaults. Elegante chooses readable equal
tick steps with endpoints on spines; its spline lines are preserved while
Line2D markers are inset so their glyphs do not touch the axes. Its
configuration supports tick targets, marker clearance, sparse visual
markers, optional zero inclusion and padding. Explicit user limits are
preserved. Use a scoped context, choose fonts and categorical cycles, label
multi-panel results and save vector/hybrid outputs. For older figures choose
``palette="legacy"``. The original HERI_PALETTE and continuous
HERI_CMAP remain public. :doc:`style` includes rendered examples and the
mathematical boundary-selection rule.

**Public exports:** ``set_style``, ``style_context``, ``available_styles``,
``apply_elegant_axes``, ``nice_tick_bounds``, ``panel_label``,
``save_figure``, ``HERI_PALETTE``, ``HERI_CMAP``,
``HERI_IRIDESCENT_HEX``, ``HERI_NEUTRAL``.

Accessibility previews and true-vector dashboards
-------------------------------------------------

Raster snapshots support arbitrary figure screenshots in the original, grayscale, print-stress, protanopia, deuteranopia and tritanopia conditions. The separate vector helper reconstructs supported Line2D and scatter PathCollection artists as PDF/PGF paths. It does not support all image, patch or heatmap artists.

**Public exports:** ``DEFAULT_ACCESSIBILITY_MODES``, ``figure_to_rgba``, ``figure_variants``, ``simulate_cvd_image``, ``simulate_figure``, ``show_accessibility_panel``, ``save_accessibility_panel``, ``to_grayscale_image``, ``to_print_stress_image``, ``show_vector_accessibility_panel``.

Document-aware publication and LaTeX
------------------------------------

Measure a trusted LaTeX preamble, set real single- or double-column figure widths, match nominal body font sizes, inspect TeX font identifiers through local tools, export PGF under document-owned fonts, audit physical typography, and verify unscaled PDF placement.

**Public exports:** ``TEX_PT_PER_INCH``, ``LatexLayout``, ``LatexProbeError``, ``LatexFontInfo``, ``find_latex_font``, ``FigureAudit``, ``FitResult``, ``PublicationStyle``, ``inspect_latex``, ``latex_style``, ``audit_figure``, ``fit_figure_to_latex``, ``verify_latex_placement``.

Specialized chart helper
------------------------

An optional pie-chart helper uses white wedge separators and print-oriented categorical colours by default. This is part of the library even though the publication demonstration focuses on line, scatter and matrix plots.

**Public exports:** ``pie_plot``.

Interactive tools, demos and development workflows
--------------------------------------------------

These are implemented repository features, **not** separate Python API names.

* :doc:`studio`: interactive Palette & Plot Studio, including equidistant,
  golden-angle, balanced-family, analogous, single-hue and manual hue layouts;
  luminance/contrast rules; categorical markers and line styles; background
  and alpha changes; local save, JSON import/export and Python preset export.
  `Open the deployed Studio <https://heri-espino.github.io/Colors/studio.html>`_.
* :doc:`gallery`: plot directive renders live Matplotlib output, including
  line, scatter, uncertainty, heatmap and multipanel demonstrations.
* :doc:`notebooks/index`: 13 executable notebooks with more plot families,
  plus generated accessibility examples. Notebooks are not separate custom
  plotting primitives.
* :doc:`publication_demo`: two-column LaTeX technical presentation with
  native font reuse, colour contrast grid, vector/hybrid examples, and
  portrait/landscape accessibility dashboards. Generated PDFs are published
  after a local successful MacTeX build.
* :doc:`publication`: explanation of dimension audits, TeX font resolution,
  PGF export and placement proofs.
* ``tools/setup_and_run.ps1``: Windows/Conda setup, tests, notebook refresh and
  strict Sphinx build.
* ``examples/latex_publication/run_macos.sh``: MacTeX/Conda publication build,
  tests and opt-in push of final PDF figures.
* ``tools/execute_notebooks.py`` and GitHub Actions: reproducible notebook
  execution and documentation deployment, with heavy refresh work manually
  initiated.
* ``pyproject.toml``, ``environment.yml``, ``LICENSE``: packaging,
  dependencies and licensing.

Design examples
---------------

Make a palette with explicit contrast levels:

.. code-block:: python

   import awesomefigures as af

   p = af.contrast_palette(
       hues=[25, 155, 275], ratio=1.55,
       start_luminance=0.65, chroma=0.12,
   )
   print(p.hex)
   print(p.luminances)
   print(p.adjacent_contrast)

For a three-series paper plot with adaptive grayscale differences and
redundant line encodings:

.. code-block:: python

   styles = af.plot_scheme([25, 155, 275])
   for values, styling in zip(three_y_series, styles):
       ax.plot(x, values, **styling)

For real manuscript dimensions and its own TeX font glyphs:

.. code-block:: python

   with af.latex_style("paper/main.tex", width="column") as pub:
       fig, ax = pub.subplots()
       ax.plot([0, 1, 2], [1, 3, 2])
       pub.savefig(fig, "paper/figures/figure.pgf")

Add the figure to the original LaTeX manuscript using
``\\input{figures/figure.pgf}``, not by scaling a screenshot.

What is not claimed
-------------------

* WCAG relative-luminance separation is not a formal guarantee that groups
  are distinguishable for every form of colour-vision deficiency.
* Grayscale and print-stress views are approximate diagnostics, not
  calibrated printer profiles.
* A PDF can contain vector paths, embedded raster art, or both. The dense
  plot example intentionally rasterizes data, while retaining vector text.
* Only the supported line/scatter dashboard redraw is guaranteed vector;
  generic image preview panels are still raster previews.
* A font name and a nominal point size are distinct. PGF inherits fonts when
  typeset inside the same original trusted LaTeX document. Matplotlib's
  separately exported PDF can use a substitute.
* This project does not claim that it adds every chart family shown in the
  cookbook to Matplotlib. Those examples use Matplotlib artists combined
  with the package's styles, palettes and diagnostics.
