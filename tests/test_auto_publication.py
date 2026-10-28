"""New high-level publication workflow: no numerical experiments are run."""
from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import pytest

import awesomefigures as af
import awesomefigures.auto_publication as auto


@pytest.fixture(autouse=True)
def clean_figures():
    yield
    plt.close("all")
    af.set_style("default")
    af.clear_publication_cache()


@pytest.fixture
def measured():
    return af.LatexLayout.from_dimensions(
        textwidth_pt=480, columnwidth_pt=230,
        fontsize_pt=10, baselineskip_pt=12,
        font_family="cmr", font_name="cmr10",
    )


def test_width_vocabulary_and_explicit_inches(measured):
    assert auto._resolve_width(measured, "column") == pytest.approx(230 / 72.27)
    assert auto._resolve_width(measured, "text") == pytest.approx(480 / 72.27)
    assert auto._resolve_width(measured, "full") == pytest.approx(480 / 72.27)
    assert auto._resolve_width(measured, r"0.85\textwidth") == pytest.approx(
        0.85 * 480 / 72.27
    )
    assert auto._resolve_width(measured, "0.5column") == pytest.approx(
        115 / 72.27
    )
    assert auto._resolve_width(measured, 3.25) == pytest.approx(3.25)
    for bad in ("", "random", "0text", "1.2text", -1, True):
        with pytest.raises(ValueError):
            auto._resolve_width(measured, bad)


def test_probe_is_cached_and_invalidated_by_document_text(tmp_path, monkeypatch, measured):
    tex = tmp_path / "main.tex"
    tex.write_text("\\documentclass{article}\n\\begin{document}\n", encoding="utf-8")
    invoked = []
    def inspect(path, *, engine, timeout):
        invoked.append((path, engine, timeout))
        return measured
    monkeypatch.setattr(auto._legacy, "inspect_latex", inspect)
    a = af.Publication(tex)
    b = af.Publication(tex)
    assert a.layout is b.layout
    assert len(invoked) == 1
    tex.write_text(tex.read_text() + "% Revision", encoding="utf-8")
    af.Publication(tex)
    assert len(invoked) == 2
    af.clear_publication_cache()
    af.Publication(tex)
    assert len(invoked) == 3


def test_existing_publication_style_is_backward_compatible(measured):
    with af.latex_style(measured, width="column") as original:
        fig, ax = original.subplots()
        ax.plot([0, 1], [0, 1])
        assert fig.get_size_inches()[0] == pytest.approx(measured.width_inches())
    with af.latex_style(measured, width="text", style="elegante",
                        palette="okabe-ito") as styled:
        fig, ax = styled.subplots()
        ax.plot([0, 1], [1, 0])
        assert fig.get_size_inches()[0] == pytest.approx(measured.width_inches("text"))


def test_batch_preview_width_font_manifest_and_no_fake_exact_claim(tmp_path, measured):
    with af.paper(measured, style="elegante", strict=False) as pub:
        fig, ax = pub.subplots()
        ax.plot([0, 1, 2], [1, 2, 0], label="A")
        ax.set(xlabel="Time", ylabel="Value")
        pdf = pub.savefig(fig, tmp_path / "a.pdf", exact=False)
        width, height, fonts = auto._pdf_details(pdf)
        assert width == pytest.approx(measured.width_inches() * 72, abs=.1)
        assert height > 0
        assert isinstance(fonts, list)
        fig2, bx = pub.subplots(width="full", height_ratio=.45)
        bx.plot([0, 1], [1, 2])
        svg = pub.savefig(fig2, tmp_path / "b.svg", width="full")
        png = pub.savefig(fig2, tmp_path / "b.png", width="full")
        assert svg.exists() and png.exists()
        manifest = pub.report(tmp_path / "manifest.json")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["figure_count"] == 3
    assert all(x["typography"] == "preview-matplotlib" for x in data["figures"])
    assert data["figures"][0]["pdf_fonts"] == fonts
    assert data["figures"][0]["sha256"] == hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert manifest.with_suffix(".md").is_file()
    assert "exact-tex-preamble" not in manifest.read_text()


def test_missing_manuscript_cannot_claim_exact_pdf(tmp_path, measured):
    with af.paper(measured) as pub:
        fig, ax = pub.subplots()
        ax.plot([0, 1], [0, 1])
        with pytest.raises(af.PublicationError, match="manuscript"):
            pub.savefig(fig, tmp_path / "publication.pdf")
        with pytest.raises(ValueError, match="only for PDF"):
            pub.savefig(fig, tmp_path / "bad.svg", exact=True)


def test_plain_figure_is_fitted_for_manuscript_width(tmp_path, measured):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("A value")
    with af.paper(measured) as pub:
        out = pub.savefig(fig, tmp_path / "fitted.pdf", exact=False)
        assert out.exists()
        assert fig.get_size_inches()[0] == pytest.approx(measured.width_inches())
        assert pub.records[-1].actual_width_tex_pt == pytest.approx(230, abs=.2)


def test_actionable_missing_tex_error(tmp_path, monkeypatch):
    pgf = tmp_path / "plot.pgf"
    pgf.write_text("test", encoding="utf-8")
    tex = tmp_path / "main.tex"
    tex.write_text("\\documentclass{article}\n\\begin{document}", encoding="utf-8")
    monkeypatch.setattr(auto.shutil, "which", lambda exe: None)
    with pytest.raises(af.PublicationError, match="MiKTeX"):
        auto._compile_exact_pdf(pgf, tmp_path / "result.pdf", tex, "pdflatex", 15)


def test_strict_mode_rejects_unreadably_small_lines(tmp_path, measured):
    with af.paper(measured, strict=True) as pub:
        fig, ax = pub.subplots()
        ax.plot([0, 1], [0, 1], linewidth=.01)
        with pytest.raises(af.PublicationError, match="Pre-export"):
            pub.savefig(fig, tmp_path / "should_not_exist.pdf", exact=False)
        assert not (tmp_path / "should_not_exist.pdf").exists()


def test_optional_real_tex_pgf_pdf_fonts_and_dimensions(tmp_path):
    if shutil.which("pdflatex") is None:
        pytest.skip("Real TeX integration is run on the Linux TeX workflow")
    tex = tmp_path / "article.tex"
    tex.write_text(
        "\\documentclass[10pt,twocolumn]{article}\n"
        "\\usepackage{graphicx}\n"
        "\\begin{document}\n"
        "Body text.\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    with af.paper(tex, strict=True) as pub:
        assert pub.layout.columnwidth_pt < pub.layout.textwidth_pt
        fig, ax = pub.subplots()
        ax.plot([0, 1, 2], [1, 2, 1], label="Series A")
        ax.set(xlabel="Time", ylabel="Measure")
        output = pub.savefig(fig, tmp_path / "tex_figure.pdf")
        assert output.is_file()
        record = pub.records[-1]
        assert record.typography == "exact-tex-preamble"
        assert record.actual_width_tex_pt == pytest.approx(
            pub.layout.columnwidth_pt, abs=0.75
        )
        assert record.pdf_fonts
        assert all(font["embedded"] for font in record.pdf_fonts)
        assert (tmp_path / "tex_figure.pgf").exists()
        manifest = pub.report(tmp_path / "verified.json")
        assert json.loads(manifest.read_text())["all_passed"] is True
