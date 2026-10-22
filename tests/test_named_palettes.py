"""Regression tests for canonical RGB palettes and their integrations."""
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pytest
import awesomefigures as cc


def teardown_function():
    cc.set_style("default")
    plt.close("all")


def test_okabe_ito_is_exact_and_has_accessible_aliases():
    expected = [
        "#E69F00", "#56B4E9", "#009E73", "#F0E442",
        "#0072B2", "#D55E00", "#CC79A7", "#000000",
    ]
    for name in ("okabe-ito", "okabe_ito", "colorblind", "wong"):
        assert cc.named_palette(name, as_hex=True) == expected
        assert cc.color_palette(name, as_hex=True) == expected
    assert cc.get_named_palette("okabe-ito").kind == "categorical"
    assert "okabe-ito" in cc.available_named_palettes("categorical")
    assert "cividis" in cc.available_named_palettes("sequential")


def test_tol_and_colorbrewer_source_values_are_unchanged():
    assert cc.color_palette("tol-bright", as_hex=True) == [
        "#4477AA", "#EE6677", "#228833", "#CCBB44",
        "#66CCEE", "#AA3377", "#BBBBBB",
    ]
    assert cc.color_palette("tol-high-contrast", as_hex=True) == [
        "#004488", "#DDAA33", "#BB5566",
    ]
    assert cc.color_palette("brewer-set2", as_hex=True)[0] == "#66C2A5"
    assert len(cc.available_named_palettes("categorical")) >= 7


@pytest.mark.parametrize("name", ["viridis", "cividis", "plasma", "magma", "inferno", "rdbu"])
def test_continuous_colormaps_are_real_matplotlib_maps(name):
    metadata = cc.get_named_palette(name)
    cmap = cc.named_colormap(name)
    assert cmap.name == metadata.matplotlib_cmap
    colors = cc.color_palette(name, n=6, as_hex=True)
    assert len(colors) == 6
    assert colors[0] == mpl.colors.to_hex(cmap(0.), keep_alpha=False).upper()
    assert colors[-1] == mpl.colors.to_hex(cmap(1.), keep_alpha=False).upper()


def test_invalid_requests_are_explained_instead_of_changing_original_palette():
    with pytest.raises(ValueError, match="only 8"):
        cc.named_palette("okabe-ito", n=9)
    with pytest.raises(ValueError, match="exact HEX"):
        cc.color_palette("okabe-ito", ratio=1.2)
    with pytest.raises(ValueError, match="WCAG luminance ladder"):
        cc.contrast_palette("okabe-ito")
    with pytest.raises(ValueError, match="positive integer"):
        cc.named_palette("okabe-ito", n=0)
    with pytest.raises(KeyError):
        cc.get_named_palette("no-such-palette")
    with pytest.raises(ValueError):
        cc.available_named_palettes("invalid")


def test_named_colors_are_integrated_with_scatter_and_line_encodings():
    line_styles = cc.plot_scheme("okabe-ito", n=3)
    assert len(line_styles) == 3
    assert len({x["marker"] for x in line_styles}) == 3
    assert len({x["linestyle"] for x in line_styles}) == 3
    assert [mpl.colors.to_hex(x["color"]).upper() for x in line_styles] == [
        "#E69F00", "#56B4E9", "#009E73",
    ]
    scatter_styles = cc.scatter_scheme("tol-bright", n=4)
    assert all(set(style) == {"color", "marker"} for style in scatter_styles)


@pytest.mark.parametrize("style", ["heri", "elegante"])
def test_styles_can_use_canonical_palette_without_losing_marker_cycle(style):
    cc.set_style(style, palette="okabe-ito", font="DejaVu Sans", use_tex=False)
    cycle = mpl.rcParams["axes.prop_cycle"].by_key()
    assert cycle["color"] == cc.named_palette("okabe-ito", as_hex=True)
    assert len(set(cycle["marker"])) == 8
    assert len(set(map(str, cycle["linestyle"]))) >= 5
    with pytest.raises(ValueError, match="Sequential/diverging"):
        cc.set_style(style, palette="viridis", font="DejaVu Sans", use_tex=False)


def test_historical_named_palettes_are_not_in_process_registrations():
    assert "okabe-ito" not in cc.available_palettes()
    cc.register_palette("my_generated", hues=[25, 155, 275],
                        ratio=1.1, overwrite=True)
    assert "my_generated" in cc.available_palettes()
    assert cc.color_palette("my_generated")


def test_alpha_and_hex_swatches_still_work():
    rgba = cc.named_palette("okabe-ito", n=3, alpha=.65,
                            preserve_apparent=False)
    assert all(color[-1] == pytest.approx(.65) for color in rgba)
    ax = cc.show_palette("okabe-ito", n=3)
    assert len(ax.patches) == 3
    plt.close(ax.figure)
    assert np.asarray(cc.named_palette("cividis", n=3)).shape == (3, 4)
