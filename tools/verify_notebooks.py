"""Check that every documentation notebook contains saved figure outputs."""
from __future__ import annotations

import argparse
from pathlib import Path
import nbformat


def verify_notebooks(directory: Path) -> int:
    paths = sorted(directory.glob("*.ipynb"))
    if not paths:
        raise ValueError(f"No notebooks found in {directory}")
    errors = []
    total_figures = 0
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
        figure_indices = [
            i for i, cell in enumerate(notebook.cells)
            if cell.cell_type == "code" and
            ("plt.subplots(" in cell.source or "plt.figure(" in cell.source
             or "grid.plot(" in cell.source)
        ]
        for i in figure_indices:
            if i + 1 >= len(notebook.cells) or "af.show_accessibility_panel(" not in notebook.cells[i + 1].source:
                errors.append(f"{path.name}: figure at cell {i+1} missing panel")

        if not code_cells:
            errors.append(f"{path.name}: no code cells")
            continue
        if any(cell.execution_count is None for cell in code_cells):
            errors.append(f"{path.name}: has unexecuted code cells")
        if any(
            output.output_type == "error"
            for cell in code_cells
            for output in cell.get("outputs", [])
        ):
            errors.append(f"{path.name}: has execution errors")
        count = sum(
            bool("image/png" in output.get("data", {}) or
                 "image/svg+xml" in output.get("data", {}))
            for cell in code_cells
            for output in cell.get("outputs", [])
        )
        total_figures += count
        if count == 0:
            errors.append(f"{path.name}: no embedded figures")
        print(f"{path.name}: {len(code_cells)} executed cells, {count} figures")
    if errors:
        raise ValueError("Notebook verification failed:\n" + "\n".join(errors))
    print(f"PASS: {len(paths)} notebooks, {total_figures} embedded figure outputs")
    return total_figures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path("docs/source/notebooks"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    verify_notebooks((root / args.directory).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
