Palettes and grids
==================

Famous preinstalled palettes
----------------------------

You can use exact published schemes without registration.

.. code-block:: python

   import awesomefigures as af

   print(af.available_named_palettes())
   okabe_ito = af.color_palette("okabe-ito", as_hex=True)
   tol = af.plot_scheme("tol-bright", n=4)
   image = ax.imshow(values, cmap=af.named_colormap("cividis"))

``okabe-ito`` and its ``colorblind`` alias preserve the original eight
HEX values. Paul Tol and ColorBrewer presets also preserve their historical
colours. Continuous maps retain their native Matplotlib interpolation.
For the complete illustrated catalogue and source references see
:doc:`named_palettes`.

Unlike a contrast-controlled palette, these palettes are **not**
recomputed for a requested adjacent WCAG ratio. Passing ``ratio``,
``start_luminance``, or ``chroma`` alongside a historical scheme raises
an informative exception rather than changing its identity.

High-level palette
------------------

Use color_palette when you want colors immediately.

.. code-block:: python

   import awesomefigures as af

   colors = af.color_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
       start_luminance=0.95,
       chroma=0.13,
   )

The number of supplied hues is the number of output colors. Hue k is assigned
to luminance level k.

Returning hex colors
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   colors = af.color_palette(
       hues=[55, 20, 145],
       ratio=1.3,
       as_hex=True,
   )

Palette objects
---------------

Use contrast_palette when you want to inspect or reuse the solved palette.

.. code-block:: python

   palette = af.contrast_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
   )

Useful attributes and methods:

.. code-block:: python

   palette.hex
   palette.rgb
   palette.luminances
   palette.adjacent_contrast

   palette.mpl_colors()
   palette.render(alpha=0.7, background="white")
   palette.minimum_alpha(background="white")
   palette.as_cmap(name="my_palette")

Each element of a Palette is a ColorCell:

.. code-block:: python

   cell = palette[0]

   cell.hex
   cell.rgb
   cell.hue
   cell.target_luminance
   cell.actual_luminance
   cell.requested_chroma
   cell.actual_chroma
   cell.oklch_lightness

Hue-luminance grids
-------------------

A ContrastGrid separates luminance level from hue choice:

.. math::

   C_{ij}=C(Y_i,h_j).

Build one with:

.. code-block:: python

   grid = af.contrast_grid(
       levels=5,
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
       start_luminance=0.95,
       chroma=0.13,
   )

Important grid data:

.. code-block:: python

   grid.shape
   grid.hues
   grid.luminances
   grid.ratio
   grid.hex

Selecting colors
~~~~~~~~~~~~~~~~

Choose one column index for each row:

.. code-block:: python

   palette = grid.select([4, 1, 3, 0, 2])

Because every row has fixed relative luminance, changing the selected hue in a
row does not change the prescribed contrast ratio between rows.

A cyclic diagonal shortcut is available:

.. code-block:: python

   palette = grid.diagonal()

Visualizing the grid
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   ax = grid.plot()
   ax.figure.show()

Single-color construction
-------------------------

For lower-level work, solve one hue/luminance target directly:

.. code-block:: python

   cell = af.color_for_luminance(
       target_luminance=0.40,
       hue=145,
       chroma=0.13,
   )

The requested chroma may be reduced if the requested combination lies outside
sRGB. Compare requested_chroma with actual_chroma to inspect this behavior.

Matplotlib colormaps
--------------------

A discrete palette can become a ListedColormap:

.. code-block:: python

   cmap = palette.as_cmap(name="five_level")
   image = ax.imshow(values, cmap=cmap)

For a continuous publication heatmap, the Heri style also exposes HERI_CMAP:

.. code-block:: python

   image = ax.imshow(values, cmap=af.HERI_CMAP)
