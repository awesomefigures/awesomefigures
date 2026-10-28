"""Document-aware publication of *existing* Matplotlib figures.

The API orchestrates the existing PublicationStyle and TeX probes. It never
runs a numerical experiment or calls a user's data-generation function.
"""
from __future__ import annotations

from contextlib import ExitStack
from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
from typing import Literal

import matplotlib.pyplot as plt

from . import publication as _legacy


class PublicationError(RuntimeError):
    """Exact TeX rendering or publication validation failed."""


def _resolve_width(layout: _legacy.LatexLayout, width: str | float) -> float:
    """Return physical inches; numeric arguments retain the legacy meaning."""
    if not isinstance(width, str):
        return layout.width_inches(width)
    normalized = width.strip().lower().replace(" ", "")
    if normalized in ("column", "text", "full", "page"):
        kind = "text" if normalized in ("full", "page") else normalized
        return layout.width_inches(kind)
    m = re.fullmatch(
        r"([0-9]+(?:\.[0-9]+)?)\\?(columnwidth|textwidth|column|text|full)",
        normalized,
    )
    if m:
        ratio = float(m.group(1))
        if not 0 < ratio <= 1:
            raise ValueError("LaTeX-relative width must be in (0, 1].")
        kind = "column" if m.group(2).startswith("column") else "text"
        return ratio * layout.width_inches(kind)
    raise ValueError(
        "width must be 'column', 'text', 'full', positive inches, "
        "or a fraction such as r'0.85\\textwidth'."
    )


@lru_cache(maxsize=32)
def _cached_probe(path: str, digest: str, engine: str, timeout: int):
    return _legacy.inspect_latex(path, engine=engine, timeout=timeout)


def clear_publication_cache() -> None:
    """Clear cached manuscript measurements when class/style files change."""
    _cached_probe.cache_clear()


def _probe_document(path: Path, engine: str, timeout: int):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return _cached_probe(str(path), digest, engine, timeout), digest


def _pdf_details(path: Path):
    """Inspect actual physical page bounds and font embedding via pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise PublicationError(
            "Install the optional publication audit dependency with "
            "python -m pip install 'awesomefigures[publication]'."
        ) from exc
    try:
        reader = PdfReader(str(path))
        if len(reader.pages) != 1:
            raise PublicationError(
                f"Expected one figure page; found {len(reader.pages)}: {path}"
            )
        page = reader.pages[0]
        fonts = {}
        visited = set()

        def inspect_resources(resources):
            if resources is None:
                return
            resources = resources.get_object()
            for key, ref in (resources.get("/Font") or {}).items():
                obj = ref.get_object()
                # Keys are scoped to a resource dictionary, not globally.
                name = str(obj.get("/BaseFont", key))
                if name in fonts:
                    continue
                desc = obj.get("/FontDescriptor")
                desc = desc.get_object() if desc else None
                fonts[name] = {
                    "name": name,
                    "embedded": bool(desc and any(
                        desc.get(x) for x in ("/FontFile", "/FontFile2", "/FontFile3")
                    )),
                }
            for key, ref in (resources.get("/XObject") or {}).items():
                if id(ref) in visited:
                    continue
                visited.add(id(ref))
                obj = ref.get_object()
                if obj.get("/Subtype") == "/Form":
                    inspect_resources(obj.get("/Resources"))

        inspect_resources(page.get("/Resources"))
        return float(page.mediabox.width), float(page.mediabox.height), sorted(
            fonts.values(), key=lambda x: x["name"]
        )
    except PublicationError:
        raise
    except Exception as exc:
        raise PublicationError(f"Could not inspect PDF {path}: {exc}") from exc


