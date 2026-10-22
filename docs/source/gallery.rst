Plot gallery
============

Every image on this page is rendered by Matplotlib from the installed
``awesomefigures`` package during the documentation build.

For the complete gallery with runnable code and saved figures, open the
:doc:`13-notebook cookbook <notebooks/index>`. You can also browse the
`raw notebooks on GitHub <https://github.com/heri-espino/Colors/tree/main/docs/source/notebooks>`_.

Line plots
----------

The high-level ``plot_scheme`` helper combines color, marker and line style.
That gives the same series more than one visual identifier.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="DejaVu Sans")

   x = np.linspace(0, 12, 350)
   scheme = af.plot_scheme(
       hues=[55, 20, 145, 210, 290],
       ratio=1.22,
       start_luminance=0.72,
       markers=["o", "s", "^", "D", "X"],
       linestyles=["-", "--", ":", "-.", (0, (5, 2))],
   )

   fig, ax = plt.subplots(figsize=(8.2, 4.2))
   for i, kwargs in enumerate(scheme):
       y = np.sin(0.65 * x + i * 0.52) + i * 0.42
       ax.plot(x, y, markevery=55, label=f"Series {i + 1}", **kwargs)

   ax.set(title="Five-series comparison", xlabel="Time", ylabel="Response")
   ax.legend(ncol=3)
   fig.tight_layout()

Scatter with alpha compensation
-------------------------------

``preserve_apparent=True`` pre-compensates the source color for the selected
background when exact recovery is possible, and uses the perceptual fallback
otherwise.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="DejaVu Sans")
   rng = np.random.default_rng(18)

   palette = af.contrast_palette(
       hues=[20, 145, 210],
       ratio=1.28,
       start_luminance=0.68,
   )
   colors = palette.mpl_colors(
       alpha=0.62,
       background="white",
       preserve_apparent=True,
   )

   fig, ax = plt.subplots(figsize=(7.8, 4.2))
   markers = ["o", "s", "^"]
   for i, (color, marker) in enumerate(zip(colors, markers)):
       x = rng.normal(1.0 + i * 1.25, 0.45, 120)
       y = 0.55 * x + rng.normal(i * 0.25, 0.48, 120)
       ax.scatter(x, y, color=color, marker=marker, s=28,
                  label=f"Group {i + 1}")

   ax.set(title="Transparent observations", xlabel="Feature", ylabel="Outcome")
   ax.legend()
   fig.tight_layout()

Uncertainty bands and error bars
--------------------------------

The Heri preset keeps ordinary lines and typography vector in PDF output while
dense artists may be rasterized.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="DejaVu Sans")

   x = np.linspace(0, 8, 220)
   y = 0.3 * np.cos(x * 0.8) + 0.08 * x
   band = 0.17 + 0.035 * np.sin(x * 1.2)
   points = np.arange(0, len(x), 28)

   fig, ax = plt.subplots(figsize=(7.8, 4.2))
   ax.fill_between(
       x, y - band, y + band,
       color=af.HERI_PALETTE[1], alpha=0.20,
       label="95% interval",
   )
   ax.plot(x, y, color=af.HERI_PALETTE[1], label="Posterior mean")
   ax.errorbar(
       x[points], y[points],
       yerr=0.11,
       fmt="o",
       color=af.HERI_PALETTE[0],
       capsize=2.5,
       label="Observed",
   )
   ax.set(title="Estimate with uncertainty", xlabel="Index", ylabel="Value")
   ax.legend()
   fig.tight_layout()

Heatmaps
--------

``HERI_CMAP`` is the continuous iridescent map used by the publication style.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="DejaVu Sans")

   a = np.linspace(-2.2, 2.2, 90)
   b = np.linspace(-1.8, 1.8, 62)
   X, Y = np.meshgrid(a, b)
   Z = np.exp(-0.32 * (X**2 + Y**2)) * np.cos(2.4 * X) + 0.16 * Y

   fig, ax = plt.subplots(figsize=(7.8, 4.2))
   im = ax.imshow(
       Z,
       cmap=af.HERI_CMAP,
       origin="lower",
       aspect="auto",
       extent=[a.min(), a.max(), b.min(), b.max()],
   )
   ax.set(title="Continuous scalar field", xlabel="x", ylabel="y")
   fig.colorbar(im, ax=ax, label="Value")
   fig.tight_layout()

Multi-panel paper figures
-------------------------

Panel labels, compact typography and a consistent visual hierarchy are part of
the Heri workflow.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="DejaVu Sans")
   rng = np.random.default_rng(4)

   x = np.linspace(0, 6, 180)
   fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.1))

   axes[0].plot(x, np.sin(x), color=af.HERI_PALETTE[1])
   axes[0].plot(x, np.cos(x), color=af.HERI_PALETTE[0], linestyle="--")
   axes[0].set_title("Signals")

   xx = rng.normal(size=160)
   yy = 0.6 * xx + rng.normal(scale=0.65, size=160)
   axes[1].scatter(xx, yy, color=af.HERI_PALETTE[2], alpha=0.72, s=18)
   axes[1].set_title("Relationship")

   bars = [1.0, 1.35, 0.82, 1.55, 1.18]
   axes[2].bar(
       np.arange(len(bars)),
       bars,
       color=af.HERI_PALETTE,
       edgecolor="white",
       linewidth=0.6,
   )
   axes[2].set_title("Categories")

   for label, ax in zip("ABC", axes):
       af.panel_label(ax, label, x=-0.12)
       ax.set_xlabel("x")
   fig.tight_layout()

Need a particular recipe?
-------------------------

The :doc:`customization` page shows how to change the number and order of
colors, markers, line styles, fonts, alpha and style settings. The
:doc:`studio` lets you do the same interactively and exports the Python.


Notebook cookbook
-----------------

The gallery above is intentionally compact. The notebook cookbook contains
many more plot families and keeps explanation, code, and rendered output
together.

.. grid:: 1 2 2 3
   :gutter: 2

   .. grid-item-card:: Lines & time series
      :link: notebooks/01_lines_time_series
      :link-type: doc

      Multi-line schemes, rolling trends, steps, and time-series examples.

   .. grid-item-card:: Histograms & distributions
      :link: notebooks/02_histograms_distributions
      :link-type: doc

      Histograms, smoothed densities, ECDFs, and cumulative histograms.

   .. grid-item-card:: Box / violin / ridge
      :link: notebooks/03_box_violin_ridge
      :link-type: doc

      Grouped distributions, ridge plots, and jittered observations.

   .. grid-item-card:: Scatter & relationships
      :link: notebooks/04_scatter_relationships
      :link-type: doc

      Grouped scatter, fitted trends, hexbin density, and bubble plots.

   .. grid-item-card:: Heatmaps & matrices
      :link: notebooks/05_heatmaps_matrices
      :link-type: doc

      Heatmaps, correlation matrices, contours, and pcolormesh.

   .. grid-item-card:: All notebooks
      :link: notebooks/index
      :link-type: doc

      Open the complete executable example collection.
