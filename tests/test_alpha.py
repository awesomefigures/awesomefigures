import numpy as np

from awesomefigures import compensate_alpha, composite, minimum_alpha


def test_exact_alpha_compensation_when_feasible():
    target = np.array([0.45, 0.55, 0.65])
    result = compensate_alpha(target, alpha=0.8, background=[0.2, 0.2, 0.2])
    assert result.feasible
    np.testing.assert_allclose(result.displayed_rgb, target, atol=1e-12)


def test_alpha_compensation_reports_gamut_limit():
    result = compensate_alpha("#101010", alpha=0.3, background="#FFFFFF")
    assert not result.feasible
    assert np.all((result.source_rgb >= 0) & (result.source_rgb <= 1))
    np.testing.assert_allclose(
        result.displayed_rgb,
        composite(result.source_rgb, "#FFFFFF", 0.3),
    )


def test_named_matplotlib_background_is_supported():
    result = compensate_alpha("#808080", alpha=1.0, background="white")
    assert result.feasible
    np.testing.assert_allclose(result.displayed_rgb, [128 / 255] * 3)


def test_minimum_alpha_on_white_for_zero_channel_is_one():
    assert minimum_alpha("#00A7BC", background="white") == 1.0


def test_minimum_alpha_is_sufficient():
    target = "#80A0C0"
    alpha = minimum_alpha(target, background="white")
    result = compensate_alpha(target, alpha=max(alpha, 1e-12), background="white")
    assert result.feasible


def test_perceptual_fallback_is_no_worse_than_channel_clipping():
    target = "#00A7BC"
    perceptual = compensate_alpha(
        target,
        alpha=0.75,
        background="white",
        strategy="perceptual",
    )
    clipped = compensate_alpha(
        target,
        alpha=0.75,
        background="white",
        strategy="clip",
    )
    assert not perceptual.feasible
    assert perceptual.delta_e_ok <= clipped.delta_e_ok + 1e-12
