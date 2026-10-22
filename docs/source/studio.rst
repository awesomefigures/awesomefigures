Palette & Plot Studio
=====================

The Studio is a static, interactive browser application for designing
contrast-controlled scientific figures. It runs without a server, database,
Python interpreter, or account and works with the Sphinx site on GitHub Pages.

.. raw:: html

   <p class="cc-actions">
     <a class="cc-button primary" href="_static/studio.html" target="_blank" rel="noopener">
       Open Studio in a full browser tab
     </a>
     <a class="cc-button" href="gallery.html">Explore examples</a>
   </p>

   <iframe
     id="cc-studio-frame"
     src="_static/studio.html"
     title="Interactive awesomefigures Palette and Plot Studio"
     style="width:100%;height:3200px;border:0;border-radius:12px;"
     loading="lazy"
   ></iframe>

   <script>
     window.addEventListener("message", function (event) {
       var frame = document.getElementById("cc-studio-frame");
       if (!frame || event.source !== frame.contentWindow ||
           event.origin !== window.location.origin) return;
       if (!event.data || event.data.type !== "awesomefigures-studio-height") return;
       var value = Number(event.data.height);
       if (Number.isFinite(value) && value > 400 && value < 15000) {
         frame.style.height = Math.ceil(value + 28) + "px";
       }
     });
   </script>

What you can customize
----------------------

- **Published categorical palettes**: built-in Okabe–Ito, Paul Tol Bright,
  High Contrast and Muted, Tableau 10, and ColorBrewer Set2/Dark2. Selecting
  one uses its original RGB coordinates in charts, simulations, saved JSON
  and generated Python code. Editing luminance/hue returns to the generator.
  Exact historical colours are not a WCAG ratio construction.
- **Palette**: 2 to 10 hues with equidistant, golden-angle,
  balanced-family, analogous, single-hue or manual hue methods; hue
  sliders and color pickers; OKLCH chroma and a WCAG luminance ladder.
- **Contrast presets**: automatic print-safe gray separation (default),
  balanced, strong, subtle and manual adjacent contrast ratios. Strong ratios are automatically capped if all
  selected luminance levels cannot fit within the available range.
- **Starting hue**: circular spectrum with markers, a hue slider, and a
  native color picker (which extracts the hue only; the exact picked
  RGB is not used because luminance and chroma are controlled).
- **Series identifiers**: marker and line style for each series, with
  drawn stroke patterns in the line-style picker and a visual atlas.
- **Plot gallery**: lines, time series, histograms, box plots, violins,
  ridge plots, scatter, categorical heatmaps, grouped bar charts and
  pie charts with white separators.
- **Print and color vision**: original color, ideal grayscale, degraded
  print-stress, deuteranopia, protanopia and tritanopia, with side-by-side
  palette swatches.
- **Animation**: subtle, nonessential plot and control transitions
  (automatically disabled for reduced-motion preferences).
- **Alpha**: opacity, background, and apparent-color compensation.
- **Publication style**: Heri or Matplotlib default, custom font,
  dense-artist rasterization, and output DPI.

The interactive preview is SVG generated in the browser. It is a fast visual
approximation, not the Matplotlib renderer. Color-vision previews operate on
the plotted swatch colors using approximate Machado-style linear-RGB matrices,
not on every pixel of a rendered Matplotlib figure. For publication checks
use ``awesomefigures.show_accessibility_panel(fig)``, which renders the
complete figure with Colorspacious and includes annotations/labels. The **Copy code** action generates
a complete, reproducible Python example for the selected plot family.

Saving and importing designs
----------------------------

Give the palette a valid Python identifier, such as ``paper_palette``.

- **Save locally** remembers the design in the current browser's local
  storage. Use Load or Delete to manage existing local designs.
- **Download JSON** exports the current palette, identifiers, alpha,
  style, and selected plot type. **Import JSON** brings it back on another
  browser or computer.
- **Download Python preset** creates a module that registers the named
  palette with the installed Python library.

Local saves are browser-specific, and may be cleared by browser privacy
settings. Export JSON for a portable backup.

Using an exported Python preset
-------------------------------

For example, download ``paper_palette.py`` and put it next to your plot
script, then:

.. code-block:: python

   import awesomefigures as af
   import paper_palette  # registers the preset in this process

   colors = af.color_palette("paper_palette")
   scheme = af.plot_scheme("paper_palette")

   for y, style in zip(series, scheme):
       ax.plot(x, y, **style)

You can also register the palette directly:

.. code-block:: python

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

Registration is process-local; import the exported module every time you
launch a new Python process. It does not modify the installed package files.

GitHub Pages
------------

The standalone Studio is available within the Sphinx build at
``_static/studio.html``. The interactive site requires
**Settings > Pages > Build and deployment > Source: GitHub Actions**, followed
by the repository's manual ``pages`` deployment workflow. A default Jekyll
workflow does not build the Sphinx documentation.

Palette selection guidance
--------------------------

For **unrelated categories**, start with equidistant hue angles and the
print-safe luminance setting: two or three series receive greater grayscale
separation than a five- or ten-series plot. Then check actual contrast and
grayscale distinguishability. Equal angles in OKLCH are
not equally distant perceptually or under color-vision deficiencies. A
**golden-angle** scheme can be useful when the number of categories changes.
Use **analogous** or **single-hue** methods for related or ordered data,
not large sets of unrelated categories. Color is not sufficient alone:
use the contrasting markers and line styles for line/scatter figures.

These presets are design starting points rather than certified accessible
color schemes. No hue preset guarantees distinguishability for every viewer.

Pie chart defaults
------------------

The Pie plot option previews **white wedge boundaries**, not dark outlines,
including in grayscale and the CVD simulations. Exported code calls
``af.pie_plot(...)``, which uses print-safe categorical luminances and
white separating strokes by default. You can override the edge color and
line thickness using ``wedgeprops`` when required by a journal.
