#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-from-precomputed}"
PYTHON_BIN="${PYTHON_BIN:-python}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="$ROOT/design"
cd "$ROOT"

if [[ "$MODE" == "recompute-features" ]]; then
  "$PYTHON_BIN" -u -B -m rasinet.nested_precompute --scope development --workers 2
  "$PYTHON_BIN" -u -B -m rasinet.nested_precompute --scope ningxia --workers 2
  "$PYTHON_BIN" -u -B -m rasinet.cross_scale_physical
fi

"$PYTHON_BIN" -u -B -m rasinet.nested_selection --stage public
"$PYTHON_BIN" -u -B -m rasinet.nested_selection --stage nested
"$PYTHON_BIN" -u -B -m rasinet.nested_selection_robust
"$PYTHON_BIN" -u -B -m rasinet.nested_analysis
"$PYTHON_BIN" -u -B -m rasinet.nested_transfer_analysis
"$PYTHON_BIN" -u -B -m rasinet.generate_nested_paper_assets
"$PYTHON_BIN" -u -B -m unittest tests.test_rasinet_nested_optimization

cd "$ROOT/design/rasinet/paper_updated"
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
bibtex paper_icassp_regular_nested_optimized
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
pdflatex -interaction=nonstopmode -halt-on-error paper_extended_nested_optimized.tex
bibtex paper_extended_nested_optimized
pdflatex -interaction=nonstopmode -halt-on-error paper_extended_nested_optimized.tex
pdflatex -interaction=nonstopmode -halt-on-error paper_extended_nested_optimized.tex
