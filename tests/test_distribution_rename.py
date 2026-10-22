"""Distribution package and Python import checks for awesomefigures."""
from pathlib import Path
import tomllib
import awesomefigures as af

ROOT = Path(__file__).resolve().parents[1]

def test_new_distribution_metadata_matches_import():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["name"] == "awesomefigures"
    assert (ROOT / "src" / "awesomefigures" / "__init__.py").exists()
    assert not (ROOT / "src" / "contrastcolors").exists()
    assert af.available_styles()
    assert af.named_palette("okabe-ito", as_hex=True)[0] == "#E69F00"

def test_new_import_alias_is_documented():
    for path in ("README.md", "docs/source/quickstart.rst", "docs/source/_static/studio.html"):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "import awesomefigures as af" in text
        assert "import contrastcolors as cc" not in text
