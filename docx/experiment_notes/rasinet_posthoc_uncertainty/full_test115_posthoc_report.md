# RASI post-hoc uncertainty report: full_test115

Status: completed full post-hoc reliability analysis using existing predictions only.

This is not a RASI-Net training result. It evaluates whether low-cost uncertainty proxies can indicate interpolation error and failure risk for existing strong methods.

## Case coverage

| Method | Available cases | Requested cases | Run directory |
|---|---:|---:|---|
| i3net | 115 | 115 | `D:\MRI\ixi_i3net\runs\full_test115_stable` |
| hat | 115 | 115 | `D:\MRI\ixi_hat_2p5d\runs\full_test115` |
| swinir | 115 | 115 | `D:\MRI\ixi_swinir_2p5d\runs\full_test115` |
| acsinet | 115 | 115 | `D:\MRI\acsinet\runs\full_test115` |

## Best proxy per method

| Method | Best proxy | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall |
|---|---|---:|---:|---:|---:|---:|---:|
| acsinet | baseline_disagreement | 0.5667 | 0.4178 | 4.2948 | 1.4552 | 0.9871 | 0.8333 |
| hat | baseline_disagreement | 0.6090 | 0.4578 | 4.4683 | 1.5250 | 0.9871 | 0.8333 |
| i3net | baseline_disagreement | 0.5018 | 0.3567 | 3.9249 | 1.4225 | 0.9822 | 0.7500 |
| swinir | baseline_disagreement | 0.6153 | 0.4572 | 4.4922 | 1.5253 | 0.9871 | 0.8333 |

## Interpretation

- `baseline_disagreement` is the strongest and most stable proxy across I3Net, HAT, SwinIR, and ACSI-Net.
- `residual_linear` and `residual_cubic` are useful sanity proxies, but they should not be framed as the main comparison target.
- The current Design 3 story should be reliability and failure-awareness on top of strong existing models, not a claim that a newly trained RASI-Net beats SOTA.

## Generated files

- `D:\MRI\docx\experiment_notes\rasinet_posthoc_uncertainty\full_test115_proxy_ranking.csv`
- `D:\MRI\docx\experiment_notes\rasinet_posthoc_uncertainty\full_test115_failure_case_ranking.csv`
- `D:\MRI\docx\experiment_notes\rasinet_posthoc_uncertainty\full_test115_risk_coverage_summary.csv`
- `D:\MRI\rasinet\runs\posthoc_uncertainty\full_test115\metrics\paper_table_posthoc.md`
- `D:\MRI\rasinet\runs\posthoc_uncertainty\full_test115\metrics\risk_coverage_posthoc.csv`
- `D:\MRI\rasinet\runs\posthoc_uncertainty\full_test115\metrics\calibration_bins_posthoc.csv`
- `D:\MRI\docx\experiment_notes\rasinet_posthoc_uncertainty\plots\full_test115_best_proxy_correlation.png`
- `D:\MRI\docx\experiment_notes\rasinet_posthoc_uncertainty\plots\full_test115_risk_coverage_baseline_disagreement.png`

## Next step

Use the top failure-case list to select visual QC examples, then repeat the same post-hoc reliability evaluation on fastMRI and NingXia if the paper needs cross-dataset evidence.
