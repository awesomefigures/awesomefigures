# AwesomeFigures: implemented capability inventory

The authoritative, continuously maintained list of the public Python API and
interactive/reproducibility features is:

- [Full Sphinx capability inventory](docs/source/features.rst)
- [Deployed inventory](https://heri-espino.github.io/Colors/features.html)
- [Interactive Palette & Plot Studio](https://heri-espino.github.io/Colors/studio.html)
- [Reproducible two-column LaTeX technical presentation](examples/latex_publication/README.md)

The inventory has **75 public exported names** in the current
`src/awesomefigures/__init__.py`. The test suite checks that every exported
name is documented by the catalog, so API additions cannot silently disappear
from the feature list.

This is a capability inventory, not a claim that every plot demonstrated
in the notebooks was implemented as a new plot primitive. Most are
Matplotlib graphics combined with `awesomefigures` styling and diagnostics.
