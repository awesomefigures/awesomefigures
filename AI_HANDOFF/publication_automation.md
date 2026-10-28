# Publication automation handoff (feature branch)

## Motivation

Downstream Trend-Estimation / SN Computer Science figures required custom
coordination of TeX layout probes, fig resizing, exact font renderer,
PDF font checks, and batch JSON manifests. Those are library concerns.

## Architecture and contracts

1. `publication.inspect_latex` remains authoritative for TeX geometry and
   nominal body size. Probe results cache by main source hash and TeX engine.
2. `latex_style` owns Matplotlib rcParams, font sizes and style restoration.
   New optional style and palette parameters preserve the legacy defaults.
3. `auto_publication.Publication` is the batch context. `subplots()`
   creates physical-size plots; `savefig()` works on existing figures only.
4. Exact PDFs retain PGF and compile a standalone figure with the original
   TeX preamble + preview package. The output MediaBox and font resources
   are checked by optional pypdf. No exact-font claim is made for previews.
5. `report()` produces a JSON/Markdown manifest with source hash,
   figure checksum, geometry, provenance and warnings.
6. `strict=True` is intended for CI; exported figures still require human
   inspection for collisions and journal compliance.

## Commands

```bash
python -m pip install -e ".[dev,docs,publication]"
python -m pytest -q
sphinx-build -W -b html docs/source docs/_build/html
python examples/automatic_publication/render.py --preview
```

For real TeX integration, use GitHub Actions
`.github/workflows/publication-integration.yml`; it installs TeX Live and
inspects a produced PDF font/resources and exact physical width.
Windows uses MiKTeX plus PGF and preview packages.

## Remaining limitations

- The probe does not compile the full manuscript body. TeX class files and
  macros may change document geometry later; figure proofs in the full
  manuscript remain advisable.
- Included .cls/.sty file changes require `clear_publication_cache()`.
- Embedded font detection depends on font resources, not a perfect semantic
  match between PDF internal names and LaTeX NFSS names.
- Some TeX sources use unusual page manipulation or shell-dependent packages;
  those are not silently worked around.
- Richness of PDF clipping/overlap checks is limited; no automated tool
  certifies aesthetic correctness.

## Experiment log

`notes/exp001_publication_integration.md` records deterministic technical
validation only. No statistical benchmark/optimization was rerun.
