#!/usr/bin/env bash
# A single macOS command to build the full LaTeX publication demonstration.
set -Eeuo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$HERE/generated"
COMMIT=0
PUSH=0
OPEN=0

while (($#)); do
  case "$1" in
    --commit) COMMIT=1 ;;
    --push) COMMIT=1; PUSH=1 ;;
    --open) OPEN=1 ;;
    --help|-h)
      echo "Usage: ./examples/latex_publication/run_macos.sh [--commit] [--push] [--open]"
      echo "  --commit  Commit the manuscript, three figure PDFs and three web PNG previews"
      echo "  --push    Also push those seven results to the current branch"
      echo "  --open    Open the final manuscript PDF in Preview"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

# MacTeX provides TeX here, even when the terminal has not picked it up.
if [[ -d /Library/TeX/texbin ]]; then
  export PATH="/Library/TeX/texbin:$PATH"
fi

for program in pdflatex kpsewhich; do
  if ! command -v "$program" >/dev/null 2>&1; then
    echo "Missing $program: install MacTeX or add your TeX installation to PATH." >&2
    exit 1
  fi
done

for package in lmodern.sty pgf.sty tikz.sty titlesec.sty fancyhdr.sty microtype.sty graphicx.sty booktabs.sty tabularx.sty hyperref.sty; do
  if ! kpsewhich "$package" >/dev/null 2>&1; then
    echo "Your TeX installation lacks $package. Install that TeX package first." >&2
    exit 1
  fi
done

if command -v conda >/dev/null 2>&1; then
  if ! conda run -n awesomefigures python -c "import sys" >/dev/null 2>&1; then
    echo "Creating the awesomefigures Conda environment..."
    conda env create --name awesomefigures --file "$ROOT/environment.yml"
  fi
  PY=(conda run --no-capture-output -n awesomefigures python)
else
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3.10+ or Miniforge is required." >&2
    exit 1
  fi
  echo "Conda not found: using a local Python virtual environment."
  python3 -m venv "$ROOT/.venv"
  PY=("$ROOT/.venv/bin/python")
fi

cd "$ROOT"
echo "Installing the library and publication tests..."
"${PY[@]}" -m pip install -e ".[dev]"
echo "Testing the publication API..."
"${PY[@]}" -m pytest \
  tests/test_publication.py \
  tests/test_publication_fonts.py \
  tests/test_publication_example.py \
  tests/test_accessibility.py

echo "Generating TeX-native PGF, vector PDF, hybrid scatter and accessibility panel..."
"${PY[@]}" "$HERE/generate.py" --tex "$HERE/main.tex" --output "$OUT"

echo "Compiling the complete two-column manuscript..."
mkdir -p "$OUT"
if command -v latexmk >/dev/null 2>&1; then
  (cd "$HERE" && latexmk -pdf -interaction=nonstopmode -halt-on-error \
      -file-line-error -outdir=generated main.tex)
else
  (cd "$HERE" && pdflatex -interaction=nonstopmode -halt-on-error \
      -output-directory=generated main.tex >/dev/null)
  (cd "$HERE" && pdflatex -interaction=nonstopmode -halt-on-error \
      -output-directory=generated main.tex >/dev/null)
fi

if [[ ! -s "$OUT/main.pdf" ]]; then
  echo "Compilation did not create $OUT/main.pdf" >&2
  exit 1
fi
PDF="$OUT/main.pdf"

# Only published deliverables are copied into the Sphinx static directory.
cp "$OUT/main.pdf" "$ROOT/docs/source/_static/publication_demo.pdf"
cp "$OUT/accessibility.png" "$ROOT/docs/source/_static/publication_accessibility.png"
cp "$OUT/accessibility.pdf" "$ROOT/docs/source/_static/publication_accessibility.pdf"
cp "$OUT/groups_accessibility.png" "$ROOT/docs/source/_static/publication_scatter_accessibility.png"
cp "$OUT/groups_accessibility.pdf" "$ROOT/docs/source/_static/publication_scatter_accessibility.pdf"
cp "$OUT/palette_grid.pdf" "$ROOT/docs/source/_static/publication_palette_grid.pdf"
cp "$OUT/palette_grid.png" "$ROOT/docs/source/_static/publication_palette_grid.png"

echo
echo "COMPLETE"
echo "  Manuscript: $OUT/main.pdf"
echo "  Font and physical-size report: $OUT/report.json"
if command -v pdffonts >/dev/null 2>&1; then
  pdffonts "$PDF" > "$OUT/embedded_fonts.txt"
  echo "  Embedded PDF font report: $OUT/embedded_fonts.txt"
  cat "$OUT/embedded_fonts.txt"
fi
echo "  Web-ready PDF: docs/source/_static/publication_demo.pdf"
echo "  Web-ready vector PDF: docs/source/_static/publication_accessibility.pdf"
echo "                         docs/source/_static/publication_scatter_accessibility.pdf"
echo "                         docs/source/_static/publication_palette_grid.pdf"
echo "  Web-ready accessibility images: docs/source/_static/publication_accessibility.png"
echo "                                docs/source/_static/publication_scatter_accessibility.png"
echo "                                docs/source/_static/publication_palette_grid.png"
echo "Nothing is committed or pushed unless explicitly requested."

if ((COMMIT)); then
  if ! command -v git >/dev/null 2>&1; then
    echo "Git is required for --commit/--push." >&2
    exit 1
  fi
  git add -- docs/source/_static/publication_demo.pdf \
    docs/source/_static/publication_accessibility.png \
    docs/source/_static/publication_scatter_accessibility.png \
    docs/source/_static/publication_accessibility.pdf \
    docs/source/_static/publication_scatter_accessibility.pdf \
    docs/source/_static/publication_palette_grid.pdf \
    docs/source/_static/publication_palette_grid.png
  if ! git diff --cached --quiet -- \
    docs/source/_static/publication_demo.pdf \
    docs/source/_static/publication_accessibility.png \
    docs/source/_static/publication_scatter_accessibility.png \
    docs/source/_static/publication_accessibility.pdf \
    docs/source/_static/publication_scatter_accessibility.pdf \
    docs/source/_static/publication_palette_grid.pdf \
    docs/source/_static/publication_palette_grid.png; then
    git commit -m "Publish LaTeX font and accessibility demonstration" -- \
      docs/source/_static/publication_demo.pdf \
      docs/source/_static/publication_accessibility.png \
      docs/source/_static/publication_scatter_accessibility.png \
      docs/source/_static/publication_accessibility.pdf \
      docs/source/_static/publication_scatter_accessibility.pdf \
      docs/source/_static/publication_palette_grid.pdf \
      docs/source/_static/publication_palette_grid.png
  else
    echo "The published results are unchanged."
  fi
  if ((PUSH)); then git push; fi
fi

if ((OPEN)) && command -v open >/dev/null 2>&1; then
  open "$OUT/main.pdf"
fi
