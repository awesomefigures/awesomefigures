Examples
========

Five-series line plot
---------------------

.. code-block:: python

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="Arial")

   x = np.linspace(0, 2 * np.pi, 500)
   colors = af.color_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.25,
       start_luminance=0.72,
   )

   fig, ax = plt.subplots(figsize=(7.2, 3.7))
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
   af.save_figure(fig, "line_plot.pdf")

Scatter plot with alpha compensation
------------------------------------

.. code-block:: python

   palette = af.contrast_palette(
       hues=[20, 145, 210],
       ratio=1.35,
       start_luminance=0.75,
   )

   colors = palette.mpl_colors(
       alpha=0.65,
       background="white",
       preserve_apparent=True,
   )

   fig, ax = plt.subplots()
   for group, color in zip(groups, colors):
       ax.scatter(group.x, group.y, color=color)

Heatmap using the Heri continuous map
-------------------------------------

.. code-block:: python

   af.set_style("heri", font="Arial")

   fig, ax = plt.subplots()
   image = ax.imshow(
       matrix,
       cmap=af.HERI_CMAP,
       interpolation="nearest",
   )
   fig.colorbar(image, ax=ax)
   af.save_figure(fig, "heatmap.pdf")

Multi-panel publication figure
------------------------------

.. code-block:: python

   af.set_style("heri", font="Arial")

   fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.7))

   axes[0].plot(x, y1)
   axes[1].scatter(x, y2)

   af.panel_label(axes[0], "A")
   af.panel_label(axes[1], "B")

   fig.tight_layout()
   af.save_figure(
       fig,
       "two_panel.pdf",
       metadata={
           "Title": "Two-panel example",
           "Author": "Heriberto Espino Montelongo",
       },
   )

Temporary style
---------------

.. code-block:: python

   with af.style_context("heri", font="Arial"):
       fig, ax = plt.subplots()
       ax.plot(x, y)

   # Previous Matplotlib rcParams are restored here.

Inspect contrast mathematically
-------------------------------

.. code-block:: python

   ys = af.luminance_ladder(
       levels=5,
       ratio=1.4,
       start_luminance=0.95,
   )

   for a, b in zip(ys[:-1], ys[1:]):
       print(af.luminance_contrast(a, b))

Inspect two arbitrary colors
----------------------------

.. code-block:: python

   print(af.relative_luminance("#0083F9"))
   print(af.contrast_ratio("#0083F9", "#97001C"))
   print(af.delta_e_ok("#0083F9", "#97001C"))
