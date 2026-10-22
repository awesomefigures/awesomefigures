"""Generate a physically correct sample figure and optional LaTeX proof.

Usage
-----
python tools/run_publication_demo.py
python tools/run_publication_demo.py --tex paper/main.tex
python tools/run_publication_demo.py --tex paper/main.tex --engine xelatex
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil

import numpy as np
import awesomefigures as af


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex", type=Path, help="Trusted LaTeX paper to measure")
    parser.add_argument("--engine", default="pdflatex", choices=("pdflatex", "xelatex", "lualatex"))
    parser.add_argument("--output", type=Path, default=Path("docs/_build/publication_demo"))
    parser.add_argument("--pgf", action="store_true",
                        help="Export TeX-native PGF for manuscript-owned fonts")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    if args.tex:
        layout = af.inspect_latex(args.tex, engine=args.engine)
        detected = af.find_latex_font(args.tex, engine=args.engine)
        print(f"LaTeX body font: {detected.tex_font_name}")
        print(f"Font outline (if located): {detected.outline_path}")
        print(f"Font metrics (if located): {detected.metrics_path}")
        print(f"Font resolution: {detected.source}")
        print(f"Measured {args.tex}: column {layout.columnwidth_pt:.2f} pt, "
              f"text {layout.textwidth_pt:.2f} pt, font {layout.fontsize_pt:.2f} pt.")
    else:
        layout = af.LatexLayout.from_dimensions(
            columnwidth_pt=245, textwidth_pt=510, fontsize_pt=10
        )
        print("Using illustrative dimensions. Pass --tex to inspect a real manuscript.")

    with af.latex_style(layout, width="column", engine=args.engine) as pub:
        fig, ax = pub.subplots(height_ratio=0.67)
        x = np.linspace(0, 10, 240)
        for i in range(3):
            ax.plot(x, np.sin(x * 0.6 + i * 0.55) + 0.32 * i,
                    label=f"Series {i+1}", markevery=40)
        ax.set(xlabel="Time", ylabel="Normalized response")
        ax.legend()
        report = pub.audit(fig)
        pdf = pub.savefig(fig, args.output / "publication_figure.pdf")
        print(f"Saved PDF: {pdf}")
        if args.pgf:
            pgf = pub.savefig(fig, args.output / "publication_figure.pgf")
            print(f"Saved TeX-native PGF: {pgf}")
            print("Include PGF using LaTeX input in the original manuscript.")
        print("Audit:", "PASS" if report.passed else "WARN")
        for warning in report.warnings:
            print(" -", warning)
        if args.tex:
            proof = args.output / "publication_proof.pdf"
            af.verify_latex_placement(
                args.tex, pdf, width="column",
                engine=args.engine, proof_pdf=proof
            )
            print("LaTeX proof:", proof)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
