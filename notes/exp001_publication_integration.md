# exp001 — Automated manuscript publication

**Scope:** New high-level API validation, not a statistical experiment.

- Frozen figure source: `examples/automatic_publication/render.py`
  contains two fixed 10-point series.
- Input TeX cases: simple article (one column), article with
  `twocolumn`, and unit tests using a synthetic measured layout.
- Expected checks: original TeX measurement once per source hash,
  correct PDF MediaBox physical width, embedded font resource discovery,
  strict failure on bad geometry/typography, preserved backward
  compatibility, and JSON/Markdown manifest generation.
- Preview outputs must be labelled `preview-matplotlib`, never
  `exact-tex-preamble`.
- Statistical benchmarks: **not run**. Frozen numerical inputs are
  never changed by the publication library.

Run pytest and the real pdflatex CI workflow and link results in the PR.
