from pathlib import Path

import awesomefigures as cc


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "source"


def test_every_public_root_symbol_is_mentioned_in_docs():
    documentation = "\n".join(
        path.read_text(encoding="utf-8")
        for path in DOCS.rglob("*.rst")
    )

    missing = sorted(name for name in cc.__all__ if name not in documentation)
    assert not missing, f"Public API missing from documentation: {missing}"
