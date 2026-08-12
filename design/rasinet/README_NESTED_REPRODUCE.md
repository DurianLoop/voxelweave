# Reproducing the Nested Reliability Study

The archive preserves the repository-relative layout. Run commands from the
archive root. Raw NIfTI files are not modified.

## Fast reproduction from supplied features

The supplied CSVs contain common-support offline labels, prediction-only pair
features, physical-plane matches, every explored candidate, and every outer
prediction.

```powershell
.\design\rasinet\reproduce_nested.ps1 -Mode from-precomputed -Python D:\conda\envs\MRI\python.exe
```

This reruns public screening, both nested protocols, attribution, paired
bootstrap, transfer analysis, paper assets, tests, and both LaTeX papers. It
does not need the original NIfTI volumes.

## End-to-end feature extraction

After configuring prediction roots in
`design/rasinet/optimization_protocol.py`:

```powershell
.\design\rasinet\reproduce_nested.ps1 -Mode recompute-features -Python D:\conda\envs\MRI\python.exe
```

This additionally recomputes common-support metrics, deployment features, and
physical world-plane matching from NIfTI. Ground truth is used only by offline
fidelity/error evaluation. Deployment scores use predictions and observed
anchors.

## Manual stages

```powershell
$env:PYTHONPATH=(Resolve-Path .\design).Path
D:\conda\envs\MRI\python.exe -B -m rasinet.nested_selection --stage public
D:\conda\envs\MRI\python.exe -B -m rasinet.nested_selection --stage nested
D:\conda\envs\MRI\python.exe -B -m rasinet.nested_selection_robust
D:\conda\envs\MRI\python.exe -B -m rasinet.nested_analysis
D:\conda\envs\MRI\python.exe -B -m rasinet.nested_transfer_analysis
D:\conda\envs\MRI\python.exe -B -m rasinet.generate_nested_paper_assets
D:\conda\envs\MRI\python.exe -B -m unittest tests.test_rasinet_nested_optimization -v
```

For every outer fold, `selection_used_outer_labels` must remain `False`.

## Paper compilation

From `design/rasinet/paper_updated`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
bibtex paper_icassp_regular_nested_optimized
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
pdflatex -interaction=nonstopmode -halt-on-error paper_icassp_regular_nested_optimized.tex
```

Replace `paper_icassp_regular_nested_optimized` with
`paper_extended_nested_optimized` for the 8+1-page extended report.
