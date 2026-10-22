Quickstart
==========

Installation
------------

From a local checkout:

.. code-block:: bash

   python -m pip install -e .

For development and documentation:

.. code-block:: bash

   python -m pip install -e ".[dev,docs]"
   pytest
   sphinx-build -W -b html docs/source docs/_build/html

A complete first plot
---------------------

.. code-block:: python

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="Arial")

   colors = af.color_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
   )

   x = np.linspace(0, 2 * np.pi, 500)

   fig, ax = plt.subplots()
   for k, color in enumerate(colors):
       ax.plot(
           x,
           np.sin(x + 0.35 * k),
           color=color,
           label=f"series {k + 1}",
       )

   ax.set_xlabel("x")
   ax.set_ylabel("value")
   ax.legend()

   af.save_figure(fig, "example.pdf")

What happened
-------------

The hue list defines one hue per output color. The library creates a decreasing
relative-luminance ladder whose adjacent WCAG contrast ratio is 1.4, then solves
for an sRGB color at each hue and luminance.

The Heri style changes Matplotlib presentation independently of palette
construction. In the example above, Arial affects typography but does not alter
the palette mathematics.

Inspecting the palette
----------------------

Use contrast_palette when you want the solved colors and diagnostics rather
than only Matplotlib RGBA tuples.

.. code-block:: python

   palette = af.contrast_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
   )

   print(palette.hex)
   print(palette.luminances)
   print(palette.adjacent_contrast)

Alpha-aware colors
------------------

.. code-block:: python

   colors = af.color_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
       alpha=0.70,
       background="white",
       preserve_apparent=True,
   )

When exact apparent-color recovery is impossible at the requested alpha, the
default perceptual strategy finds a representable source color with small
OKLab error.

Exploring multiple hue choices
------------------------------

.. code-block:: python

   grid = af.contrast_grid(
       levels=5,
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
   )

   grid.plot()
   palette = grid.select([0, 1, 2, 3, 4])

Each row has a fixed relative luminance, so any one-color-per-row selection
inherits the same adjacent contrast ladder.

Where to go next
----------------

Library tour
   A complete inventory of what the package contains.

Palettes and grids
   Palette objects, ColorCell metadata, ContrastGrid, colormaps, and hue
   selection.

Alpha and apparent color
   Composition, compensation, feasibility, minimum alpha, and OKLab fallback.

Heri publication style
   Fonts, white-grid styling, panel labels, continuous colormap, and hybrid PDF
   output.

Mathematics
   The equations behind the contrast ladder and alpha compensation.

API reference
   Exact signatures and class members for the complete library.
