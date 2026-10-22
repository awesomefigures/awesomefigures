"""Publication-mode figure sizing and LaTeX probe unit tests."""
from __future__ import annotations

import math
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

import awesomefigures as af
import awesomefigures.publication as pub


@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")


@pytest.fixture
def layout():
    return af.LatexLayout.from_dimensions(
        columnwidth_pt=240.0,
        textwidth_pt=500.0,
        fontsize_pt=10.0,
        baselineskip_pt=12.0,
        font_family="ptm",
    )


def test_dimensions_and_pt_to_inch(layout):
    assert math.isclose(layout.width_inches("column"), 240 / 72.27)
    assert math.isclose(layout.width_inches("text"), 500 / 72.27)
    assert layout.width_pt("page") == 500.0
    assert layout.width_pt(3.0) == pytest.approx(3 * 72.27)
    with pytest.raises(ValueError):
        layout.width_inches("bad")
    with pytest.raises(ValueError):
        layout.width_inches(0)
    with pytest.raises(ValueError):
        af.LatexLayout.from_dimensions(
            columnwidth_pt=550, textwidth_pt=300, fontsize_pt=10
        )


def test_probe_parses_pt_and_font_identity():
    log = "\n".join([
        "CCLAYOUT:COLUMN=242.315pt",
        "CCLAYOUT:TEXT=510.123pt",
        "CCLAYOUT:FONT=10 pt",
        "CCLAYOUT:BASELINE=12.0pt",
        "CCLAYOUT:FAMILY=ppl",
        "CCLAYOUT:FONTNAME=pplr7t at 10.0pt",
    ])
    layout = pub._parse_layout_log(log)
    assert layout.columnwidth_pt == pytest.approx(242.315)
    assert layout.textwidth_pt == pytest.approx(510.123)
    assert layout.fontsize_pt == 10
    assert layout.baselineskip_pt == 12
    assert layout.font_family == "ppl"
    with pytest.raises(af.LatexProbeError):
        pub._parse_layout_log("No measurements")


def test_preamble_probe_does_not_compile_paper_body(monkeypatch, tmp_path):
    tex = tmp_path / "main.tex"
    tex.write_text(
        "\\documentclass[twocolumn]{article}\n"
        "% \\begin{document} (not the real begin document)\n"
        "\\usepackage{amsmath}\n"
        "\\begin{document}\n"
        "THE PRIVATE MANUSCRIPT BODY MUST NOT BE COMPILED\n"
        "\\end{document}\n", encoding="utf-8"
    )
    calls = []

    def fake_run(source, *, source_dir, engine, timeout, output_pdf=None):
        calls.append((source, source_dir, engine, timeout))
        return (
            "CCLAYOUT:COLUMN=240.0pt\nCCLAYOUT:TEXT=500.0pt\n"
            "CCLAYOUT:FONT=10 pt\nCCLAYOUT:BASELINE=12 pt\n"
            "CCLAYOUT:FAMILY=cmr\n"
        )
    monkeypatch.setattr(pub, "_run_tex", fake_run)
    layout = af.inspect_latex(tex)
    assert layout.fontsize_pt == 10
    assert "THE PRIVATE MANUSCRIPT BODY" not in calls[0][0]
    assert r"\usepackage{amsmath}" in calls[0][0]
    assert calls[0][1] == tmp_path
    assert calls[0][2] == "pdflatex"


def test_latex_style_sets_real_font_and_width(layout, tmp_path):
    before = mpl.rcParams.copy()
    with af.latex_style(layout, width="column") as publication:
        assert mpl.rcParams["font.size"] == 10
        assert mpl.rcParams["axes.labelsize"] == 10
        assert mpl.rcParams["xtick.labelsize"] == 8
        fig, ax = publication.subplots()
        ax.plot([0, 1, 2], [3, 4, 2])
        ax.set(xlabel="Time", ylabel="Price")
        assert fig.get_size_inches()[0] == pytest.approx(layout.width_inches())
        audit = publication.audit(fig)
        assert audit.passed, audit.warnings
        assert ax.xaxis.label.get_fontsize() == 10
        path = publication.savefig(fig, tmp_path / "publication.pdf")
        assert path.exists() and path.stat().st_size > 500
        assert "MediaBox" in path.read_bytes().decode("latin-1", "ignore")
    assert mpl.rcParams["font.size"] == before["font.size"]


def test_existing_figure_fit_does_not_compound_font_scaling(layout):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("Time", fontsize=12)
    start_fontsize = ax.xaxis.label.get_fontsize()
    result = af.fit_figure_to_latex(
        fig, layout, reference_fontsize_pt=10, max_iterations=3
    )
    assert fig.get_size_inches()[0] == pytest.approx(layout.width_inches())
    assert ax.xaxis.label.get_fontsize() == pytest.approx(12)
    assert result.iterations <= 3
    result2 = af.fit_figure_to_latex(
        fig, layout, reference_fontsize_pt=10, max_iterations=3
    )
    assert result2.iterations <= 3
    assert ax.xaxis.label.get_fontsize() == pytest.approx(12)
    assert start_fontsize == 12


def test_width_and_readability_audit_fail_on_undersized_figure(layout):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([0, 1], [1, 2], linewidth=0.1)
    ax.set_xlabel("x")
    report = af.audit_figure(fig, layout)
    assert not report.passed
    assert any("width" in issue for issue in report.warnings)
    assert any("line" in issue for issue in report.warnings)


def test_latex_proof_requires_pdf(monkeypatch, tmp_path):
    tex = tmp_path / "paper.tex"
    tex.write_text("\\documentclass{article}\n\\begin{document}\nA\n", encoding="utf-8")
    graphic = tmp_path / "panel.pdf"
    graphic.write_bytes(b"%PDF-1.4\n")

    def fake_run(source, *, source_dir, engine, timeout, output_pdf=None):
        assert r"\usepackage{graphicx}" in source
        assert r"\includegraphics[width=\columnwidth]" not in source
        assert r"\typeout{CCLAYOUT:FIGURE=\the\wd\ccfigurebox}" in source
        assert str(graphic.resolve().as_posix()) in source
        return ("CCLAYOUT:COLUMN=250pt\nCCLAYOUT:TEXT=500pt\n"
                "CCLAYOUT:FONT=10pt\nCCLAYOUT:FIGURE=250pt\n")
    monkeypatch.setattr(pub, "_run_tex", fake_run)
    result = af.verify_latex_placement(tex, graphic)
    assert result.columnwidth_pt == 250
    with pytest.raises(ValueError):
        af.verify_latex_placement(tex, tmp_path / "not_a_pdf.png")


def test_exact_source_contains_no_body_and_engine_validation(tmp_path):
    source = r"\documentclass{article}" + "\n" + (
        r"\begin{document}" + "\nHello" + "\n" + r"\end{document}"
    )
    preamble = pub._latex_preamble(source)
    assert "Hello" not in preamble
    assert r"\documentclass" in preamble
    with pytest.raises(ValueError):
        pub._run_tex(source, source_dir=tmp_path, engine="bad", timeout=5)


def test_optional_real_latex_probe_when_installed(tmp_path):
    import shutil
    if shutil.which("pdflatex") is None:
        pytest.skip("pdflatex is not installed in CI")
    tex = tmp_path / "min.tex"
    tex.write_text(
        "\\documentclass[10pt,twocolumn]{article}\n"
        "\\begin{document}\nThis body is not needed.\n\\end{document}\n",
        encoding="utf-8",
    )
    actual = af.inspect_latex(tex, timeout=30)
    assert actual.fontsize_pt == pytest.approx(10.0)
    assert actual.columnwidth_pt < actual.textwidth_pt


def test_latex_proof_checks_real_unscaled_width(monkeypatch, tmp_path):
    tex = tmp_path / "paper.tex"
    tex.write_text(r"\documentclass{article}" + "\n" + r"\begin{document}")
    pdf = tmp_path / "fig.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    def wrong(source, *, source_dir, engine, timeout, output_pdf=None):
        return ("CCLAYOUT:COLUMN=250pt\nCCLAYOUT:TEXT=500pt\n"
                "CCLAYOUT:FONT=10pt\nCCLAYOUT:FIGURE=245pt\n")
    monkeypatch.setattr(pub, "_run_tex", wrong)
    with pytest.raises(af.LatexProbeError, match="Figure has width"):
        af.verify_latex_placement(tex, pdf)
    def right(source, *, source_dir, engine, timeout, output_pdf=None):
        assert r"\onecolumn" in source
        return ("CCLAYOUT:COLUMN=250pt\nCCLAYOUT:TEXT=500pt\n"
                "CCLAYOUT:FONT=10pt\nCCLAYOUT:FIGURE=500pt\n")
    monkeypatch.setattr(pub, "_run_tex", right)
    layout = af.verify_latex_placement(tex, pdf, width="text")
    assert layout.textwidth_pt == 500


def test_pdf_and_svg_keep_exact_latex_width_with_heri_tight_default(layout, tmp_path):
    """Regression: a publication PDF must not inherit savefig.bbox='tight'.

    A tight crop passed the artist audit but shortened the exported PDF
    from 217.69 TeX pt to 211.67 TeX pt on macOS, breaking LaTeX placement.
    PDF uses 72 PostScript points/in, whereas TeX measures 72.27 pt/in.
    """
    with af.latex_style(layout, width="column") as publication:
        assert mpl.rcParams["savefig.bbox"] == "tight"
        fig, ax = publication.subplots(height_ratio=0.8)
        ax.plot([0, 1, 2], [1, 3, 2])
        ax.set(xlabel="Time", ylabel="Response")
        pdf = publication.savefig(fig, tmp_path / "exact.pdf", audit=False)
        svg = publication.savefig(fig, tmp_path / "exact.svg", audit=False)
        import re
        match = re.search(
            rb"/MediaBox\s*\[\s*([0-9.]+)\s+([0-9.]+)\s+"
            rb"([0-9.]+)\s+([0-9.]+)\s*\]",
            pdf.read_bytes(),
        )
        assert match is not None, "PDF did not contain a readable MediaBox"
        pdf_width = float(match.group(3)) - float(match.group(1))
        expected_pdf_points = layout.width_inches("column") * 72.0
        assert pdf_width == pytest.approx(expected_pdf_points, abs=0.03)
        svg_tag = re.search(r"<svg\b[^>]+>", svg.read_text(encoding="utf-8"))
        assert svg_tag is not None
        width_match = re.search(r'\bwidth="([0-9.]+)pt"', svg_tag.group(0))
        assert width_match is not None
        assert float(width_match.group(1)) == pytest.approx(
            expected_pdf_points, abs=0.03
        )
        # Export must not switch off the caller's Heri crop preference.
        assert mpl.rcParams["savefig.bbox"] == "tight"


def test_publication_axis_label_typography_defaults_and_customizable(layout):
    with af.latex_style(layout, width="column") as p:
        fig, ax = p.subplots()
        ax.set(xlabel="x axis", ylabel="y axis")
        assert mpl.rcParams["axes.labelweight"] == "normal"
        assert ax.xaxis.label.get_fontsize() == pytest.approx(layout.fontsize_pt)
        assert ax.yaxis.label.get_fontsize() == pytest.approx(layout.fontsize_pt)
        assert ax.xaxis.label.get_fontweight() == "normal"
        assert ax.yaxis.label.get_fontweight() == "normal"
    with af.latex_style(layout, axis_label_scale=0.9,
                        axis_label_weight="bold") as p:
        fig, ax = p.subplots()
        ax.set(xlabel="x", ylabel="y")
        assert ax.xaxis.label.get_fontsize() == pytest.approx(
            layout.fontsize_pt * 0.9
        )
        assert ax.yaxis.label.get_fontweight() == "bold"
    with pytest.raises(ValueError):
        with af.latex_style(layout, axis_label_scale=0):
            pass
