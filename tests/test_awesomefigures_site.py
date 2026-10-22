"""Keep the public Sphinx site consistent with the installed library."""
from pathlib import Path
import re

import awesomefigures as af


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "source"


def test_awesomefigures_brand_is_consistent_across_site():
    conf = (DOCS / "conf.py").read_text(encoding="utf-8")
    index = (DOCS / "index.rst").read_text(encoding="utf-8")
    studio = (DOCS / "_static" / "studio.html").read_text(encoding="utf-8")
    picker = (DOCS / "_static" / "picker.html").read_text(encoding="utf-8")
    assert 'project = "AwesomeFigures"' in conf
    assert '"logo": {"text": "AwesomeFigures"}' in conf
    assert "AwesomeFigures" in index
    assert "AwesomeFigures Studio" in studio
    assert "AwesomeFigures" in picker
    assert "named_palettes" in index


def test_featured_palette_swatches_are_identical_to_library_originals():
    """Never let manually displayed homepage swatches drift from the API."""
    index = (DOCS / "index.rst").read_text(encoding="utf-8")
    for name in ["okabe-ito", "tol-bright", "brewer-dark2"]:
        token = {
            "okabe-ito": "Eight original Okabe–Ito colours",
            "tol-bright": "Seven Paul Tol Bright colours",
            "brewer-dark2": "Eight ColorBrewer Dark2 colours",
        }[name]
        block = index.split(f'aria-label="{token}"', 1)[1].split("</span>", 1)[0]
        hex_codes = [v.upper() for v in re.findall(r"background:(#[0-9A-Fa-f]{6})", block)]
        assert hex_codes == af.named_palette(name, as_hex=True)


def test_all_builtin_palettes_are_represented_in_atlas():
    rst = (DOCS / "named_palettes.rst").read_text(encoding="utf-8")
    assert "available_named_palettes" in rst
    assert "named_colormap" in rst
    assert "13" in rst


def test_sparse_marker_guide_explains_sample_preservation():
    rst = (DOCS / "style.rst").read_text(encoding="utf-8")
    for term in ("marker_min_spacing_pt=38.0", "marker_count=7",
                 "markevery=1", "1401", "full continuous line"):
        assert term in rst.replace("1,401", "1401")
