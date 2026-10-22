from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

import awesomefigures as af


def teardown_function():
    af.set_style("default")
    plt.close("all")


def test_set_style_heri_matches_wti_publication_rcparams():
    af.set_style("heri", use_tex=False)

    assert mpl.rcParams["axes.spines.top"] is False
    assert mpl.rcParams["axes.spines.right"] is False
    assert mpl.rcParams["axes.grid"] is True
    assert mpl.rcParams["axes.facecolor"] == "white"
    assert mpl.rcParams["figure.facecolor"] == "white"
    assert mpl.rcParams["savefig.transparent"] is False
    assert mpl.rcParams["savefig.dpi"] == 600
    assert mpl.rcParams["font.size"] == 8.5
    assert mpl.rcParams["lines.linewidth"] == 1.6
    assert mpl.rcParams["lines.markersize"] == 4.5
    assert mpl.rcParams["pdf.fonttype"] == 42


def test_heri_palette_matches_wti_publication_palette():
    assert af.HERI_PALETTE == (
        "#97001c",
        "#0083f9",
        "#00b49c",
        "#ffc600",
        "#f198ff",
    )
    assert af.HERI_IRIDESCENT_HEX[0] == "#FEFBE9"
    assert af.HERI_IRIDESCENT_HEX[-1] == "#46353A"


def test_heri_style_keeps_lines_vector_and_rasterizes_dense_artists():
    af.set_style("heri", use_tex=False, rasterize=True)
    fig, ax = plt.subplots()
    (line,) = ax.plot([0, 1], [0, 1])
    points = ax.scatter([0, 1], [1, 0])
    ax.set_xlabel("x")

    assert line.get_rasterized() is False
    assert points.get_rasterized() is True
    assert ax.xaxis.label.get_rasterized() is False


def test_rasterization_can_be_disabled():
    af.set_style("heri", use_tex=False, rasterize=False)
    fig, ax = plt.subplots()
    points = ax.scatter([0, 1], [0, 1])

    assert points.get_rasterized() is False


def test_custom_font_can_be_selected():
    af.set_style("heri", font="Arial", use_tex=False)
    assert mpl.rcParams["font.family"] == ["Arial"]
    assert mpl.rcParams["text.usetex"] is False


def test_custom_font_auto_mode_avoids_latex():
    af.set_style("heri", font="Arial", use_tex="auto")
    assert mpl.rcParams["font.family"] == ["Arial"]
    assert mpl.rcParams["text.usetex"] is False


def test_custom_font_cannot_be_forced_through_utopia_tex_stack():
    with pytest.raises(ValueError):
        af.set_style("heri", font="Arial", use_tex=True)


def test_save_figure_defaults_to_pdf(tmp_path: Path):
    af.set_style("heri", use_tex=False)
    fig, ax = plt.subplots()
    ax.scatter([0, 1], [1, 0])

    path = af.save_figure(fig, tmp_path / "example")
    assert path.suffix == ".pdf"
    assert path.exists()
    assert path.stat().st_size > 0


def test_style_context_restores_previous_rcparams():
    before = mpl.rcParams["axes.spines.top"]
    with af.style_context("heri", font="Arial", use_tex=False):
        assert mpl.rcParams["axes.spines.top"] is False
        assert mpl.rcParams["font.family"] == ["Arial"]
    assert mpl.rcParams["axes.spines.top"] == before


def test_unknown_style_fails():
    with pytest.raises(ValueError):
        af.set_style("not-a-style")


def test_default_heri_palette_prioritizes_grayscale_separation():
    from awesomefigures.color_spaces import relative_luminance

    af.set_style("heri", font="DejaVu Sans", use_tex=False)
    rendered = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
    first_three = [relative_luminance(color) for color in rendered[:3]]
    assert first_three[0] > first_three[1] > first_three[2]
    assert first_three[0] - first_three[1] > 0.20
    assert first_three[1] - first_three[2] > 0.10
    assert len(set(rendered)) == 5


def test_legacy_style_palette_is_still_selectable():
    af.set_style("heri", font="DejaVu Sans", use_tex=False, palette="legacy")
    assert mpl.rcParams["axes.prop_cycle"].by_key()["color"] == list(af.HERI_PALETTE)
    with pytest.raises(ValueError):
        af.set_style("heri", palette="unknown")
