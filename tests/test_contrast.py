import numpy as np
import pytest

from awesomefigures import luminance_ladder, luminance_contrast


def test_luminance_ladder_has_constant_ratio():
    ys = luminance_ladder(5, 1.5, start_luminance=0.95)
    ratios = [luminance_contrast(a, b) for a, b in zip(ys[:-1], ys[1:])]
    np.testing.assert_allclose(ratios, 1.5, atol=1e-12)


def test_luminance_ladder_rejects_impossible_request():
    with pytest.raises(ValueError):
        luminance_ladder(20, 2.0)
