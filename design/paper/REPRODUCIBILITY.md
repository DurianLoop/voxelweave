# Reproducibility

## Scope and immutability

All Plan-2 programs, logs, reports, and generated outputs are under `D:\MRI\design\paper`. They read existing artifacts below `D:\MRI\design` but do not modify them. `PC-v1-FROZEN` is specified in `FROZEN_METHOD.md`.

## Environment

- Windows PowerShell
- Python: `D:\conda\envs\MRI\python.exe`
- Repository module path: `D:\MRI\pre;D:\MRI\design;D:\MRI`
- Plan-2 date: 2026-08-12
- Bootstrap seeds and replication counts are recorded in each script/output manifest; confirmatory clustered intervals use 5,000 replicates.

## Plan-2 analysis commands

Run from `D:\MRI\design\paper` in this order:

```powershell
D:\conda\envs\MRI\python.exe -B .\plan2_confirmatory_analysis.py
D:\conda\envs\MRI\python.exe -B .\plan2_geometry_audit.py
D:\conda\envs\MRI\python.exe -B .\plan2_common_mode_mechanism.py
D:\conda\envs\MRI\python.exe -B .\plan2_context_controls.py
D:\conda\envs\MRI\python.exe -B .\plan2_tta_comparator.py
D:\conda\envs\MRI\python.exe -B .\plan2_boundary_analysis.py
D:\conda\envs\MRI\python.exe -B .\plan2_localization_analysis.py
D:\conda\envs\MRI\python.exe -B .\plan2_localization_statistics.py
D:\conda\envs\MRI\python.exe -B .\plan2_localization_ningxia.py
D:\conda\envs\MRI\python.exe -B .\plan2_synthesis_analysis.py
```

The programs write only to `plan2_outputs/`. The derivation/confirmation split is deterministic and lexicographic, not selected by outcomes.

## Evidence audit

```powershell
D:\conda\envs\MRI\python.exe -B .\audit_evidence.py
```

Verified result on 2026-08-12: `21` checks, `0` failures.

## Canonical RASINet tests

Run from `D:\MRI`:

```powershell
$env:PYTHONPATH='D:\MRI\pre;D:\MRI\design;D:\MRI'
D:\conda\envs\MRI\python.exe -B -m unittest -q tests.test_rasinet_committee_experiments tests.test_rasinet_committee_paper_assets tests.test_rasinet_committee_reliability tests.test_rasinet_committee_statistics tests.test_rasinet_core tests.test_rasinet_icassp_scores tests.test_rasinet_multiscale tests.test_rasinet_nested_optimization tests.test_rasinet_optimization tests.test_rasinet_paper_consistency
```

Verified result on 2026-08-12: `64` tests passed in `0.424 s`.

## Primary machine-readable outputs

- `plan2_outputs/confirmatory_summary.json`
- `plan2_outputs/extended_geometry_summary.json`
- `plan2_outputs/boundary_summary.json`
- `plan2_outputs/synthesis_summary.json`
- `plan2_outputs/localization/confirmation/statistical_summary.json`
- `plan2_outputs/localization/ningxia_confirmation/statistical_summary.json`
- `plan2_outputs/localization/cross_dataset_statistical_summary.json`

The Markdown reports are interpretations of these files; the CSV/JSON artifacts are the numerical source of truth.

## Plan-3 additions

Plan-3 programs are the 19 files matching `plan3_*.py`. Their outputs are under `plan3_outputs/`. Key summaries are:

- `boundary_variance_summary.json`
- `prereconstruction_triangle_summary.json`
- `diversity_validation_summary.json`
- `spectral_spatial_summary.json`
- `scaling_decomposition_summary.json`
- `anchor_curvature_summary.json`
- `bias_diversity_summary.json`
- `scale_control_summary.json`
- `tta_all_summary.json`
- `variance_fraction_clustered_ci.json`

The TTA experiments use frozen checkpoints and four views: identity, horizontal flip, vertical flip, and both flips. NingXia uses its fold-specific OOF checkpoint. No checkpoint is retrained or modified.

Plan-3 closeout verification on 2026-08-13:

- 19/19 Plan-3 scripts parse successfully;
- all 35 Plan-3 JSON files parse successfully;
- all 18 TTA profile deltas favor PC;
- legacy evidence audit passes 21/21;
- canonical RASINet tests pass 64/64 in 0.327 s.
