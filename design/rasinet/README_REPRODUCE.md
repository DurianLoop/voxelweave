# Reproducing the ICASSP Reliability Study

## Scope

The evaluation consumes stored deterministic NIfTI reconstructions. It does not retrain a reconstructor and never modifies source NIfTI files. Ground truth is unavailable to score and deployment-mask functions and is loaded only after the deployment scores for a case have been constructed.

## Environment

The validated local interpreter is `D:\conda\envs\MRI\python.exe`. From `D:\MRI`, expose the local packages:

```powershell
$env:PYTHONPATH=(Resolve-Path .\pre).Path + ";" + (Resolve-Path .\baseline).Path + ";" + (Resolve-Path .\design).Path + ";" + (Resolve-Path .).Path
```

Install only if the environment is missing a dependency:

```powershell
D:\conda\envs\MRI\python.exe -m pip install -r design\rasinet\requirements.txt
```

## Commands

Run unit tests:

```powershell
D:\conda\envs\MRI\python.exe -B -m unittest tests.test_rasinet_committee_reliability tests.test_rasinet_icassp_scores -v
```

Run the registered candidate optimization tests:

```powershell
D:\conda\envs\MRI\python.exe -B -m unittest tests.test_rasinet_optimization -v
```

Reproduce the development search, freeze, and one-shot validation (run in this order):

```powershell
$env:PYTHONPATH=(Resolve-Path .\design).Path + ";" + (Resolve-Path .).Path
D:\conda\envs\MRI\python.exe -u -B -m rasinet.run_candidate_optimization --stage development
D:\conda\envs\MRI\python.exe -u -B -m rasinet.run_candidate_optimization --stage validation
D:\conda\envs\MRI\python.exe -u -B -m rasinet.analyze_optimization_results
D:\conda\envs\MRI\python.exe -u -B -m rasinet.generate_optimization_assets
```

Run the implementation smoke test:

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.run_reliability_evaluation --config design\rasinet\configs\icassp_smoke.yaml
```

Run all pre-specified P0/P1 analyses:

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.run_reliability_evaluation --config design\rasinet\configs\icassp_primary.yaml
```

Export bounded primary voxel-map examples (two IXI/fastMRI examinations and two per NingXia fold):

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.run_reliability_evaluation --config design\rasinet\configs\icassp_voxel_examples.yaml
```

Run the pre-specified 20-case IXI shared-error stress test:

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.shared_error_stress_test --config design\rasinet\configs\shared_error_stress.yaml
```

Re-evaluate the existing fastMRI SwinIR TTA maps under the same case-level protocol:

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.evaluate_tta_maps --config design\rasinet\configs\tta_fastmri.yaml
```

Benchmark linear and cubic interpolation on the fixed first ten examinations per cohort (CPU interpolation only; no source file is modified):

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.benchmark_analytical_cost --config design\rasinet\configs\analytical_cost.yaml
```

Benchmark the complete stored-output audit (prediction NIfTI reads plus the default score/mask, with no ground-truth read):

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.benchmark_posthoc_cost --config design\rasinet\configs\posthoc_cost.yaml
```

Generate paper assets after the full run:

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.icassp_paper_assets --results design\rasinet\outputs\icassp_primary
```

Rebuild the result registry and run the fixed-count/content audit:

```powershell
D:\conda\envs\MRI\python.exe -u -B -m rasinet.build_results_registry
D:\conda\envs\MRI\python.exe -u -B -m rasinet.validate_icassp_outputs
```

Compile both manuscripts from `design\rasinet\paper`:

```powershell
pdflatex paper_icassp_regular.tex
bibtex paper_icassp_regular
pdflatex paper_icassp_regular.tex
pdflatex paper_icassp_regular.tex
pdflatex paper_icassp_extended.tex
bibtex paper_icassp_extended
pdflatex paper_icassp_extended.tex
pdflatex paper_icassp_extended.tex
```

## Output contract

`outputs/icassp_primary/` contains 33,672 per-examination specification rows and 504 summaries when the registered run is complete. Outputs include geometry/intensity checks, deployment scores, offline errors, foreground and all-pixel correlations, top-decile secondary failure metrics, bootstrap samples, risk--coverage source data, paired comparisons, timings, and environment metadata. The `ground_truth_offline` mask is an evaluation-only sensitivity and is never available to `score_map()` or `deployment_mask()`. `outputs/icassp_voxel_examples/` contains primary voxel maps from a separate bounded run. `outputs/results_registry.csv` records every summarized metric. Tables and figures are generated from these files rather than copied by hand.

## Governance

The primary method is frozen as all-member median target-to-committee disagreement, raw inverse-normalized intensity, a 1% target-derived foreground mask, x4 generated slices, seed 20260715, and 2,000 paired case-bootstrap replicates. IXI, fastMRI-brain, and NingXia results were already observed; variants are sensitivity analyses and are not used to select a dataset-specific method.
