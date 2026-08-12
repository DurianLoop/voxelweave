# fastMRI SwinIR TTA variance experiment

This experiment evaluates 4-view flip TTA variance as an uncertainty proxy for fastMRI-brain T2 SwinIR.

| Method / proxy | Cases | Pixel Corr | Slice Corr | AURC | MAE@50% low-U | Failure AUROC | Top-k Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| swinir_original__tta_variance | 1 | 0.4592 | 0.8961 | 18.0130 | 8.3036 |  | 1.0000 |
| swinir_tta_mean__tta_variance | 1 | 0.4783 | 0.9024 | 17.9984 | 8.2230 |  | 1.0000 |

## Baseline disagreement comparison

| Metric | TTA variance | Baseline disagreement | Delta |
|---|---:|---:|---:|
| pixel_corr | 0.4783 | 0.5122 | -0.0339 |
| slice_corr | 0.9024 | 0.2942 | 0.6082 |
| risk_coverage_aurc | 17.9984 | 15.6157 | 2.3828 |
| mae_50pct_low_u | 8.2230 | 7.3133 | 0.9098 |
| top_k_failure_recall | 1.0000 | 1.0000 | 0.0000 |
