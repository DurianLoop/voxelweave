# IXI T2 full_test115 SwinIR TTA variance experiment

This experiment evaluates 4-view flip TTA variance as an uncertainty proxy for IXI T2 full_test115 SwinIR.

| Method / proxy | Cases | Pixel Corr | Slice Corr | AURC | MAE@50% low-U | Failure AUROC | Top-k Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| swinir_original__tta_variance | 5 | 0.5702 | 0.8854 | 7.7453 | 2.1079 | 1.0000 | 1.0000 |
| swinir_tta_mean__tta_variance | 5 | 0.5779 | 0.8880 | 7.7036 | 2.0986 | 1.0000 | 1.0000 |

## Baseline disagreement comparison

| Metric | TTA variance | Baseline disagreement | Delta |
|---|---:|---:|---:|
| pixel_corr | 0.5779 | 0.6153 | -0.0374 |
| slice_corr | 0.8880 | 0.4572 | 0.4308 |
| risk_coverage_aurc | 7.7036 | 4.4922 | 3.2114 |
| mae_50pct_low_u | 2.0986 | 1.5253 | 0.5733 |
| failure_auroc | 1.0000 | 0.9871 | 0.0129 |
| top_k_failure_recall | 1.0000 | 0.8333 | 0.1667 |
