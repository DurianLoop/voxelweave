# fastMRI SwinIR TTA variance experiment

This experiment evaluates 4-view flip TTA variance as an uncertainty proxy for fastMRI-brain T2 SwinIR.

| Method / proxy | Cases | Pixel Corr | Slice Corr | AURC | MAE@50% low-U | Failure AUROC | Top-k Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| swinir_original__tta_variance | 24 | 0.4645 | 0.7607 | 15.7742 | 7.1311 | 1.0000 | 1.0000 |
| swinir_tta_mean__tta_variance | 24 | 0.4786 | 0.7673 | 15.7601 | 7.0977 | 1.0000 | 1.0000 |

## Baseline disagreement comparison

| Metric | TTA variance | Baseline disagreement | Delta |
|---|---:|---:|---:|
| pixel_corr | 0.4786 | 0.5122 | -0.0336 |
| slice_corr | 0.7673 | 0.2942 | 0.4730 |
| risk_coverage_aurc | 15.7601 | 15.6157 | 0.1445 |
| mae_50pct_low_u | 7.0977 | 7.3133 | -0.2156 |
| failure_auroc | 1.0000 | 1.0000 | 0.0000 |
| top_k_failure_recall | 1.0000 | 1.0000 | 0.0000 |
