"""Static tests for the macOS publication showcase sources."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "latex_publication"


def test_manuscript_has_all_demo_graphics():
    assert all((DEMO / name).is_file() for name in (
        "main.tex", "generate.py", "run_macos.sh", "README.md"))
    tex = (DEMO / "main.tex").read_text(encoding="utf-8")
    assert r"\documentclass[10pt,twocolumn,a4paper]{article}" in tex
    assert r"\begin{titlepage}" in tex
    assert r"\input{generated/cover_palette.tex}" in tex
    assert r"\onecolumn" in tex and r"\twocolumn" in tex
    assert r"\pagecolor{CoverInk}" in tex
    assert r"\usepackage{tikz}" in tex
    assert r"\usepackage{titlesec}" in tex
    assert r"\usepackage{fancyhdr}" in tex
    assert r"\usepackage{lmodern}" in tex
    assert r"\input{generated/lines.pgf}" in tex
    assert r"\includegraphics{generated/lines.pdf}" in tex
    assert r"\includegraphics{generated/dense.pdf}" in tex
    assert r"\input{generated/groups.pgf}" in tex
    assert r"\input{generated/palette_grid.pgf}" in tex
    assert "https://heri-espino.github.io/Colors/studio.html" in tex
    assert "WCAG" in tex and "OKLCH" in tex
    assert r"\input{generated/groups_accessibility.pgf}" in tex
    assert r"\input{generated/accessibility.pgf}" in tex
    assert "pie.pdf" not in tex
    assert r"\section{Categorical pie-chart boundaries}" not in tex
    assert r"\begin{figure*}[p]" in tex
    assert r"\begin{figure*}[t]" in tex
    assert r"\clearpage" in tex
    assert r"\end{document}" in tex


def test_generated_graphics_use_public_apis():
    script = (DEMO / "generate.py").read_text(encoding="utf-8")
    for part in (
        "af.inspect_latex(", "af.find_latex_font(", "af.latex_style(",
        "af.show_vector_accessibility_panel(",
        "af.verify_latex_placement(",
    ):
        assert part in script
    assert "np.random.default_rng(20261007)" in script
    assert "lines.pgf" in script
    assert "lines.pdf" in script
    assert "pie.pdf" not in script
    assert "af.pie_plot(" not in script
    assert "groups.pgf" in script
    assert "af.contrast_grid(" in script
    assert '"palette_grid.pdf"' in script
    assert '"palette_grid.pgf"' in script
    assert 'edgecolors="white"' in script
    assert "match_manuscript_axes(ax, layout.fontsize_pt)" in script
    assert "ncols=3" in script and "ncols=2" in script
    assert "accessibility.pdf" in script
    assert "accessibility.pgf" in script
    assert "groups_accessibility.pdf" in script
    assert "groups_accessibility.pgf" in script
    assert 'b"/Subtype /Image"' in script
    assert 'linewidths=0.22' in script
    assert 'alpha=0.68' in script
    assert '#E69F00' in script and '#0072B2' in script and '#009E73' in script


def test_cover_palette_is_generated_from_real_contrast_grid(tmp_path):
    import runpy
    # Import the generator without triggering full TeX compilation.
    namespace = runpy.run_path(str(DEMO / "generate.py"))
    grid = namespace["write_cover_palette"](tmp_path / "cover_palette.tex")
    content = (tmp_path / "cover_palette.tex").read_text(encoding="utf-8")
    assert grid.shape == (5, 6)
    assert content.count(r"\definecolor{CoverCell") == 30
    assert content.count(r"\fill[CoverCell") == 30
    assert r"\begin{tikzpicture}" in content
    assert r"\end{tikzpicture}" in content
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            assert (
                rf"\definecolor{{CoverCell{i}{j}}}"
                rf"{{HTML}}{{{cell.hex.lstrip('#')}}}"
            ) in content


def test_builder_only_pushes_after_opt_in():
    sh = (DEMO / "run_macos.sh").read_text(encoding="utf-8")
    assert "set -Eeuo pipefail" in sh
    assert "publication_demo.pdf" in sh
    assert "publication_accessibility.png" in sh
    assert "publication_scatter_accessibility.png" in sh
    assert "publication_accessibility.pdf" in sh
    assert "publication_scatter_accessibility.pdf" in sh
    assert "publication_palette_grid.pdf" in sh
    assert "publication_palette_grid.png" in sh
    assert "if ((COMMIT)); then" in sh
    assert "if ((PUSH)); then git push; fi" in sh


def test_site_navigation_and_ignore_rules():
    page = (ROOT / "docs/source/publication_demo.rst").read_text(encoding="utf-8")
    index = (ROOT / "docs/source/index.rst").read_text(encoding="utf-8")
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "_static/publication_demo.pdf" in page
    assert "_static/publication_accessibility.png" in page
    assert "_static/publication_accessibility.pdf" in page
    assert "_static/publication_palette_grid.pdf" in page
    assert "   publication_demo" in index
    assert "examples/latex_publication/generated/" in ignore


def test_demo_python_and_bash_have_valid_syntax():
    import shutil
    import subprocess

    generator = DEMO / "generate.py"
    compile(generator.read_text(encoding="utf-8"), str(generator), "exec")
    bash = shutil.which("bash")
    if bash:
        subprocess.run([bash, "-n", str(DEMO / "run_macos.sh")], check=True)
