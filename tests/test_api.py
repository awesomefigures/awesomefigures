import numpy as np

import awesomefigures as cc


def test_palette_maps_one_hue_to_each_luminance_level():
    p = cc.contrast_palette(
        [55, 20, 145, 210, 290],
        ratio=1.4,
        start_luminance=0.95,
    )
    assert len(p) == 5
    np.testing.assert_allclose(p.adjacent_contrast, 1.4, atol=2e-8)
    np.testing.assert_allclose([cell.hue for cell in p], [55, 20, 145, 210, 290])


def test_color_palette_returns_matplotlib_rgba():
    colors = cc.color_palette([55, 145, 290], ratio=1.3)
    assert len(colors) == 3
    assert all(len(color) == 4 for color in colors)
    assert all(0 <= channel <= 1 for color in colors for channel in color)


def test_color_palette_can_return_hex():
    colors = cc.color_palette([55, 145, 290], ratio=1.3, as_hex=True)
    assert all(color.startswith("#") and len(color) == 7 for color in colors)


def test_numpy_hue_array_is_supported():
    p = cc.contrast_palette(np.array([30.0, 150.0, 270.0]), ratio=1.25)
    assert len(p) == 3
    np.testing.assert_allclose(p.adjacent_contrast, 1.25, atol=2e-8)


def test_plot_scheme_combines_color_marker_and_linestyle():
    scheme = cc.plot_scheme(
        [55, 20, 145, 210, 290],
        ratio=1.4,
        markers=["o", "s"],
        linestyles=["-", "--", ":"],
    )
    assert len(scheme) == 5
    assert scheme[0]["marker"] == "o"
    assert scheme[1]["marker"] == "s"
    assert scheme[2]["marker"] == "o"
    assert scheme[0]["linestyle"] == "-"
    assert scheme[3]["linestyle"] == "-"
    assert all("color" in item for item in scheme)


def test_plot_scheme_rejects_empty_identifier_sequences():
    import pytest

    with pytest.raises(ValueError):
        cc.plot_scheme([55, 145], markers=[])
    with pytest.raises(ValueError):
        cc.plot_scheme([55, 145], linestyles=[])


def test_print_safe_defaults_separate_three_series_in_grayscale():
    from awesomefigures.color_spaces import relative_luminance

    values = cc.print_safe_luminances(3)
    assert values[0] > values[1] > values[2]
    np.testing.assert_allclose(values[[0, 2]], [0.5, 0.035], atol=1e-10)
    assert values[0] / values[1] > 2.0
    scheme = cc.plot_scheme([25, 150, 275])
    ys = [relative_luminance(s["color"][:3]) for s in scheme]
    np.testing.assert_allclose(ys, values, atol=0.0001)
    assert len({s["marker"] for s in scheme}) == 3
    assert len({str(s["linestyle"]) for s in scheme}) == 3


def test_print_safe_scatter_defaults_and_manual_overrides():
    from awesomefigures.color_spaces import relative_luminance

    styles = cc.scatter_scheme([25, 150, 275])
    values = [relative_luminance(s["color"][:3]) for s in styles]
    np.testing.assert_allclose(values, cc.print_safe_luminances(3), atol=0.0001)
    custom = cc.plot_scheme([25, 150, 275], ratio=1.2, start_luminance=0.75)
    y = [relative_luminance(s["color"][:3]) for s in custom]
    np.testing.assert_allclose(y, [.75, (.75+.05)/1.2-.05, (.75+.05)/1.2**2-.05], atol=1e-6)


def test_print_safe_handles_different_counts_and_invalid_inputs():
    import pytest
    for count in [1, 2, 3, 5, 10]:
        values = cc.print_safe_luminances(count)
        assert len(values) == count
        assert np.all((values >= 0) & (values <= 1))
        if count > 1:
            assert np.all(np.diff(values) < 0)
    with pytest.raises(ValueError):
        cc.print_safe_luminances(0)
    with pytest.raises(ValueError):
        cc.print_safe_luminances(3, lightest=.1, darkest=.2)


def test_pie_plot_has_white_wedge_edges_and_clear_grayscale_groups():
    import matplotlib.pyplot as plt
    from awesomefigures.color_spaces import relative_luminance

    fig, ax = plt.subplots()
    wedges, labels = cc.pie_plot([20, 35, 45], labels=["A", "B", "C"], ax=ax)
    assert len(wedges) == len(labels) == 3
    assert all(np.allclose(w.get_edgecolor()[:3], (1, 1, 1)) for w in wedges)
    ys = [relative_luminance(w.get_facecolor()[:3]) for w in wedges]
    assert ys[0] > ys[1] > ys[2]
    plt.close(fig)


def test_pie_plot_edge_overrides_and_values():
    import pytest
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    wedges, _ = cc.pie_plot([1, 2], ax=ax, wedgeprops={"linewidth": 3})
    assert all(w.get_linewidth() == 3 for w in wedges)
    with pytest.raises(ValueError):
        cc.pie_plot([-1, 2], ax=ax)
    plt.close(fig)


def test_palette_preview_hex_text_uses_higher_contrast_foreground():
    import matplotlib.pyplot as plt

    ax = cc.show_palette(
        [25, 115, 205, 295],
        ratio=1.55, start_luminance=0.65,
        alpha=0.7, background="white",
    )
    assert len(ax.texts) == len(ax.patches) == 4
    from awesomefigures.color_spaces import contrast_ratio
    for patch, label in zip(ax.patches, ax.texts):
        r, g, b, a = patch.get_facecolor()
        background = [(a * ch + (1 - a)) for ch in (r, g, b)]
        # Text contrast was chosen using the actual compensated displayed
        # color, not the nominal uncomposited source color.
        assert contrast_ratio(background, label.get_color()) >= 4.5
    plt.close(ax.figure)
