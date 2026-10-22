"""Documentation and Studio controls are published together."""
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "docs" / "source" / "_static" / "studio.html"
STUDIO_PAGE = ROOT / "docs" / "source" / "studio.rst"


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.types = set()

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if "id" in props:
            self.ids.add(props["id"])
        if "data-plot" in props:
            self.types.add(props["data-plot"])


def test_studio_has_real_export_and_design_controls():
    content = STUDIO.read_text(encoding="utf-8")
    doc = STUDIO_PAGE.read_text(encoding="utf-8")
    elements = Elements()
    elements.feed(content)
    required_ids = {
        "nColors", "ratio", "startY", "chroma", "seriesList",
        "plotSwitcher", "chart", "alpha", "background", "preserve",
        "presetName", "savedPresetList", "savePreset", "loadPreset",
        "deletePreset", "importJson", "importFile", "downloadJson",
        "downloadPy", "copyCode", "code",
    }
    assert required_ids <= elements.ids
    assert {
        "lines", "time", "histogram", "box", "violin", "ridge",
        "scatter", "heatmap", "bar", "pie",
    } <= elements.types
    assert "af.register_palette(" in content
    assert "plotPython(plotType)" in content
    assert "designSnapshot()" in content
    assert "applyDesign(raw)" in content
    assert "_static/studio.html" in doc
    assert "awesomefigures-studio-height" in doc


def test_palette_studio_has_visual_hue_methods_and_cvd_modes():
    html = STUDIO.read_text(encoding="utf-8")
    el = Elements()
    el.feed(html)
    assert {
        "hueStrategy", "baseHue", "baseHueColor", "contrastPreset",
        "applyStrategy", "hueWheel", "lineAtlas", "markerAtlas",
        "visionComparison",
    } <= el.ids
    for method in (
        "equidistant", "golden", "qualitative", "analogous",
        "monochrome", "custom"
    ):
        assert f'value="{method}"' in html
    for mode in ("deuteranopia", "protanopia", "tritanopia"):
        assert f'data-mode="{mode}"' in html
    for logic in ("function methodHues(", "function toCvdRgb(",
                  "function renderVisionComparison(",
                  "function linePreview(", "function hueFromHex("):
        assert logic in html
    assert "prefers-reduced-motion:reduce" in html
    assert "frame.style.height" in STUDIO_PAGE.read_text(encoding="utf-8")



def test_print_safe_studio_defaults_adapt_to_color_count():
    html = STUDIO.read_text(encoding="utf-8")
    assert 'value="print-safe" selected' in html
    assert "awesomefigures.print_safe_luminances" in html
    assert "Math.pow((light+.05)/(dark+.05),1/(n-1))" in html
    assert "ratio<1||ratio>8" in html


def test_studio_historical_palettes_match_python_exactly():
    """A browser preview must not quietly depart from Python's HEX scheme."""
    import re
    import awesomefigures as af

    html = STUDIO.read_text(encoding="utf-8")
    el = Elements()
    el.feed(html)
    assert "builtinPalette" in el.ids
    for name in af.available_named_palettes("categorical"):
        match = re.search(r"'" + re.escape(name) + r"':\[([^]]+)\]", html)
        assert match, f"Missing browser palette: {name}"
        actual = re.findall(r"#[A-F0-9]{6}", match.group(1))
        assert actual == af.named_palette(name, as_hex=True)
    assert "let activeBuiltin=''" in html
    assert "function leaveBuiltin()" in html
    assert "function chooseBuiltin(name)" in html
    assert "Measured adjacent CR (not a WCAG design constraint)" in html
    assert "style:['heri','elegante','default']" in html
    assert "af.named_palette(" in html
    assert "af.plot_scheme(" in html
    assert "builtinPalette:activeBuiltin" in html


def test_studio_javascript_syntax_when_node_is_available(tmp_path):
    import re
    import shutil
    import subprocess
    import pytest

    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is not installed")
    html = STUDIO.read_text(encoding="utf-8")
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.S)
    assert scripts
    for index, script in enumerate(scripts):
        if not script.strip():
            continue
        script_file = tmp_path / f"studio-{index}.js"
        script_file.write_text(script, encoding="utf-8")
        subprocess.run([node, "--check", str(script_file)], check=True,
                       capture_output=True, text=True, timeout=12)

