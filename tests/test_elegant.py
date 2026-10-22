"""The elegant preset aligns spines with readable endpoint ticks."""
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pytest

import awesomefigures as cc


@pytest.fixture(autouse=True)
def cleanup():
    yield
    cc.set_style("default")
    plt.close("all")


@pytest.mark.parametrize("bounds,target", [
    ((7.0, 94.0), 6),
    ((0.0, 100.0), 6),
    ((-0.37, 1.28), 5),
    ((-112.4, -13.8), 6),
    ((0.00012, 0.00034), 5),
])
def test_nice_ticks_cover_values_and_include_both_endpoints(bounds, target):
    lo, hi, ticks = cc.nice_tick_bounds(*bounds, target_ticks=target)
    assert lo <= bounds[0] < bounds[1] <= hi
    assert ticks[0] == lo and ticks[-1] == hi
    np.testing.assert_allclose(np.diff(ticks), np.diff(ticks)[0], atol=1e-12)
    assert 2 <= len(ticks) <= 2 * target + 4


def test_pretty_exact_data_endpoints_preferred():
    lo, hi, ticks = cc.nice_tick_bounds(0, 100, target_ticks=6)
    assert (lo, hi) == (0, 100)
    np.testing.assert_allclose(ticks, [0, 20, 40, 60, 80, 100])


def test_elegante_auto_finishes_axes_during_draw():
    assert "elegante" in cc.available_styles()
    cc.set_style("elegante", font="DejaVu Sans", use_tex=False, rasterize=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.linspace(0, 100, 301)
    y = np.sin(x / 19)
    (line,) = ax.plot(x, y, marker="o", markersize=6)
    before_x = line.get_xdata().copy()
    before_y = line.get_ydata().copy()
    fig.canvas.draw()

    assert ax.get_xlim() == (0, 100)
    np.testing.assert_allclose(ax.get_xticks(), [0, 20, 40, 60, 80, 100])
    assert ax.get_xticks()[0] == ax.get_xlim()[0]
    assert ax.get_xticks()[-1] == ax.get_xlim()[-1]
    assert ax.get_yticks()[0] == ax.get_ylim()[0]
    assert ax.get_yticks()[-1] == ax.get_ylim()[-1]
    np.testing.assert_array_equal(line.get_xdata(), before_x)
    np.testing.assert_array_equal(line.get_ydata(), before_y)
    assert 1 <= len(line.get_markevery()) <= 9
    assert 0 not in line.get_markevery()
    assert len(x) - 1 not in line.get_markevery()


def test_inset_markers_respect_both_axes_and_keep_full_line():
    cc.set_style("elegante", font="DejaVu Sans", use_tex=False, rasterize=False)
    fig, ax = plt.subplots(figsize=(5, 3))
    x = np.linspace(0, 10, 101)
    y = np.sin(x) * 1.0
    (line,) = ax.plot(x, y, marker="s", markersize=8, markevery=4)
    fig.canvas.draw()
    positions = ax.transData.transform(np.column_stack((x, y)))
    clearance = (4 + 8 / 2 + line.get_markeredgewidth() / 2) * fig.dpi / 72
    for i in line.get_markevery():
        px, py = positions[i]
        assert ax.bbox.x0 + clearance <= px <= ax.bbox.x1 - clearance
        assert ax.bbox.y0 + clearance <= py <= ax.bbox.y1 - clearance
    assert len(line.get_xdata()) == 101
    assert line.get_markevery()[0] > 0


def test_manual_limits_are_respected_and_still_inset_markers():
    cc.set_style("elegante", font="DejaVu Sans", use_tex=False)
    fig, ax = plt.subplots()
    ax.plot(np.linspace(0, 10, 60), np.sin(np.linspace(0, 10, 60)))
    ax.set_xlim(-2.3, 12.7)
    fig.canvas.draw()
    assert ax.get_xlim() == (-2.3, 12.7)


def test_scatter_only_extrema_are_not_clipped_or_hidden():
    cc.set_style("elegante", font="DejaVu Sans", use_tex=False, rasterize=False)
    fig, ax = plt.subplots()
    points = ax.scatter([0, 100], [0, 100], s=90)
    fig.canvas.draw()
    assert points.get_offsets().shape == (2, 2)
    assert ax.get_xlim()[0] < 0 < 100 < ax.get_xlim()[1]
    assert ax.get_ylim()[0] < 0 < 100 < ax.get_ylim()[1]


def test_style_context_restores_automatic_finishing():
    with cc.style_context("elegante", font="DejaVu Sans", use_tex=False):
        fig, ax = plt.subplots()
        ax.plot(np.linspace(0, 10, 30), np.sin(np.linspace(0, 10, 30)))
        fig.canvas.draw()
        assert ax.get_xticks()[0] == ax.get_xlim()[0]
    fig2, ax2 = plt.subplots()
    ax2.plot([0, 10], [0, 1])
    fig2.canvas.draw()
    assert ax2.get_xlim()[0] < 0  # default Matplotlib margin


def test_elegant_input_validation():
    with pytest.raises(ValueError):
        cc.nice_tick_bounds(0, 10, target_ticks=1)
    with pytest.raises(ValueError):
        cc.nice_tick_bounds(0, 10, padding=-1)
    with pytest.raises(ValueError):
        cc.nice_tick_bounds(0, 10, steps=[0])
    with pytest.raises(ValueError):
        cc.apply_elegant_axes(plt.subplots()[1], marker_inset_pt=-2)


@pytest.mark.parametrize("style_name", ["heri", "elegante"])
@pytest.mark.parametrize("markevery", [None, 1, 2, 4, (0, 3), slice(None, None, 3)])
def test_dense_triangles_have_legible_physical_spacing(style_name, markevery):
    """Explicit markevery must not bypass the sparse-marker safety rule."""
    cc.set_style(style_name, font="DejaVu Sans", use_tex=False,
                 rasterize=False)
    fig, ax = plt.subplots(figsize=(5.4, 3.0), dpi=100)
    x = np.linspace(0, 100, 1401)
    y = 0.8 * np.sin(x * .11)
    (line,) = ax.plot(x, y, marker="^", markersize=7,
                      markevery=markevery)
    before = np.column_stack((line.get_xdata().copy(), line.get_ydata().copy()))
    fig.canvas.draw()
    chosen = line.get_markevery()
    assert isinstance(chosen, list)
    assert 1 <= len(chosen) <= 7
    # In 'elegante' a line may touch the spine, so endpoint markers
    # must be inset. 'heri' retains default Matplotlib axis margins, so
    # an endpoint marker can be fully inside the visible plotting area.
    if style_name == "elegante":
        assert 0 not in chosen and len(x) - 1 not in chosen
    screen = ax.transData.transform(before[chosen])
    inset_pt = 6 + line.get_markersize() / 2 + line.get_markeredgewidth() / 2
    for sx, sy in screen:
        assert (sx - ax.bbox.x0) * 72 / fig.dpi >= inset_pt - 0.01
        assert (ax.bbox.x1 - sx) * 72 / fig.dpi >= inset_pt - 0.01
        assert (sy - ax.bbox.y0) * 72 / fig.dpi >= inset_pt - 0.01
        assert (ax.bbox.y1 - sy) * 72 / fig.dpi >= inset_pt - 0.01
    for i in range(len(screen)):
        for j in range(i):
            distance_pt = np.linalg.norm(screen[i] - screen[j]) * 72 / fig.dpi
            assert distance_pt >= 37.99
    np.testing.assert_array_equal(
        np.column_stack((line.get_xdata(), line.get_ydata())), before
    )


def test_repeated_exports_and_resize_reuse_original_marker_candidates(tmp_path):
    cc.set_style("elegante", font="DejaVu Sans", use_tex=False,
                 rasterize=False)
    fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
    x = np.linspace(0, 100, 901)
    (line,) = ax.plot(x, np.sin(x / 20), marker="s", markevery=3)
    fig.canvas.draw()
    first = line.get_markevery()
    assert 1 <= len(first) <= 7
    fig.savefig(tmp_path / "sparse-markers.pdf")
    assert line.get_markevery() == first
    fig.set_size_inches(3.3, 2.6)
    fig.canvas.draw()
    narrower = line.get_markevery()
    assert len(narrower) <= len(first)
    assert len(narrower) <= 7


def test_heri_does_not_thin_marker_only_observations():
    cc.set_style("heri", font="DejaVu Sans", use_tex=False, rasterize=False)
    fig, ax = plt.subplots()
    x = np.arange(65)
    (points,) = ax.plot(x, np.sqrt(x), marker="o", linestyle="None")
    fig.canvas.draw()
    assert points.get_markevery() is None
    assert len(points.get_xdata()) == 65


def test_user_can_adjust_marker_density_explicitly():
    cc.set_style("elegante", font="DejaVu Sans", use_tex=False,
                 rasterize=False)
    fig, ax = plt.subplots(figsize=(6, 3))
    x = np.linspace(0, 100, 500)
    (line,) = ax.plot(x, np.sin(x / 13), marker="D")
    cc.apply_elegant_axes(ax, marker_count=4, marker_min_spacing_pt=46,
                          marker_inset_pt=7)
    fig.canvas.draw()
    assert 1 <= len(line.get_markevery()) <= 4
    with pytest.raises(ValueError, match="spacing"):
        cc.apply_elegant_axes(ax, marker_min_spacing_pt=0)
