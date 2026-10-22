"""The elegant preset aligns spines with readable endpoint ticks."""
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pytest

import awesomefigures as af


@pytest.fixture(autouse=True)
def cleanup():
    yield
    af.set_style("default")
    plt.close("all")


@pytest.mark.parametrize("bounds,target", [
    ((7.0, 94.0), 6),
    ((0.0, 100.0), 6),
    ((-0.37, 1.28), 5),
    ((-112.4, -13.8), 6),
    ((0.00012, 0.00034), 5),
])
def test_nice_ticks_cover_values_and_include_both_endpoints(bounds, target):
    lo, hi, ticks = af.nice_tick_bounds(*bounds, target_ticks=target)
    assert lo <= bounds[0] < bounds[1] <= hi
    assert ticks[0] == lo and ticks[-1] == hi
    np.testing.assert_allclose(np.diff(ticks), np.diff(ticks)[0], atol=1e-12)
    assert 2 <= len(ticks) <= 2 * target + 4


def test_pretty_exact_data_endpoints_preferred():
    lo, hi, ticks = af.nice_tick_bounds(0, 100, target_ticks=6)
    assert (lo, hi) == (0, 100)
    np.testing.assert_allclose(ticks, [0, 20, 40, 60, 80, 100])


def test_elegante_auto_finishes_axes_during_draw():
    assert "elegante" in af.available_styles()
    af.set_style("elegante", font="DejaVu Sans", use_tex=False, rasterize=False)
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
    af.set_style("elegante", font="DejaVu Sans", use_tex=False, rasterize=False)
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
    af.set_style("elegante", font="DejaVu Sans", use_tex=False)
    fig, ax = plt.subplots()
    ax.plot(np.linspace(0, 10, 60), np.sin(np.linspace(0, 10, 60)))
    ax.set_xlim(-2.3, 12.7)
    fig.canvas.draw()
    assert ax.get_xlim() == (-2.3, 12.7)


def test_scatter_only_extrema_are_not_clipped_or_hidden():
    af.set_style("elegante", font="DejaVu Sans", use_tex=False, rasterize=False)
    fig, ax = plt.subplots()
    points = ax.scatter([0, 100], [0, 100], s=90)
    fig.canvas.draw()
    assert points.get_offsets().shape == (2, 2)
    assert ax.get_xlim()[0] < 0 < 100 < ax.get_xlim()[1]
    assert ax.get_ylim()[0] < 0 < 100 < ax.get_ylim()[1]


def test_style_context_restores_automatic_finishing():
    with af.style_context("elegante", font="DejaVu Sans", use_tex=False):
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
        af.nice_tick_bounds(0, 10, target_ticks=1)
    with pytest.raises(ValueError):
        af.nice_tick_bounds(0, 10, padding=-1)
    with pytest.raises(ValueError):
        af.nice_tick_bounds(0, 10, steps=[0])
    with pytest.raises(ValueError):
        af.apply_elegant_axes(plt.subplots()[1], marker_inset_pt=-2)
