import numpy as np

from awesomefigures import contrast_grid


def test_every_column_hits_row_luminance():
    grid = contrast_grid(
        levels=5,
        hues=[50, 15, 145, 210, 290],
        ratio=1.4,
        start_luminance=0.9,
    )
    for i, row in enumerate(grid):
        for cell in row:
            assert abs(cell.actual_luminance - grid.luminances[i]) < 2e-9


def test_any_one_per_row_keeps_constant_contrast():
    grid = contrast_grid(
        levels=5,
        hues=[50, 15, 145, 210, 290],
        ratio=1.4,
        start_luminance=0.9,
    )
    palette = grid.select([4, 1, 3, 0, 2])
    np.testing.assert_allclose(palette.adjacent_contrast, 1.4, atol=2e-8)


def test_diagonal_palette_has_expected_size():
    grid = contrast_grid(levels=4, hues=[20, 120, 240], ratio=1.3)
    assert len(grid.diagonal()) == 4


def test_contrast_grid_hex_text_uses_higher_contrast_foreground():
    import matplotlib.pyplot as plt
    import awesomefigures as cc

    grid = cc.contrast_grid(
        levels=3, hues=[25, 115, 205, 295],
        ratio=1.55, start_luminance=.65, chroma=.12,
    )
    fig, ax = plt.subplots()
    grid.plot(ax=ax, annotate=True)
    assert len(ax.texts) == len(ax.patches) == 12
    for patch, label in zip(ax.patches, ax.texts):
        background = patch.get_facecolor()[:3]
        ratio = cc.contrast_ratio(background, label.get_color())
        assert ratio >= 4.5, f"Hex label contrast too weak: {ratio}"
    assert all(label.get_text().startswith(r"$\#$") for label in ax.texts)
    plt.close(fig)


def test_contrast_grid_hex_labels_compile_in_native_pgf(tmp_path):
    """Regression: bare #RRGGBB used to halt TeX inside backend_pgf."""
    import shutil
    import subprocess
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import pytest

    grid = contrast_grid(levels=3, hues=[25, 115, 205, 295],
                         ratio=1.55, start_luminance=.65, chroma=.12)
    fig, ax = plt.subplots(figsize=(6, 2.6))
    grid.plot(ax=ax, annotate=True)
    assert all(label.get_text().startswith(r"$\#$") for label in ax.texts)
    if shutil.which("pdflatex") is None:
        plt.close(fig)
        pytest.skip("pdflatex is not installed")
    pgf = tmp_path / "palette_grid.pgf"
    with mpl.rc_context({"pgf.texsystem": "pdflatex", "pgf.rcfonts": False}):
        fig.savefig(pgf, format="pgf", bbox_inches=None)
    plt.close(fig)
    tex = tmp_path / "proof.tex"
    tex.write_text(
        r"\documentclass{article}" + "\n"
        r"\usepackage{pgf}" + "\n"
        r"\begin{document}" + "\n"
        r"\input{palette_grid.pgf}" + "\n"
        r"\end{document}" + "\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
        cwd=tmp_path, check=True, timeout=60, capture_output=True, text=True,
    )
    assert (tmp_path / "proof.pdf").stat().st_size > 100
