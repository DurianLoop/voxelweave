# TTA variance cross-dataset summary

本轮实验评估 4-view flip TTA variance 作为 SwinIR 的 post-hoc uncertainty proxy。结论：TTA variance 有稳定的 slice-level 相关性优势，但在 pixel-level correlation 和 risk-coverage 上不稳定优于 `baseline_disagreement`，因此更适合放在 proxy ablation / supplementary analysis，而不是替代当前主 proxy。

| Dataset | Cases | Proxy | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall | Runtime |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| fastMRI-brain T2 | 24 | SwinIR TTA variance | 0.4786 | 0.7673 | 15.7601 | 7.0977 | 1.0000 | 1.0000 | 26.6s |
| fastMRI-brain T2 | 24 | SwinIR baseline disagreement | 0.5122 | 0.2942 | 15.6157 | 7.3133 | 1.0000 | 1.0000 | post-hoc only |
| IXI T2 full_test115 | 115 | SwinIR TTA variance | 0.5748 | 0.8557 | 4.6478 | 1.6350 | 0.9879 | 0.8333 | 663.5s |
| IXI T2 full_test115 | 115 | SwinIR baseline disagreement | 0.6153 | 0.4572 | 4.4922 | 1.5253 | 0.9871 | 0.8333 | post-hoc only |
| NingXia T2 CV | 22 | SwinIR TTA variance | 0.4033 | 0.6665 | 30.7713 | 24.4254 | 1.0000 | 1.0000 | 49.2s |
| NingXia T2 CV | 22 | SwinIR baseline disagreement | 0.4562 | 0.2758 | 30.2951 | 24.4725 | 0.9474 | 0.6667 | post-hoc only |

## Interpretation

- TTA variance consistently improves slice-level error-uncertainty correlation for SwinIR: `+0.4730` on fastMRI, `+0.3985` on IXI, and `+0.3907` on NingXia.
- TTA variance is weaker than baseline disagreement for pixel-level correlation on all three tested datasets.
- Failure detection is already saturated on fastMRI; on IXI the AUROC difference is negligible; on NingXia TTA improves AUROC and top-k recall.
- Risk-coverage does not support replacing baseline disagreement as the main proxy.
- Recommended paper placement: include TTA variance in the proxy ablation table and discussion as a stronger slice-level signal with extra inference cost.

## Artifacts

- fastMRI metrics: `rasinet/runs/posthoc_uncertainty/fastmri_swinir_tta/metrics/`
- fastMRI report: `rasinet/reports/posthoc_uncertainty/fastmri_swinir_tta/tta_variance_summary.md`
- IXI metrics: `rasinet/runs/posthoc_uncertainty/ixi_swinir_tta/metrics/`
- IXI report: `rasinet/reports/posthoc_uncertainty/ixi_swinir_tta/tta_variance_summary.md`
- NingXia metrics: `rasinet/runs/posthoc_uncertainty/ningxia_swinir_tta/metrics/`
- NingXia report: `rasinet/reports/posthoc_uncertainty/ningxia_swinir_tta/tta_variance_summary.md`
