"""Font search and TeX-native PGF integration."""
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib as mpl
import matplotlib.pyplot as plt

import awesomefigures as af
import awesomefigures.publication as publication


def test_find_tex_font_metrics_only(monkeypatch, tmp_path):
    metrics = tmp_path / "pplr7t.tfm"
    metrics.write_bytes(b"metric")
    monkeypatch.setattr(publication, "inspect_latex", lambda *args, **kwargs:
        af.LatexLayout.from_dimensions(columnwidth_pt=240, textwidth_pt=500,
            fontsize_pt=10, font_family="ppl", font_name="pplr7t at 10pt"))
    monkeypatch.setattr(publication, "_kpsewhich",
        lambda filename: metrics if filename == "pplr7t.tfm" else None)
    result = af.find_latex_font(tmp_path / "paper.tex")
    assert result.tex_font_name == "pplr7t at 10pt"
    assert result.metrics_path == metrics
    assert result.outline_path is None
    assert not result.has_font_file


def test_find_tex_font_outline(monkeypatch, tmp_path):
    file = tmp_path / "cmr10.pfb"
    file.write_bytes(b"outline")
    monkeypatch.setattr(publication, "inspect_latex", lambda *args, **kwargs:
        af.LatexLayout.from_dimensions(columnwidth_pt=240, textwidth_pt=500,
            fontsize_pt=10, font_family="cmr", font_name="cmr10 at 10pt"))
    monkeypatch.setattr(publication, "_kpsewhich",
        lambda filename: file if filename == "cmr10.pfb" else None)
    result = af.find_latex_font(tmp_path / "paper.tex")
    assert result.outline_path == file
    assert result.has_font_file


def test_pgf_uses_manuscript_engine_not_os_font(monkeypatch, tmp_path):
    layout = af.LatexLayout.from_dimensions(
        columnwidth_pt=245, textwidth_pt=510, fontsize_pt=10)
    before = bool(mpl.rcParams["pgf.rcfonts"])
    with af.latex_style(layout, engine="pdflatex") as pub:
        fig, ax = pub.subplots()
        ax.plot([0, 1], [1, 2])
        calls = []
        def fake_savefig(filename, *, format=None, **kwargs):
            calls.append((filename, format, mpl.rcParams["pgf.texsystem"],
                          mpl.rcParams["pgf.rcfonts"], kwargs["bbox_inches"]))
        monkeypatch.setattr(fig, "savefig", fake_savefig)
        output = pub.savefig(fig, tmp_path / "curve.pgf", audit=False)
        assert output == tmp_path / "curve.pgf"
        assert calls == [(output, "pgf", "pdflatex", False, None)]
        assert bool(mpl.rcParams["pgf.rcfonts"]) == before
        plt.close(fig)


def test_kpsewhich_not_installed(monkeypatch):
    monkeypatch.setattr(publication.shutil, "which", lambda cmd: None)
    assert publication._kpsewhich("font.tfm") is None
