#!/usr/bin/env bash
set -euo pipefail
pdflatex -interaction=nonstopmode -halt-on-error main.tex
/usr/bin/bibtex.original main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
mv -f main.pdf paper_icassp_regular_visual_relayout.pdf
