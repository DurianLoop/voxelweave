# NingXia T2 CV SwinIR TTA variance experiment

This experiment evaluates 4-view flip TTA variance as an uncertainty proxy for NingXia T2 CV SwinIR.

| Method / proxy | Cases | Pixel Corr | Slice Corr | AURC | MAE@50% low-U | Failure AUROC | Top-k Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| swinir_original__tta_variance | 2 | 0.4020 | 0.8100 | 30.7755 | 29.2439 | 1.0000 | 1.0000 |
| swinir_tta_mean__tta_variance | 2 | 0.4061 | 0.8228 | 30.7502 | 29.1966 | 1.0000 | 1.0000 |

## Baseline disagreement comparison

| Metric | TTA variance | Baseline disagreement | Delta |
|---|---:|---:|---:|
| pixel_corr | 0.4061 | 0.4562 | -0.0501 |
| slice_corr | 0.8228 | 0.2758 | 0.5470 |
| risk_coverage_aurc | 30.7502 | 30.2951 | 0.4552 |
| mae_50pct_low_u | 29.1966 | 24.4725 | 4.7241 |
| failure_auroc | 1.0000 | 0.9474 | 0.0526 |
| top_k_failure_recall | 1.0000 | 0.6667 | 0.3333 |
