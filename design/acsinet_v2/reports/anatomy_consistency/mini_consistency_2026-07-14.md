# ACSI-v2.1 Mini Consistency Screening

Date: 2026-07-14

## Scope

`mini_consistency` used the same IXI partition scale as the original mini screen: 8 training cases, 2 validation cases, and 2 held-out evaluation cases. It trained for 8 epochs with the original lightweight model (0.0637M parameters; 0.5319 GFLOPs per generated 192x192 slice), stronger z-gradient/z-Laplacian/edge-z weights, and a new adjacent-slice NCC-profile loss.

The NCC-profile loss matches the predicted adjacent-slice Pearson-NCC values to the GT values within a multi-anchor training window. Its purpose was to avoid treating arbitrary z-smoothing as anatomical consistency.

## Result

| Method | PSNR | SSIM | MAE | NCC | ZGE | ZLE | EdgeZ | NCC-z-MAE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ACSI-v2.1 | 23.9142 | 0.7656 | 54.0037 | 0.8802 | 0.02095 | 0.03199 | 0.01194 | 0.10473 |
| Linear | 23.8926 | 0.7638 | 54.6535 | 0.8756 | 0.02086 | 0.03194 | 0.01187 | 0.10246 |
| Cubic | 23.3145 | 0.7435 | 60.9144 | 0.8548 | 0.02219 | 0.03276 | 0.01266 | 0.09518 |

ACSI-v2.1 remains slightly better than linear and clearly better than cubic on the reported slice-level reconstruction values. It is better than cubic on ZGE, ZLE, and EdgeZ, but worse than cubic on NCC-z-MAE and worse than linear on all four 3D metrics.

The relevant diagnostic is the adjacent-slice NCC mean: ACSI-v2.1 `0.97949`, linear `0.97723`, cubic `0.96693`, GT `0.87477`. The model still yields an overly correlated volume. Therefore the new loss did not provide evidence for the desired anatomy-consistency claim.

## Decision

Do not run `full_test115` for this configuration. The screen fails the pre-registered gate: it does not beat both linear and cubic on at least three of the four 3D measures.

The next constructive experiment should be an ablation that isolates the cause of the high-NCC output: evaluate the saved ACSI-v2 checkpoint with (1) residual decoder only, (2) residual plus z-refinement, and (3) full loss. That is a short inference/ablation task and is more informative than increasing smoothness weights again. If the z-refinement creates the excess correlation, redesign or remove that tiny 3D head before any new full training.

## Artifacts

- `runs/mini_consistency/metrics/summary_metrics.csv`
- `runs/mini_consistency/metrics/summary_3d_consistency.csv`
- `runs/mini_consistency/metrics/per_case_3d_consistency.csv`
- `runs/mini_consistency/metrics/complexity.json`
- `runs/mini_consistency/training_history.json`
