Automatic manuscript publication
================================

AwesomeFigures can measure a trusted LaTeX document once and generate
publication-ready figures without manual PGF or backend configuration.
The new :func:`awesomefigures.publication` workflow extends the existing
:func:`awesomefigures.inspect_latex`, :func:`awesomefigures.latex_style`
and :class:`awesomefigures.PublicationStyle` APIs, which remain supported.

Quick start
-----------

.. code-block:: python

   import awesomefigures as af

   with af.paper("paper/main.tex", style="elegante",
                       palette="okabe-ito", strict=True) as pub:
       fig, ax = pub.subplots()
       ax.plot(saved_x, saved_y, label="Trend")
       ax.set(xlabel="Time", ylabel="Value")
       pub.savefig(fig, "paper/figures/trend.pdf")
       pub.report("paper/figures/publication_manifest.json")

The plotting data are **already computed**. This API never runs a model
fit, numerical search, regression, or simulation. The default PDF export
produces a PGF source plus a PDF compiled with the **actual trusted
manuscript preamble**, then audits physical dimensions and embedded fonts.
Do not scale it again with LaTeX includegraphics: that would shrink the
printed text sizes.

Widths and readability
----------------------

Available width specifications include ``column`` (measured columnwidth),
``text`` and ``full`` (measured textwidth), positive inches, or a LaTeX
fraction such as ``r"0.85\textwidth"``. Measurements are obtained by
compiling the document's real preamble, not by reading textual class options
or guessing the column count.

Body labels default to the nominal manuscript point size. Legends and ticks
use 80%, with an independent configurable ``minimum_text_pt`` and
``minimum_line_pt`` checked against final printed dimensions. Layout
inspection cannot certify perfect visual spacing.

Multi-panel and two-column figures
----------------------------------

.. code-block:: python

   with af.paper("paper/main.tex", width="full",
                       palette="tol-bright") as pub:
       fig, axes = pub.subplots(2, 2, height_ratio=0.60)
       for ax, series in zip(axes.flat, archived_series):
           ax.plot(archived_time, series)
       pub.savefig(fig, "paper/figures/multipanel.pdf", width="text")
       pub.savefig(fig, "paper/figures/multipanel.svg", width="text")
       pub.report("paper/figures/manifest.json")

For a two-column article, a figure with width ``column`` uses the measured
column width; ``text`` spans both columns, preserving the original text
sizes rather than relying on downstream resizing.

PDF versus preview
------------------

The default for PDF is ``exact=True``. This calls a real TeX engine with
the manuscript preamble and compiles the generated PGF, then examines PDF
MediaBox geometry and embedded fonts through optional ``pypdf``.
If exact TeX is unavailable, it **raises** an actionable error; it does
not silently substitute another font.

SVG/PNG are fast non-exact previews, and ``exact=False`` explicitly
permits a Matplotlib preview PDF. The JSON manifest records either
``exact-tex-preamble`` or ``preview-matplotlib``.

.. code-block:: python

   with af.paper("paper/main.tex") as pub:
       fig, ax = pub.subplots()
       ax.plot(saved_x, saved_y)
       pub.savefig(fig, "paper/figures/preview.svg")
       pub.savefig(fig, "paper/figures/preview.png")
       pub.savefig(fig, "paper/figures/draft.pdf", exact=False)

The exact PDF requires a trusted manuscript path, not merely a guessed
or manually supplied LatexLayout. The same font family name in Matplotlib
is **not** proof of matching TeX glyphs.

Windows with MiKTeX / Linux with TeX Live
-----------------------------------------

.. code-block:: bash

   python -m pip install -e ".[publication]"

* Windows: install MiKTeX and its PGF/preview packages. Ensure pdflatex
  is on PATH. Perl may be managed inside an activated Conda environment,
  if latexmk is used separately.
* Linux: install TeX Live, fonts, PGF, preview.sty, and any journal class
  files. The TeX engine must be on PATH.
* Springer Nature SNCS: use the real ``sncs_main.tex``, local
  ``sn-jnl.cls`` and included styles. The probe executes its actual class
  setup; it never assumes the document is single-column or two-column.

Only trusted TeX source should be passed: the preamble is executed (with
shell escape disabled). Missing packages/classes produce diagnostic TeX
log lines. Preview is not exact TeX typography.

Batch output and caching
------------------------

One context measures the manuscript once, and exports every already-plotted
figure using the same style, palette, dimensions and font hierarchy.
Call ``pub.report("figures/manifest.json")`` to save a JSON manifest
and Markdown report for CI and manuscript review. Records include source
hash, exported PDF SHA256, physical width, embedded font names, text
audits, backend, and warnings.

A changed main TeX file invalidates the inspection cache automatically.
If imported .cls/.sty files change independently, call
:func:`awesomefigures.clear_publication_cache`. PDF metadata and
uninspected external resources may have non-reproducible properties;
archive frozen results and rendered outputs in the Git repository.

Migration from existing plotting code
-------------------------------------

The former low-level workflow remains valid:

.. code-block:: python

   with af.latex_style("paper/main.tex", width="column") as old:
       fig, ax = old.subplots()
       old.savefig(fig, "figures/old.pdf")

The new workflow configures the document once, adds automatic
TeX-backed PDF compilation and reports:

.. code-block:: python

   with af.paper("paper/main.tex", strict=True) as pub:
       fig, ax = pub.subplots()
       pub.savefig(fig, "figures/new.pdf")
       pub.report("figures/report.json")

For an existing Matplotlib figure use ``pub.savefig(fig, ...)`` directly:
it fits the figure to the intended width without re-running the
upstream numerical experiment. Check intentionally customized font sizes
and final visual placement before publication.

Limits and strict mode
----------------------

``strict=True`` raises on observed small labels, thin lines, clipped
text where detectable, mismatched exported PDF dimensions and failures
to embed font resources. It is suitable for CI, but cannot guarantee
no overlapping labels, publisher compliance, or mathematical correctness.
Only the TeX-compiled PDF is labelled as exact; previews are explicitly
labelled approximate.

API reference
-------------

See :doc:`api` for the complete documented interface.
