# Multiscale Paper Reproduction

## Experiment

From `D:\MRI` in PowerShell:

```powershell
$env:PYTHONPATH="D:\MRI\pre;D:\MRI\design"
D:\conda\envs\MRI\python.exe -B -m rasinet.run_cross_scale_evaluation --config D:\MRI\design\rasinet\configs\multiscale_primary.yaml
D:\conda\envs\MRI\python.exe -B -m rasinet.cross_scale_paper_assets
```

The first command audits all inputs before scoring and writes results to
`design\rasinet\outputs\multiscale`. The second command regenerates the LaTeX
tables and vector figures under `paper_updated`.

## Papers

```powershell
cd D:\MRI\design\rasinet\paper_updated
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_multiscale.tex
bibtex paper_icassp_regular_multiscale
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_multiscale.tex
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_multiscale.tex
```

Replace the basename with `paper_extended_multiscale` for the extended paper.
The Overleaf ZIP uses `main.tex` as the regular entry point.

## Governance

- Primary committee membership, score, mask, normalization, seed, and bootstrap
  count are frozen in `configs/multiscale_primary.yaml`.
- Ground truth is passed only to retrospective metric functions.
- The expanded seven-neural analysis is sensitivity, not model selection.
- All fixed profiles, including negative results, remain in `results_registry.csv`.
