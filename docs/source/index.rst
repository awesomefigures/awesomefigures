.. raw:: html

   <section class="cc-hero">
     <div>
       <div class="cc-eyebrow">AwesomeFigures / Scientific plotting toolkit</div>
       <h1>AwesomeFigures<span class="af-title-dot">.</span><br>Every figure, considered.</h1>
       <p>
         Build publication-ready scientific figures with famous accessible
         palettes, careful axis geometry, spacious line markers, and a
         precise path from Matplotlib to LaTeX.
       </p>
       <div class="cc-actions">
         <a class="cc-button primary" href="studio.html">Open Palette Studio</a>
         <a class="cc-button" href="named_palettes.html">Explore palettes</a>
         <a class="cc-button" href="style.html">Explore styles</a>
         <a class="cc-button" href="gallery.html">See the plot gallery</a>
         <a class="cc-button" href="notebooks/index.html">Browse 13 notebooks</a>
         <a class="cc-button" href="quickstart.html">Quickstart</a>
       </div>
     </div>
     <div class="cc-hero-palette" aria-label="Heri palette">
       <span style="background:#97001c;color:white">#97001c</span>
       <span style="background:#0083f9;color:white">#0083f9</span>
       <span style="background:#00b49c;color:#111">#00b49c</span>
       <span style="background:#ffc600;color:#111">#ffc600</span>
       <span style="background:#f198ff;color:#111">#f198ff</span>
     </div>
   </section>

Styles: from raw plots to publication-ready axes
------------------------------------------------

Three complementary styles let you decide how much layout discipline
Matplotlib applies before the figure is exported.

.. grid:: 1 2 2 3
   :gutter: 2

   .. grid-item-card:: Elegante
      :link: style
      :link-type: doc

      Endpoint-aligned readable ticks, no arbitrary axis margin, and inset
      line markers that never collide with the frame.

   .. grid-item-card:: Heri
      :link: style
      :link-type: doc

      Print-aware hues, distinct markers and line patterns, compact
      publication typography, and vector-first exports.

   .. grid-item-card:: Matplotlib default
      :link: style
      :link-type: doc

      The familiar baseline, available to restore native Matplotlib
      behavior at any time.

The palette library
-------------------

A curated catalogue of familiar, attributed colours is ready to use in
``AwesomeFigures``. Named palettes keep their original published HEX
coordinates; the custom OKLCH engine remains available when you need
mathematically controlled luminance and contrast.

.. raw:: html

   <div class="af-palette-gallery" aria-label="Featured scientific palettes">
     <a class="af-palette-card" href="named_palettes.html">
       <span class="af-palette-category">Colour-vision-aware starting point</span>
       <strong>Okabe–Ito</strong>
       <span class="af-palette-strip" aria-label="Eight original Okabe–Ito colours">
         <i style="background:#E69F00"></i><i style="background:#56B4E9"></i><i style="background:#009E73"></i><i style="background:#F0E442"></i><i style="background:#0072B2"></i><i style="background:#D55E00"></i><i style="background:#CC79A7"></i><i style="background:#000000"></i>
       </span>
       <span class="af-palette-caption">8 categorical colours · Original published values</span>
     </a>
     <a class="af-palette-card" href="named_palettes.html">
       <span class="af-palette-category">Qualitative colour cycle</span>
       <strong>Paul Tol · Bright</strong>
       <span class="af-palette-strip" aria-label="Seven Paul Tol Bright colours">
         <i style="background:#4477AA"></i><i style="background:#EE6677"></i><i style="background:#228833"></i><i style="background:#CCBB44"></i><i style="background:#66CCEE"></i><i style="background:#AA3377"></i><i style="background:#BBBBBB"></i>
       </span>
       <span class="af-palette-caption">7 categories · Distinct hues and values</span>
     </a>
     <a class="af-palette-card" href="named_palettes.html">
       <span class="af-palette-category">Categorical design system</span>
       <strong>ColorBrewer · Dark2</strong>
       <span class="af-palette-strip" aria-label="Eight ColorBrewer Dark2 colours">
         <i style="background:#1B9E77"></i><i style="background:#D95F02"></i><i style="background:#7570B3"></i><i style="background:#E7298A"></i><i style="background:#66A61E"></i><i style="background:#E6AB02"></i><i style="background:#A6761D"></i><i style="background:#666666"></i>
       </span>
       <span class="af-palette-caption">8 categorical colours · Readable on white</span>
     </a>
   </div>

More references include Paul Tol High Contrast and Muted, Tableau 10,
ColorBrewer Set2, and the sequential/diverging maps
``viridis``, ``cividis``, ``magma``, ``plasma``, ``inferno``, and
``RdBu``. Browse the full :doc:`illustrated palette atlas <named_palettes>`
or compare colours directly in :doc:`Palette & Plot Studio <studio>`.

Notebook cookbook: 13 executable demos
--------------------------------------

The complete notebook collection contains over 30 saved Matplotlib figures,
with runnable code directly alongside each output. Choose a topic below or
:doc:`browse all notebooks <notebooks/index>`.

.. grid:: 1 2 2 3
   :gutter: 2

   .. grid-item-card:: Histograms & distributions
      :link: notebooks/02_histograms_distributions
      :link-type: doc

      Histograms, KDE-like density curves, ECDF and cumulative distributions.

   .. grid-item-card:: Box, violin & ridge
      :link: notebooks/03_box_violin_ridge
      :link-type: doc

      Four ways to compare distributions by group.

   .. grid-item-card:: Lines & time series
      :link: notebooks/01_lines_time_series
      :link-type: doc

      Multi-series lines, markers, rolling trends and step plots.

   .. grid-item-card:: Scatter & regression
      :link: notebooks/04_scatter_relationships
      :link-type: doc

      Scatter, fitted trends, bubble and hexbin plots.

   .. grid-item-card:: Heatmaps & matrices
      :link: notebooks/05_heatmaps_matrices
      :link-type: doc

      Heatmaps, correlation matrices, contours and pcolormesh.

   .. grid-item-card:: All 13 notebooks
      :link: notebooks/index
      :link-type: doc

      Uncertainty, grayscale, paper figures, colormaps, alpha and more.

A plotting library should show plots
------------------------------------

The figures below are generated from the installed package during the Sphinx
build. They are not screenshots or hand-drawn approximations.

.. plot::

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="DejaVu Sans")

   rng = np.random.default_rng(7)
   x = np.linspace(0, 10, 250)
   colors = af.color_palette(
       hues=[20, 145, 210, 290],
       ratio=1.22,
       start_luminance=0.72,
   )

   fig, axes = plt.subplots(2, 2, figsize=(9.0, 5.6))

   for i, color in enumerate(colors):
       axes[0, 0].plot(
           x,
           np.sin(x * 0.72 + i * 0.5) + i * 0.34,
           color=color,
           label=f"Series {i + 1}",
       )
   axes[0, 0].set_title("Lines")
   axes[0, 0].legend(ncol=2)

   for i, color in enumerate(colors[:3]):
       xx = rng.normal(i * 1.0, 0.48, 70)
       yy = 0.45 * xx + rng.normal(i * 0.35, 0.42, 70)
       axes[0, 1].scatter(xx, yy, color=color, alpha=0.78, s=22)
   axes[0, 1].set_title("Scatter")

   mean = np.sin(x * 0.6)
   band = 0.18 + 0.06 * np.cos(x)
   axes[1, 0].plot(x, mean, color=af.HERI_PALETTE[1])
   axes[1, 0].fill_between(
       x, mean - band, mean + band,
       color=af.HERI_PALETTE[1], alpha=0.22
   )
   axes[1, 0].set_title("Uncertainty")

   z = np.outer(np.sin(np.linspace(0, np.pi, 42)),
                np.cos(np.linspace(-1.7, 1.7, 58)))
   im = axes[1, 1].imshow(z, cmap=af.HERI_CMAP, aspect="auto")
   axes[1, 1].set_title("Heatmap")
   fig.colorbar(im, ax=axes[1, 1], fraction=0.046, pad=0.04)

   for ax in axes.flat:
       ax.set_xlabel("x")
   fig.tight_layout()

From palette to paper
---------------------

.. grid:: 1 2 2 4
   :gutter: 2

   .. grid-item-card:: Design
      :link: studio
      :link-type: doc

      Pick the number of colors, hue order, contrast ratio, markers, line
      styles, alpha and background interactively.

   .. grid-item-card:: Preview
      :link: gallery
      :link-type: doc

      See line plots, scatter plots, uncertainty bands, error bars, heatmaps
      and multi-panel figures generated by the library.

   .. grid-item-card:: Customize
      :link: customization
      :link-type: doc

      Change hues, add more colors, choose fonts, markers, line styles and
      rendering behavior.

   .. grid-item-card:: Export
      :link: api
      :link-type: doc

      Copy a plotting scheme into Matplotlib or work with the lower-level
      palette and color-space API.

The Heri style
--------------

``heri`` is the publication preset based on the WTI APO figures. The visual
system and the palette system are independent: you can use Heri with the
built-in categorical cycle, or generate your own contrast-controlled colors.

.. raw:: html

   <div class="cc-palette-strip">
     <span style="background:#97001c;color:white">red</span>
     <span style="background:#0083f9;color:white">blue</span>
     <span style="background:#00b49c;color:#111">teal</span>
     <span style="background:#ffc600;color:#111">yellow</span>
     <span style="background:#f198ff;color:#111">pink</span>
   </div>

.. code-block:: python

   import awesomefigures as af

   af.set_style("heri", font="Arial")

   scheme = af.plot_scheme(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
       markers=["o", "s", "^", "D", "X"],
       linestyles=["-", "--", ":", "-.", (0, (5, 2))],
   )

   for y, kwargs in zip(series, scheme):
       ax.plot(x, y, **kwargs)

Explore next
------------

.. grid:: 1 2 2 3
   :gutter: 2

   .. grid-item-card:: Styles
      :link: style
      :link-type: doc

      See every available style as a rendered figure and learn how to
      personalize it.

   .. grid-item-card:: Palette mathematics
      :link: mathematics
      :link-type: doc

      Why the luminance ladder gives a constant adjacent WCAG contrast ratio.


   .. grid-item-card:: Full feature inventory
      :link: features
      :link-type: doc

      Documented Python API exports, Studio methods, notebook demos,
      TeX publication tools and workflow scripts.

   .. grid-item-card:: Automatic publication integration
      :link: automatic_publication
      :link-type: doc

      Generate TeX-font PDFs, validate embedded fonts and produce batch manifests.

   .. grid-item-card:: LaTeX publication figures
      :link: publication
      :link-type: doc

      Match the document's real column width and body font, audit labels,
      and compile a proof.

   .. grid-item-card:: Full LaTeX publication example
      :link: publication_demo
      :link-type: doc

      A two-column PDF, true PGF fonts, vector/raster plots and print/CVD
      comparisons built reproducibly on macOS.

   .. grid-item-card:: Alpha
      :link: alpha
      :link-type: doc

      Preserve apparent color when transparency and background change.

.. toctree::
   :hidden:
   :maxdepth: 2

   overview
   gallery
   notebooks/index
   studio
   accessibility
   publication
   automatic_publication
   publication_demo
   features
   customization
   quickstart
   palettes
   named_palettes
   alpha
   style
   picker
   mathematics
   color_spaces
   limitations
   examples
   api
