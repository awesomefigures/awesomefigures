"""Keep the documented capability inventory synchronized with the actual API."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_every_exported_name_is_documented_in_feature_catalogue():
    module = ast.parse(
        (ROOT / "src/awesomefigures/__init__.py").read_text(encoding="utf-8")
    )
    assignments = (
        node for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
    )
    names = ast.literal_eval(next(assignments).value)
    catalogue = (ROOT / "docs/source/features.rst").read_text(encoding="utf-8")
    assert len(names) == len(set(names)), "Public exports must be unique"
    missing = [name for name in names if f"``{name}``" not in catalogue]
    assert not missing, f"Update the feature inventory for new API symbols: {missing}"


def test_feature_catalogue_is_discoverable():
    index = (ROOT / "docs/source/index.rst").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "   features" in index
    assert "features.rst" in readme
