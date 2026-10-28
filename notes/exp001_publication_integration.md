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

## Verified real-TeX result

Checked at commit `d5837b40b18e3b897996a306bdf8b01c6890ba27`:

- Python 3.10/3.12 test workflows and strict Sphinx checks passed.
- TeX Live integration: [GitHub Actions run 40742976850](https://github.com/heri-espino/awesomefigures/actions/runs/40742976850), **passed**.
- The real-PDF test generated a TeX-compiled PGF/PDF from a two-column
  article, verified PDF MediaBox insertion width and embedded font resources.
- The deterministic batch example produced four output files (two TeX PDFs,
  one SVG, one PNG), with a JSON manifest whose `all_passed` is true.
- The validation step verified that every exact PDF had nonempty embedded
  font resources. No numerical experiments were rerun.
- Generated PGF, PDF, JSON and Markdown artifacts were uploaded to the
  [exp001 CI artifact](https://github.com/heri-espino/awesomefigures/actions/runs/40742976850)
  (artifact retention 90 days). The source and reproducible checks remain
  committed in this repository.
- Full document-insertion aesthetics still require human review.
