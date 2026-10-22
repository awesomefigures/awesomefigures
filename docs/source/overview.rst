Library tour
============

This page is the map of the library. If you only want to make a plot, start
with color_palette and set_style. If you want diagnostics or to build tooling
on top of the package, use the lower-level objects.

What the library contains
-------------------------

Palette construction
~~~~~~~~~~~~~~~~~~~~

color_palette
    The shortest path from a sequence of hue angles to Matplotlib-ready RGBA
    colors with a controlled adjacent contrast ratio.

contrast_palette
    Builds the same palette but returns a Palette object with metadata,
    luminances, contrast diagnostics, alpha rendering, and colormap export.

register_palette / get_palette / available_palettes
    Register named palette specifications, retrieve them, and list
    registrations in the current Python session. Save the registration
    in a Python module for reuse across scripts.

plot_scheme
    Combines contrast-controlled colors with marker and line-style identifiers
    for redundant scientific-plot encoding and grayscale robustness.

DEFAULT_MARKERS and DEFAULT_LINESTYLES
    Default identifier cycles used by plot_scheme when no custom sequences are
    supplied.

contrast_grid
    Builds an i by j matrix of candidate colors. Rows have fixed relative
    luminance and columns have fixed hue.

color_for_luminance
    Constructs one color for a requested WCAG relative luminance and hue,
    reducing OKLCH chroma only when required by the sRGB gamut.

Palette objects
~~~~~~~~~~~~~~~

ColorCell
    One solved color. Stores RGB, hue, target and achieved luminance, requested
    and achieved chroma, and solved OKLCH lightness.

RenderedColor
    One ColorCell after alpha/background preparation.

Palette
    Ordered sequence of ColorCell objects. Provides hex, RGB, luminance,
    adjacent-contrast, alpha-rendering, minimum-alpha, and ListedColormap
    helpers.

ContrastGrid
    Matrix of ColorCell objects with fixed luminance by row and hue by column.
    Supports arbitrary one-per-row selections, diagonal selections, hex export,
    and plotting.

Contrast mathematics
~~~~~~~~~~~~~~~~~~~~

luminance_ladder
    Generates the sequence of relative luminances that produces a constant
    adjacent WCAG contrast ratio.

luminance_contrast
    Computes a WCAG contrast ratio directly from two relative luminances.

contrast_ratio
    Computes WCAG contrast directly from two colors.

relative_luminance
    Computes WCAG relative luminance from an sRGB color.

Alpha and compositing
~~~~~~~~~~~~~~~~~~~~~

composite
    Applies standard foreground/background alpha compositing.

compensate_alpha
    Solves for the source color that should be drawn so the composited result
    reproduces the desired target color.

minimum_alpha
    Finds the smallest opacity at which exact target-color recovery is possible
    for a known background.

AlphaCompensation
    Diagnostic result object containing source, target, displayed color,
    feasibility, channel error, and OKLab error.

Color utilities
~~~~~~~~~~~~~~~

to_rgb
    Accepts hex, Matplotlib color names, or RGB triples and returns an sRGB
    NumPy triple.

to_hex
    Converts a supported color input to hexadecimal RGB.

srgb_to_oklab
    Converts sRGB to OKLab coordinates.

delta_e_ok
    Euclidean color distance in OKLab.

The color_spaces module also contains lower-level helpers for sRGB transfer
functions, OKLCH conversion, and gamut testing. These are documented in the API
reference.

Publication plotting
~~~~~~~~~~~~~~~~~~~~

set_style
    Applies a global Matplotlib preset. The Heri preset follows the publication
    figures from Bayesian-Uncertainty-in-WTI-APOs and lets the user select the
    font independently.

style_context
    Applies a style temporarily and restores the previous Matplotlib state.

save_figure
    Saves a hybrid publication figure. Dense artists can remain raster while
    text, axes, lines, and annotations remain vector.

panel_label
    Adds the A/B/C-style panel labels used by the Heri publication style.

available_styles
    Returns the registered style names.

Heri constants
~~~~~~~~~~~~~~

HERI_PALETTE
    Five-color Paul Tol categorical palette used as the default line cycle.

HERI_CMAP
    Continuous iridescent colormap used for heatmaps and dense scalar fields.

HERI_IRIDESCENT_HEX
    Source control points used to construct HERI_CMAP.

HERI_NEUTRAL
    Neutral black/gray/grid colors used by the style.

Typical workflows
-----------------

Shortest plotting workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import awesomefigures as af

   af.set_style("heri", font="Arial")

   colors = af.color_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
   )

   for series, color in zip(data, colors):
       ax.plot(x, series, color=color)

Palette with diagnostics
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   palette = af.contrast_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
   )

   print(palette.hex)
   print(palette.luminances)
   print(palette.adjacent_contrast)
   print(palette.minimum_alpha(background="white"))

Explore a matrix of choices
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   grid = af.contrast_grid(
       levels=5,
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
   )

   grid.plot()
   palette = grid.select([0, 3, 1, 4, 2])

Alpha-aware rendering
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   palette = af.contrast_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
   )

   rendered = palette.render(
       alpha=0.75,
       background="white",
       preserve_apparent=True,
       alpha_strategy="perceptual",
   )

   for item in rendered:
       print(item.target.hex)
       print(item.compensation.source_hex)
       print(item.compensation.displayed_hex)
       print(item.compensation.feasible)
       print(item.compensation.delta_e_ok)
