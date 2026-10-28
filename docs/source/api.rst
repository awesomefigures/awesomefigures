API reference
=============

This reference documents the public API first, followed by lower-level module
helpers intended for advanced use.

Automatic publication from manuscripts
--------------------------------------

.. autofunction:: awesomefigures.paper

.. autoclass:: awesomefigures.Publication
   :members: subplots, savefig, report

.. autoclass:: awesomefigures.ExportRecord
   :members: passed

.. autoclass:: awesomefigures.PublicationError

.. autofunction:: awesomefigures.clear_publication_cache

High-level palette API
----------------------

.. autofunction:: awesomefigures.color_palette

.. autofunction:: awesomefigures.contrast_palette

.. autofunction:: awesomefigures.show_palette

.. autofunction:: awesomefigures.plot_scheme

.. autofunction:: awesomefigures.scatter_scheme

DEFAULT_MARKERS
    Default marker sequence used by plot_scheme.

DEFAULT_LINESTYLES
    Default line-style sequence used by plot_scheme.

Accessibility and print previews
--------------------------------

DEFAULT_ACCESSIBILITY_MODES
    Original, grayscale, print-stress, deuteranopia, protanopia, tritanopia.

.. autofunction:: awesomefigures.figure_to_rgba

.. autofunction:: awesomefigures.to_grayscale_image

.. autofunction:: awesomefigures.to_print_stress_image

.. autofunction:: awesomefigures.simulate_cvd_image

.. autofunction:: awesomefigures.simulate_figure

.. autofunction:: awesomefigures.figure_variants

.. autofunction:: awesomefigures.show_vector_accessibility_panel

For standard line and scatter plots, this function redraws vector artists
per viewing mode instead of rasterizing the original graphic. Export its
Matplotlib figure as PDF or PGF; PGF can be included in the manuscript for
the exact document font. Unsupported artist types raise explicitly.

.. autofunction:: awesomefigures.show_accessibility_panel

.. autofunction:: awesomefigures.save_accessibility_panel

Preinstalled historical palettes and colormaps
----------------------------------------------

The original named categorical palettes preserve their source HEX
values; their contrast ratios are not rebuilt by the OKLCH solver.
Continuous maps use Matplotlib's original colormap implementations.
The two systems can be selected from high-level plotting helpers.

.. autoclass:: awesomefigures.NamedPalette
   :members:

.. autofunction:: awesomefigures.available_named_palettes

.. autofunction:: awesomefigures.get_named_palette

.. autofunction:: awesomefigures.named_palette

.. autofunction:: awesomefigures.named_colormap

.. code-block:: python

   af.color_palette("okabe-ito", as_hex=True)
   af.plot_scheme("tol-bright", n=5)
   af.set_style("elegante", palette="brewer-dark2")
   ax.imshow(values, cmap=af.named_colormap("cividis"))

See :doc:`named_palettes` for full visual examples, exact HEX sets and
source attribution.

User-defined palette presets
----------------------------

Presets register palettes for the current Python process. Put the registration
in a project module, then import it in each script that needs those names.

.. autofunction:: awesomefigures.register_palette

.. autofunction:: awesomefigures.get_palette

.. autofunction:: awesomefigures.available_palettes

.. autoclass:: awesomefigures.PalettePreset
   :members:

Example:

.. code-block:: python

   import awesomefigures as af

   af.register_palette(
       "paper_palette",
       hues=[55, 20, 145, 210, 290],
       ratio=1.25,
       start_luminance=0.72,
       markers=["o", "s", "^", "D", "X"],
       linestyles=["-", "--", ":", "-.", (0, (5, 2))],
   )
   colors = af.color_palette("paper_palette")
   scheme = af.plot_scheme("paper_palette")

Core palette objects
--------------------

.. autoclass:: awesomefigures.ColorCell
   :members:

.. autoclass:: awesomefigures.RenderedColor
   :members:

.. autoclass:: awesomefigures.Palette
   :members:
   :special-members: __len__, __getitem__

.. autoclass:: awesomefigures.ContrastGrid
   :members:
   :special-members: __getitem__

Palette construction
--------------------

.. autofunction:: awesomefigures.color_for_luminance

.. autofunction:: awesomefigures.contrast_grid

Contrast mathematics
--------------------

.. autofunction:: awesomefigures.luminance_ladder

.. autofunction:: awesomefigures.luminance_contrast

.. autofunction:: awesomefigures.relative_luminance

.. autofunction:: awesomefigures.contrast_ratio

Alpha and compositing
---------------------

.. autoclass:: awesomefigures.AlphaCompensation
   :members:

.. autofunction:: awesomefigures.composite

.. autofunction:: awesomefigures.compensate_alpha

.. autofunction:: awesomefigures.minimum_alpha

Color utilities
---------------

.. autofunction:: awesomefigures.to_rgb

.. autofunction:: awesomefigures.to_hex

.. autofunction:: awesomefigures.srgb_to_oklab

.. autofunction:: awesomefigures.delta_e_ok

Categorical pie charts
----------------------

.. autofunction:: awesomefigures.pie_plot

Pie wedges use white separators by default (with a user-overridable
edgecolor/linewidth), plus the same adaptive color and luminance policy
as other categorical plots.

Adaptive print-safe colors
--------------------------

.. autofunction:: awesomefigures.print_safe_luminances

The default awesomefigures.plot_scheme() and scatter_scheme() distribute
luminances across a broad grayscale range when the number of series is
small (and both the contrast ratio and starting luminance are omitted).
Named presets and explicit contrast ratios are kept unchanged.

LaTeX layout and publication fitting
------------------------------------

.. autoclass:: awesomefigures.LatexFontInfo
   :members:

.. autofunction:: awesomefigures.find_latex_font

.. autoclass:: awesomefigures.LatexLayout
   :members:

.. autoexception:: awesomefigures.LatexProbeError

.. autoclass:: awesomefigures.PublicationStyle
   :members:

.. autoclass:: awesomefigures.FigureAudit
   :members:

.. autoclass:: awesomefigures.FitResult
   :members:

.. autofunction:: awesomefigures.inspect_latex

.. autofunction:: awesomefigures.latex_style

.. autofunction:: awesomefigures.audit_figure

.. autofunction:: awesomefigures.fit_figure_to_latex

.. autofunction:: awesomefigures.verify_latex_placement

TEX_PT_PER_INCH
    Conversion constant: 72.27 TeX points per inch.

Publication style
-----------------

.. autofunction:: awesomefigures.set_style

.. autofunction:: awesomefigures.style_context

.. autofunction:: awesomefigures.apply_elegant_axes

.. autofunction:: awesomefigures.nice_tick_bounds

.. autofunction:: awesomefigures.save_figure

.. autofunction:: awesomefigures.panel_label

.. autofunction:: awesomefigures.available_styles

Heri style constants
--------------------

HERI_PALETTE
    Five categorical colors used as the default Heri line cycle.

    .. code-block:: text

       #97001c
       #0083f9
       #00b49c
       #ffc600
       #f198ff

HERI_NEUTRAL
    Neutral colors used for axes, reference lines, and grid styling.

    .. code-block:: python

       {
           "black": "#111111",
           "dark": "#3A3A3A",
           "mid": "#777777",
           "light": "#B0B0B0",
           "grid": "#D8D8D8",
       }

HERI_IRIDESCENT_HEX
    Twenty-three control colors used to construct the continuous Heri
    iridescent colormap.

HERI_CMAP
    A 256-level Matplotlib LinearSegmentedColormap constructed from
    HERI_IRIDESCENT_HEX. Missing/bad values use #999999.

Advanced color-space helpers
----------------------------

These functions live in the awesomefigures.color_spaces module. They are useful
for implementing custom palette algorithms or diagnostics, but are not all
re-exported at the package root.

.. autofunction:: awesomefigures.color_spaces.srgb_to_linear

.. autofunction:: awesomefigures.color_spaces.linear_to_srgb

.. autofunction:: awesomefigures.color_spaces.oklch_to_linear_srgb

.. autofunction:: awesomefigures.color_spaces.in_srgb_gamut

Advanced style constants
------------------------

awesomefigures.style.HERI_BAD_DATA_COLOR
    Hex color #999999 used for bad/missing values in HERI_CMAP.

awesomefigures.style.HERI_SAVEFIG_KWARGS
    Default save settings used by save_figure:

    .. code-block:: python

       {
           "dpi": 600,
           "bbox_inches": "tight",
           "pad_inches": 0.035,
           "facecolor": "white",
           "edgecolor": "white",
           "transparent": False,
       }
