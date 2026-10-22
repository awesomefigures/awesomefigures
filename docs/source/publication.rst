LaTeX publication fit
=====================

Prepare a Matplotlib figure at its **real insertion size** instead of
guessing fonts from pixels or rescaling it repeatedly.

The workflow has four steps: measure the LaTeX template, create the figure
at the final physical width, audit it, and optionally compile an insertion
proof. Use only trusted LaTeX sources; the probe compiles the preamble with
shell escape disabled.

Measure the actual manuscript
-----------------------------

Install a LaTeX engine (TeX Live, MiKTeX or MacTeX), then run:

.. code-block:: python

   import awesomefigures as af

   layout = af.inspect_latex("paper/main.tex", engine="pdflatex")
   print(layout.columnwidth_pt)
   print(layout.textwidth_pt)
   print(layout.fontsize_pt)
   print(layout.font_family)

The probe uses a temporary source containing the manuscript preamble and
a very short document body. It measures the sizes *after* class/package
initialization, without editing the original manuscript.

If TeX is unavailable but your journal specifies the dimensions:

.. code-block:: python

   layout = af.LatexLayout.from_dimensions(
       columnwidth_pt=245.0,
       textwidth_pt=510.0,
       fontsize_pt=10.0,
   )

Those are illustrative values, **not universal journal dimensions**.

Create at column or text width
------------------------------

.. code-block:: python

   import numpy as np
   import awesomefigures as af

   with af.latex_style("paper/main.tex", width="column") as pub:
       fig, ax = pub.subplots(height_ratio=0.65)
       x = np.linspace(0, 10, 160)
       ax.plot(x, np.sin(x))
       ax.set_xlabel("Time")
       ax.set_ylabel("Response")
       report = pub.audit(fig)
       print(report.passed, report.warnings)
       pub.savefig(fig, "paper/figures/signal.pdf")

The generated PDF has the same width as your column. Axis labels use
the nominal body font size; ticks and legends default to 80% of that size.
For a figure across both columns use width="text" instead.

.. code-block:: latex

   \begin{figure}
     \centering
     \includegraphics{figures/signal.pdf}
     \caption{Example figure.}
   \end{figure}

**Do not resize this PDF again in includegraphics** unless you intend a
different effective font size. The output uses bbox_inches=None; automatically
tight-cropping a PDF would change its physical insertion dimensions.


Find or reuse the actual LaTeX font
-----------------------------------

A font used by LaTeX may be installed in TeX Live or MiKTeX without appearing
in the Windows font manager. You do not need to download it again.

.. code-block:: python

   import awesomefigures as af

   font = af.find_latex_font("paper/main.tex", engine="pdflatex")
   print(font.family_code, font.tex_font_name)
   print(font.outline_path, font.metrics_path)
   print(font.source)

This uses the TeX installation's own file search (kpsewhich). Some TeX font
names resolve only to a TFM file: **TFM contains metrics, not the glyph
outlines**. In particular, a Type 1 font may use separate PFB outlines,
virtual fonts and encodings. The diagnostic neither copies nor downloads fonts.

**To guarantee the same typesetting as your paper, use native PGF:**

.. code-block:: python

   with af.latex_style("paper/main.tex", engine="pdflatex") as pub:
       fig, ax = pub.subplots()
       ax.plot([0, 1, 2], [1, 3, 2])
       ax.set_xlabel("Time")
       pub.savefig(fig, "paper/figures/curve.pgf")

And include it in the original LaTeX manuscript:

.. code-block:: latex

   \begin{figure}
     \centering
     \input{figures/curve.pgf}
     \caption{The manuscript typesets the figure text.}
   \end{figure}

Make sure the pgf package is loaded in LaTeX. PGF drawing commands take
their typographic fonts from the document itself, even when those fonts
are not registered in Windows. The backend is set to use the selected
document engine with pgf.rcfonts=False.

If Matplotlib exports auxiliary PNG files for rasterized plot elements,
keep those alongside the PGF and resolve their paths with the LaTeX import
package if needed.

**Limits:** only the PGF as typeset inside the original manuscript is
guaranteed to use that manuscript's font setup. The Matplotlib preview
and a separately created PDF may still use a substitute. TeX font metrics
and style-specific text positions may require checking the finished PDF.

Adjust an existing Matplotlib figure
------------------------------------

.. code-block:: python

   layout = af.inspect_latex("paper/main.tex")
   result = af.fit_figure_to_latex(fig, layout, width="column")
   print(result.passed, result.audit.warnings)
   af.save_figure(fig, "fitted.pdf", bbox_inches=None, pad_inches=0)

The fitter adjusts width and text hierarchy, runs tight_layout where
applicable, and may increase figure height if clipping persists. It has a
bounded number of iterations: unresolved problems are reported rather than
silently hidden. It cannot infer the scientific importance of an overlap.

Compile a proof PDF
-------------------

.. code-block:: python

   af.verify_latex_placement(
       "paper/main.tex",
       "paper/figures/signal.pdf",
       proof_pdf="paper/figures/signal_proof.pdf",
   )

This compiles a **separate minimal document** with your template preamble
and an *unscaled* copy of the PDF, comparing the physical PDF width against
the measured column width (default tolerance: 0.75 TeX points). The proof
also shows normal document text for a typography comparison. For a wide
two-column figure use width="text".
It does not validate the final position of a float inside the manuscript.

Matching the actual font glyphs
-------------------------------

Matching 10 pt in both LaTeX and Matplotlib does not necessarily mean both
use the *same* Times/Utopia/Computer Modern outlines. The automatic font
choice is a serif/sans-serif approximation. For true document-owned TeX fonts
and math typesetting, export a PGF file:

.. code-block:: python

   with af.latex_style("paper/main.tex", width="column") as pub:
       fig, ax = pub.subplots()
       ax.plot([0, 1, 2], [2, 3, 1])
       pub.savefig(fig, "paper/figures/curve.pgf")

.. code-block:: latex

   \begin{figure}
     \centering
     \input{figures/curve.pgf}
     \caption{Figure text typeset by LaTeX.}
   \end{figure}

A working TeX installation is required for PGF and some nonstandard math/font
settings may need additional configuration.

What the audit checks
---------------------

- Width mismatch against the actual TeX column or text width.
- Smallest rendered point size at that insertion scale.
- Smallest line thickness at that insertion scale.
- Matplotlib text that extends beyond the figure canvas.

It does *not* certify colorblind accessibility, scientific clarity,
legend overlap quality, or journal compliance. Use
:doc:`accessibility` for grayscale and CVD diagnostics.

See :doc:`api` for inspect_latex, LatexLayout, latex_style,
PublicationStyle, fit_figure_to_latex, FigureAudit and verify_latex_placement.
