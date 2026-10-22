"""Distribution package and Python import checks for awesomefigures."""
from pathlib import Path
from importlib.metadata import metadata
import awesomefigures as af

ROOT = Path(__file__).resolve().parents[1]

def test_new_distribution_metadata_matches_import():
    assert metadata("awesomefigures")["Name"] == "awesomefigures"
    assert (ROOT / "src" / "awesomefigures" / "__init__.py").exists()
    assert not (ROOT / "src" / "contrastcolors").exists()
    assert af.available_styles()
    assert af.named_palette("okabe-ito", as_hex=True)[0] == "#E69F00"

def test_new_import_alias_is_documented():
    for path in ("README.md", "docs/source/quickstart.rst", "docs/source/_static/studio.html"):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "import awesomefigures as af" in text
        assert "import contrastcolors as cc" not in text
