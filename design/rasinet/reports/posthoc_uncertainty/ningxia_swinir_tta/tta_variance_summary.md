# NingXia T2 CV SwinIR TTA variance experiment

This experiment evaluates 4-view flip TTA variance as an uncertainty proxy for NingXia T2 CV SwinIR.

| Method / proxy | Cases | Pixel Corr | Slice Corr | AURC | MAE@50% low-U | Failure AUROC | Top-k Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| swinir_original__tta_variance | 22 | 0.4042 | 0.6661 | 30.8201 | 24.4556 | 1.0000 | 1.0000 |
| swinir_tta_mean__tta_variance | 22 | 0.4033 | 0.6665 | 30.7713 | 24.4254 | 1.0000 | 1.0000 |

## Baseline disagreement comparison

| Metric | TTA variance | Baseline disagreement | Delta |
|---|---:|---:|---:|
| pixel_corr | 0.4033 | 0.4562 | -0.0528 |
| slice_corr | 0.6665 | 0.2758 | 0.3907 |
| risk_coverage_aurc | 30.7713 | 30.2951 | 0.4763 |
| mae_50pct_low_u | 24.4254 | 24.4725 | -0.0471 |
| failure_auroc | 1.0000 | 0.9474 | 0.0526 |
| top_k_failure_recall | 1.0000 | 0.6667 | 0.3333 |
