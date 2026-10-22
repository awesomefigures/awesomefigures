"""Test accessibility, print and marker defaults."""
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pytest
import awesomefigures as af


@pytest.fixture
def small_fig():
    fig, ax = plt.subplots(figsize=(2.8, 2.0), dpi=70)
    x = np.linspace(0, 6, 80)
    for i, style in enumerate(af.plot_scheme(
        [20, 140, 260], ratio=1.2, start_luminance=.75
    )):
        ax.plot(x, np.sin(x+i), **style)
    fig.tight_layout()
    yield fig
    plt.close("all")


def test_six_modes(small_fig):
    original = af.figure_to_rgba(small_fig, max_width=170)
    views = af.figure_variants(small_fig, max_width=170)
    assert tuple(views) == af.DEFAULT_ACCESSIBILITY_MODES
    for output in views.values():
        assert output.shape == original.shape
        assert output.dtype == np.uint8
    np.testing.assert_array_equal(views["original"], original)


def test_color_vision_simulations_preserve_alpha():
    src = np.array([[[255, 0, 0, 90], [0, 255, 0, 255]]], dtype=np.uint8)
    for mode in ("deuteranopia", "protanopia", "tritanopia"):
        target = af.simulate_cvd_image(src, mode)
        np.testing.assert_array_equal(src[..., 3], target[..., 3])
        assert np.any(src[..., :3] != target[..., :3])


def test_grayscale_and_print():
    img = np.array([[[255, 0, 0, 130]]], dtype=np.uint8)
    for transformed in (af.to_grayscale_image(img),
                        af.to_print_stress_image(img)):
        assert transformed[0, 0, 0] == transformed[0, 0, 1]
        assert transformed[0, 0, 1] == transformed[0, 0, 2]
        assert transformed[0, 0, 3] == 130


def test_panel_does_not_modify_original(small_fig, tmp_path):
    count = len(small_fig.axes[0].lines)
    panel, axes = af.show_accessibility_panel(small_fig, max_width=160)
    assert len(axes) == 6
    assert len(small_fig.axes[0].lines) == count
    plt.close(panel)
    target = tmp_path / "panel.png"
    assert af.save_accessibility_panel(small_fig, target, max_width=160) == target
    assert target.is_file()


def test_bad_inputs(small_fig):
    with pytest.raises(ValueError):
        af.simulate_figure(small_fig, "invalid")
    with pytest.raises(ValueError):
        af.to_grayscale_image(np.zeros((3, 2)))
    with pytest.raises(ValueError):
        af.simulate_cvd_image(np.zeros((1, 1, 3), dtype=np.uint8),
                              "protanopia", severity=101)


def test_scheme_and_automatic_identifiers():
    scheme = af.scatter_scheme([20, 140, 280], ratio=1.2, start_luminance=.72)
    assert all(set(item) == {"color", "marker"} for item in scheme)
    assert len(set(x["marker"] for x in scheme)) == 3
    with af.style_context("heri", font="DejaVu Sans"):
        fig, ax = plt.subplots()
        for i in range(3):
            ax.plot([0, 1], [i, i+1])
            ax.scatter([0, 1], [i, i+1])
        assert len(set(x.get_marker() for x in ax.lines)) == 3
        assert len(set(x.get_linestyle() for x in ax.lines)) == 3
        assert len(set(len(c.get_paths()[0].vertices) for c in ax.collections)) >= 2
        plt.close(fig)



@pytest.mark.parametrize("ncols", [2, 3])
def test_panel_titles_centered_just_above_the_rendered_image(small_fig, ncols):
    panel, image_axes = af.show_accessibility_panel(
        small_fig, ncols=ncols, max_width=220,
        figsize=(10, 12) if ncols == 2 else (13, 8),
        title_fontsize=10, title_pad=0.01,
    )
    panel.canvas.draw()
    renderer = panel.canvas.get_renderer()
    assert len(image_axes) == 6
    assert len(panel.axes) == 6
    for ax in image_axes:
        assert len(ax.texts) == 1
        title = ax.texts[0]
        text_box = title.get_window_extent(renderer)
        image_box = ax.get_window_extent(renderer)
        assert title.get_fontweight() == "normal"
        # Centered on the actual image, not on a wider header cell.
        assert abs((text_box.x0 + text_box.x1) / 2 -
                   (image_box.x0 + image_box.x1) / 2) < 2.0
        assert text_box.y0 >= image_box.y1 - 1.0
        assert text_box.y0 - image_box.y1 < 15.0
    plt.close(panel)


def test_panel_rejects_unusable_title_spacing(small_fig):
    with pytest.raises(ValueError):
        af.show_accessibility_panel(small_fig, title_fontsize=0)
    with pytest.raises(ValueError):
        af.show_accessibility_panel(small_fig, title_pad=-1)


@pytest.mark.parametrize("ncols", [2, 3])
def test_vector_dashboard_has_no_raster_images_and_correct_fonts(ncols, tmp_path):
    import matplotlib.collections as collections
    import matplotlib as mpl
    with af.style_context("heri", font="DejaVu Sans", rasterize=False):
        source, ax = plt.subplots()
        x = np.arange(5)
        for i, color in enumerate(("#E69F00", "#0072B2", "#009E73")):
            ax.plot(x, x + i, label=f"Series {i+1}", marker="o",
                    color=color, linestyle=("-", "--", ":")[i])
        ax.set(xlabel="Time", ylabel="Response")
        panel, views = af.show_vector_accessibility_panel(
            source, ncols=ncols, figsize=(7, 8 if ncols == 2 else 4.5),
            axis_label_fontsize=10, title_fontsize=10,
        )
        assert len(views) == 6
        for panel_ax in views:
            assert not panel_ax.images
            assert len(panel_ax.lines) == 3
            assert panel_ax.xaxis.label.get_fontsize() == 10
            assert panel_ax.yaxis.label.get_fontweight() == "normal"
            assert panel_ax.title.get_fontsize() == 10
        out = tmp_path / "vectors.pdf"
        with mpl.rc_context({"savefig.bbox": None}):
            panel.savefig(out, bbox_inches=None)
        content = out.read_bytes()
        assert b"/Subtype /Image" not in content
        assert out.stat().st_size > 500
        plt.close(panel)
        plt.close(source)


def test_vector_scatter_keeps_marker_geometry_alpha_and_white_edges():
    fig, ax = plt.subplots()
    for i, (color, marker) in enumerate(zip(
        ("#E69F00", "#0072B2", "#009E73"), ("o", "s", "^")
    )):
        ax.scatter([0, 1], [i, i + 1], marker=marker, c=color, s=45,
                   alpha=.62, edgecolors="white", linewidths=.22,
                   label=f"Group {i+1}")
    dest, axs = af.show_vector_accessibility_panel(
        fig, figsize=(7, 8), ncols=2,
    )
    for a in axs:
        assert not a.images
        assert len(a.collections) == 3
        for original, copied in zip(ax.collections, a.collections):
            assert copied.get_rasterized() is False
            np.testing.assert_allclose(original.get_offsets(), copied.get_offsets())
            np.testing.assert_allclose(original.get_sizes(), copied.get_sizes())
            np.testing.assert_allclose(copied.get_linewidths(), [.22])
            np.testing.assert_allclose(copied.get_edgecolors()[:, :3], [[1, 1, 1]])
            assert np.max(copied.get_facecolors()[:, 3]) == pytest.approx(.62)
    plt.close(dest)
    plt.close(fig)


def test_vector_scatter_does_not_fill_entire_axes_with_marker_paths():
    """Catch oversized PDF/PGF markers that shape/size metadata tests miss."""
    rng = np.random.default_rng(20261007)
    source, ax = plt.subplots()
    for i, (marker, color) in enumerate(zip(
        ("o", "s", "^"), ("#E69F00", "#0072B2", "#009E73")
    )):
        x = rng.normal(i * .65, .45, 34)
        y = .5 * x + rng.normal(i * .45, .32, 34)
        ax.scatter(x, y, s=48, marker=marker, color=color, alpha=.68,
                   edgecolors="white", linewidths=.22, label=f"Group {i+1}")

    panel, views = af.show_vector_accessibility_panel(
        source, modes=("original",), ncols=1, figsize=(3.5, 3.4)
    )
    panel.canvas.draw()
    rgba = np.asarray(panel.canvas.buffer_rgba())
    bbox = views[0].get_window_extent()
    x0, y0, x1, y1 = map(int, (bbox.x0, bbox.y0, bbox.x1, bbox.y1))
    height = rgba.shape[0]
    # Sample the interior: no labels, borders, or legends.
    interior = rgba[height-y1+20:height-y0-20, x0+20:x1-20, :3]
    filled_fraction = np.mean(np.any(interior < 245, axis=2))
    # Correctly sized 48 pt2 markers occupy a minority of the graph.
    # The old direct PathCollection clone colored virtually every pixel.
    assert filled_fraction < .45, f"Scatter paths expanded: {filled_fraction:.1%}"
    plt.close(panel)
    plt.close(source)


def test_vector_print_stress_restores_gray_paper_background():
    source, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], color="#0072B2")
    panel, axes = af.show_vector_accessibility_panel(
        source, modes=("original", "grayscale", "print"), ncols=3
    )
    np.testing.assert_allclose(axes[0].get_facecolor()[:3], (1, 1, 1))
    np.testing.assert_allclose(axes[1].get_facecolor()[:3], (1, 1, 1))
    np.testing.assert_allclose(axes[2].get_facecolor()[:3], (.875, .875, .875))
    assert all(not view.images for view in axes)
    plt.close(panel)
    plt.close(source)


def test_compact_vector_scatter_dashboard_has_no_clipped_labels():
    """Physical 452 TeX pt wide 3 x 2 publication layout must pass audits."""
    layout = af.LatexLayout.from_dimensions(
        columnwidth_pt=217.69, textwidth_pt=452, fontsize_pt=10
    )
    source, ax = plt.subplots()
    for i, (marker, color) in enumerate(zip(
        ("o", "s", "^"), ("#E69F00", "#0072B2", "#009E73")
    )):
        ax.scatter([i, i + .5], [i / 2, i / 2 + .4],
                   marker=marker, color=color, s=48, alpha=.68,
                   edgecolors="white", linewidths=.22, label=f"Group {i+1}")
    ax.set(xlabel="Measurement A", ylabel="Measurement B")
    with af.latex_style(layout, width="text", rasterize=False) as pub:
        panel, _ = af.show_vector_accessibility_panel(
            source, ncols=3,
            figsize=(layout.width_inches("text"), 4.05),
            axis_label_fontsize=10, title_fontsize=10,
            tick_fontsize=8, legend_fontsize=8,
        )
        report = pub.audit(panel)
        assert report.passed, report.warnings
        plt.close(panel)
    plt.close(source)


def test_vector_dashboard_rejects_unsupported_heatmaps():
    fig, ax = plt.subplots()
    ax.imshow(np.ones((2, 3)))
    with pytest.raises(ValueError, match="no line or scatter"):
        af.show_vector_accessibility_panel(fig)
    plt.close(fig)



def test_vector_pdf_scatter_contains_no_bitmap_objects(tmp_path):
    fig, ax = plt.subplots()
    for i, (marker, color) in enumerate(
        zip(("o", "s", "^"), ("#E69F00", "#0072B2", "#009E73"))
    ):
        ax.scatter(np.arange(12), np.arange(12) + i, marker=marker,
                   color=color, s=48, alpha=.68,
                   edgecolors="white", linewidths=.22,
                   label=f"G{i}")
    with af.latex_style(
        af.LatexLayout.from_dimensions(
            columnwidth_pt=220, textwidth_pt=452, fontsize_pt=10
        ), width="text", rasterize=False,
    ) as pub:
        panel, _ = af.show_vector_accessibility_panel(
            fig, ncols=3,
            figsize=(pub.layout.width_inches("text"), 4.05),
            axis_label_fontsize=10,
        )
        path = pub.savefig(panel, tmp_path / "vector_panel.pdf", audit=False)
        assert b"/Subtype /Image" not in path.read_bytes()
        assert panel.get_size_inches()[0] == pytest.approx(
            pub.layout.width_inches("text")
        )
        plt.close(panel)
    plt.close(fig)
