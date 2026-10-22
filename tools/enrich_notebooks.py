"""Ensure every plot-producing notebook cell has an accessibility panel after it.

Idempotent; safe to run repeatedly. Does not execute notebooks.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import nbformat
from nbformat.v4 import new_code_cell


def is_plot_cell(cell) -> bool:
    if cell.cell_type != "code":
        return False
    src = cell.source
    return "plt.subplots(" in src or "plt.figure(" in src or "grid.plot(" in src


def is_accessibility_cell(cell) -> bool:
    return cell.cell_type == "code" and (
        "accessibility-panel" in cell.metadata.get("tags", ())
        or "af.show_accessibility_panel(" in cell.source
    )


def enrich_notebook(notebook) -> int:
    cells = []
    added = 0
    for index, cell in enumerate(notebook.cells):
        cells.append(cell)
        if not is_plot_cell(cell):
            continue
        if (index + 1 < len(notebook.cells)
                and is_accessibility_cell(notebook.cells[index + 1])):
            continue
        figure = "ax.figure" if "grid.plot(" in cell.source and "plt.subplots(" not in cell.source else "fig"
        panel = new_code_cell(
            "af.show_accessibility_panel(" + figure + ", max_width=640)\n"
            "plt.show()"
        )
        panel.metadata["tags"] = ["accessibility-panel"]
        cells.append(panel)
        added += 1
    notebook.cells = cells
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directory", type=Path, default=Path("docs/source/notebooks")
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    files = sorted((root / args.directory).resolve().glob("*.ipynb"))
    if not files:
        raise ValueError("No notebooks found")
    for path in files:
        notebook = nbformat.read(path, as_version=4)
        count = enrich_notebook(notebook)
        if count:
            nbformat.write(notebook, path)
        print(f"{path.name}: {count} added panel cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
