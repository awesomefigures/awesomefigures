"""Validate the reproducible Conda development entrypoint.

Dependency versions are controlled by pyproject.toml. Conda supplies Python
and the native scientific stack; pip installs the local package and tooling.
"""
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_conda_environment_is_self_contained():
    env = yaml.safe_load((ROOT / "environment.yml").read_text(encoding="utf-8"))
    assert env["name"] == "awesomefigures"
    assert env["channels"] == ["conda-forge"]
    dependencies = env["dependencies"]
    assert any(x == "python=3.12" for x in dependencies)
    assert "pip" in dependencies
    for lib in ("numpy", "matplotlib", "colorspacious"):
        assert any(isinstance(x, str) and x.startswith(lib + ">=")
                   for x in dependencies)
    assert dependencies[-1] == {"pip": ["-e .[dev,docs,notebooks]"]}


def test_editable_conda_install_has_matching_extras():
    metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "awesomefigures"' in metadata
    assert 'dev = [' in metadata
    assert 'docs = [' in metadata
    assert 'notebooks = [' in metadata
    assert '"pyyaml>=6"' in metadata
    # No pinned absolute local path or platform-specific packages:
    # a cloned checkout can use the same YAML on macOS, Linux or Windows.
    env_text = (ROOT / "environment.yml").read_text(encoding="utf-8")
    assert "prefix:" not in env_text
    assert "/Users/" not in env_text
    assert "C:\\\\" not in env_text
