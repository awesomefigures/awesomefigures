"""Render frozen sample values without executing a numerical experiment.

Example:
    python examples/automatic_publication/render.py --preview
    python examples/automatic_publication/render.py --tex examples/automatic_publication/two_column.tex
    python examples/automatic_publication/render.py --tex paper/sncs_main.tex
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import awesomefigures as af


HERE = Path(__file__).resolve().parent

# Fixed demonstration values; no regression, optimization or random generation.
X = tuple(range(10))
SERIES = {
    "Reference": (1.2, 1.5, 1.9, 2.0, 1.8, 2.3, 2.6, 2.5, 2.8, 3.0),
    "Alternative": (1.0, 1.3, 1.6, 1.9, 2.0, 2.1, 2.3, 2.6, 2.7, 2.9),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex", type=Path, default=HERE / "article.tex")
    parser.add_argument("--preview", action="store_true",
                        help="Use an ordinary Matplotlib PDF without TeX font claims")
    parser.add_argument("--output", type=Path, default=HERE / "generated")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    with af.paper(args.tex, style="elegante",
                        palette="okabe-ito", strict=not args.preview) as pub:
        # First figure at the manuscript's actual column width.
        fig, ax = pub.subplots()
        for name, y in SERIES.items():
            ax.plot(X, y, label=name)
        ax.set(xlabel="Observation", ylabel="Recorded value")
        ax.legend()
        pub.savefig(fig, args.output / "series.pdf", exact=not args.preview)
        pub.savefig(fig, args.output / "series.svg")

        # One figure spanning the full text width of the same manuscript.
        fig, axes = pub.subplots(1, 2, width="full", height_ratio=.42)
        for ax, (name, values) in zip(axes, SERIES.items()):
            ax.plot(X, values, label=name)
            ax.set(xlabel="Observation", ylabel="Value", title=name)
        pub.savefig(fig, args.output / "comparison.pdf",
                    width="full", exact=not args.preview)
        pub.savefig(fig, args.output / "comparison.png", width="full")
        print("Manifest:", pub.report(args.output / "manifest.json"))
    print("No statistical results were recalculated.")


if __name__ == "__main__":
    main()
