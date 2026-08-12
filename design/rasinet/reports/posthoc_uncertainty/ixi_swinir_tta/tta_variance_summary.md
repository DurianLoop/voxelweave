# IXI T2 full_test115 SwinIR TTA variance experiment

This experiment evaluates 4-view flip TTA variance as an uncertainty proxy for IXI T2 full_test115 SwinIR.

| Method / proxy | Cases | Pixel Corr | Slice Corr | AURC | MAE@50% low-U | Failure AUROC | Top-k Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| swinir_original__tta_variance | 115 | 0.5703 | 0.8571 | 4.6687 | 1.6376 | 0.9879 | 0.8333 |
| swinir_tta_mean__tta_variance | 115 | 0.5748 | 0.8557 | 4.6478 | 1.6350 | 0.9879 | 0.8333 |

## Baseline disagreement comparison

| Metric | TTA variance | Baseline disagreement | Delta |
|---|---:|---:|---:|
| pixel_corr | 0.5748 | 0.6153 | -0.0406 |
| slice_corr | 0.8557 | 0.4572 | 0.3985 |
| risk_coverage_aurc | 4.6478 | 4.4922 | 0.1556 |
| mae_50pct_low_u | 1.6350 | 1.5253 | 0.1097 |
| failure_auroc | 0.9879 | 0.9871 | 0.0008 |
| top_k_failure_recall | 0.8333 | 0.8333 | 0.0000 |
