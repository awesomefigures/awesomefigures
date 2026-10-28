# Automatic LaTeX publication examples

The complete workflow is based on **fixed source values**. No research
experiments or numerical benchmarks are rerun.

From the repository root, with TeX Live or MiKTeX and the publication extra
installed:

```bash
python -m pip install -e ".[publication]"
python examples/automatic_publication/render.py --tex examples/automatic_publication/article.tex
python examples/automatic_publication/render.py --tex examples/automatic_publication/two_column.tex
```

The output directory contains a TeX-compiled PDF, retained PGF sources,
SVG and PNG previews, and a JSON/Markdown batch report. For a quick
non-exact PDF use `--preview`; the manifest flags those figures as previews.

**Springer Nature / SNCS:** supply the real manuscript and its
`sn-jnl.cls` and local styles:

```bash
python examples/automatic_publication/render.py --tex paper/computational-statistics-submission/sncs_main.tex
```

Run that command from a project that contains the class and manuscript,
adjusting the example script path if needed. It only demonstrates the
published API on precomputed values. The actual `trendestimation` project
must continue to load its archived model outputs; the library must never
execute estimators while regenerating figures.

A screenshot is not proof of exact fonts. Use the produced PDF manifest's
MediaBox and embedded-font fields, and inspect the final manuscript visually.

On Windows install MiKTeX and its `preview` and `pgf` packages.
On Linux install the matching TeX Live packages and journal fonts/class.
