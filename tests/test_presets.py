import numpy as np
import pytest
import awesomefigures as af


def test_named_preset_colors_and_scheme():
    af.register_palette(
        "test_website_demo",
        hues=[35, 155, 260],
        ratio=1.22,
        start_luminance=0.72,
        chroma=0.10,
        markers=["o", "^", "s"],
        linestyles=["-", "--", ":"],
        overwrite=True,
    )
    preset = af.get_palette("test_website_demo")
    assert preset.hues == (35.0, 155.0, 260.0)
    assert "test_website_demo" in af.available_palettes()
    colors = af.color_palette("test_website_demo")
    direct = af.color_palette(preset.hues, ratio=1.22, start_luminance=0.72, chroma=0.10)
    np.testing.assert_allclose(colors, direct)
    styles = af.plot_scheme("test_website_demo")
    assert [s["marker"] for s in styles] == ["o", "^", "s"]
    assert [s["linestyle"] for s in styles] == ["-", "--", ":"]


def test_named_preset_can_override_parameters():
    af.register_palette("test_override", hues=[15, 155], ratio=1.21,
                        start_luminance=0.72, overwrite=True)
    direct = af.color_palette([15, 155], ratio=1.30, start_luminance=0.72)
    named = af.color_palette("test_override", ratio=1.30)
    np.testing.assert_allclose(named, direct)


def test_named_preset_validation_and_duplicates():
    with pytest.raises(ValueError):
        af.register_palette("not a name", hues=[55, 145])
    with pytest.raises(ValueError):
        af.register_palette("bad_values", hues=[55, np.nan])
    with pytest.raises(ValueError):
        af.register_palette("bad_ratio", hues=[55, 145, 210], ratio=7.0)
    with pytest.raises(ValueError):
        af.register_palette("bad_markers", hues=[55, 145], markers=[])
    with pytest.raises(KeyError):
        af.color_palette("does_not_exist")
    af.register_palette("test_duplicate", hues=[55, 145], overwrite=True)
    with pytest.raises(ValueError):
        af.register_palette("test_duplicate", hues=[55, 145])
