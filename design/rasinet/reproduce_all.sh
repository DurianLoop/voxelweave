#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
if command -v cygpath >/dev/null 2>&1; then
  REPO_ROOT="$(cygpath -w "$(pwd)")"
else
  REPO_ROOT="$(pwd)"
fi
export PYTHONPATH="${REPO_ROOT}/pre;${REPO_ROOT}/baseline;${REPO_ROOT}/design;${REPO_ROOT}"
PYTHON_BIN="${PYTHON_BIN:-D:/conda/envs/MRI/python.exe}"

"$PYTHON_BIN" -B -m unittest tests.test_rasinet_committee_reliability tests.test_rasinet_icassp_scores -v
"$PYTHON_BIN" -u -B -m rasinet.run_reliability_evaluation --config design/rasinet/configs/icassp_primary.yaml
"$PYTHON_BIN" -u -B -m rasinet.run_reliability_evaluation --config design/rasinet/configs/icassp_voxel_examples.yaml
"$PYTHON_BIN" -u -B -m rasinet.shared_error_stress_test --config design/rasinet/configs/shared_error_stress.yaml
"$PYTHON_BIN" -u -B -m rasinet.evaluate_tta_maps --config design/rasinet/configs/tta_fastmri.yaml
"$PYTHON_BIN" -u -B -m rasinet.benchmark_analytical_cost --config design/rasinet/configs/analytical_cost.yaml
"$PYTHON_BIN" -u -B -m rasinet.benchmark_posthoc_cost --config design/rasinet/configs/posthoc_cost.yaml
"$PYTHON_BIN" -u -B -m rasinet.build_results_registry
"$PYTHON_BIN" -u -B -m rasinet.icassp_paper_assets --results design/rasinet/outputs/icassp_primary
"$PYTHON_BIN" -u -B -m rasinet.validate_icassp_outputs

cd design/rasinet/paper
for paper in paper_icassp_regular paper_icassp_extended; do
  pdflatex -interaction=nonstopmode -halt-on-error "${paper}.tex"
  bibtex "$paper"
  pdflatex -interaction=nonstopmode -halt-on-error "${paper}.tex"
  pdflatex -interaction=nonstopmode -halt-on-error "${paper}.tex"
done
