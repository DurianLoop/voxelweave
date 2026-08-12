# ningxia_cv RASI post-hoc reliability 中文总结

说明：本页只汇总 post-hoc uncertainty 结果，不包含任何新 RASI-Net 训练结论。

## 1. 主结论

- `baseline_disagreement` 是当前最稳的 proxy：在 I3Net、HAT、SwinIR 上全像素 corr 约 `0.46-0.49`，非零脑区 corr 仍为正。
- 背景区域会抬高 pixel-level corr，因此论文表述中应优先报告 masked/nonzero 版本。
- residual-to-linear / residual-to-cubic 可以作为 sanity 或 ablation，不应作为主故事。

## 2. 全部 method/proxy 可靠性表

| 方法 | Proxy | Cases | MAE | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Failure AUPRC | Top-k recall |
|---|---|---|---|---|---|---|---|---|---|---|
| HAT | Baseline disagreement | 22 | 87.7686 | 0.4581 | 0.2671 | 30.4454 | 24.5532 | 0.9474 | 0.8333 | 0.6667 |
| HAT | Residual to cubic | 22 | 87.7686 | 0.3692 | 0.1253 | 34.4285 | 31.5114 | 0.9649 | 0.8667 | 0.6667 |
| HAT | Residual to linear | 22 | 87.7686 | 0.3818 | 0.5596 | 33.0343 | 27.1702 | 0.9474 | 0.8333 | 0.6667 |
| I3Net | Baseline disagreement | 22 | 96.0987 | 0.4856 | 0.3555 | 32.8816 | 26.1346 | 0.9474 | 0.8333 | 0.6667 |
| I3Net | Residual to cubic | 22 | 96.0987 | 0.4101 | 0.3250 | 37.8615 | 35.3750 | 0.9474 | 0.8333 | 0.6667 |
| I3Net | Residual to linear | 22 | 96.0987 | 0.4393 | 0.6627 | 36.5106 | 31.5663 | 0.9298 | 0.8095 | 0.6667 |
| SwinIR | Baseline disagreement | 22 | 87.2663 | 0.4562 | 0.2758 | 30.2951 | 24.4725 | 0.9474 | 0.8333 | 0.6667 |
| SwinIR | Residual to cubic | 22 | 87.2663 | 0.3670 | 0.1220 | 34.2311 | 31.3722 | 0.9649 | 0.8667 | 0.6667 |
| SwinIR | Residual to linear | 22 | 87.2663 | 0.3812 | 0.5569 | 32.8334 | 27.0661 | 0.9649 | 0.8667 | 0.6667 |

## 3. Proxy 对比表

| 方法 | 排名 | Proxy | Cases | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall |
|---|---|---|---|---|---|---|---|---|---|
| HAT | 1 | Baseline disagreement | 22 | 0.4581 | 0.2671 | 30.4454 | 24.5532 | 0.9474 | 0.6667 |
| HAT | 2 | Residual to linear | 22 | 0.3818 | 0.5596 | 33.0343 | 27.1702 | 0.9474 | 0.6667 |
| HAT | 3 | Residual to cubic | 22 | 0.3692 | 0.1253 | 34.4285 | 31.5114 | 0.9649 | 0.6667 |
| I3Net | 1 | Baseline disagreement | 22 | 0.4856 | 0.3555 | 32.8816 | 26.1346 | 0.9474 | 0.6667 |
| I3Net | 2 | Residual to linear | 22 | 0.4393 | 0.6627 | 36.5106 | 31.5663 | 0.9298 | 0.6667 |
| I3Net | 3 | Residual to cubic | 22 | 0.4101 | 0.3250 | 37.8615 | 35.3750 | 0.9474 | 0.6667 |
| SwinIR | 1 | Baseline disagreement | 22 | 0.4562 | 0.2758 | 30.2951 | 24.4725 | 0.9474 | 0.6667 |
| SwinIR | 2 | Residual to linear | 22 | 0.3812 | 0.5569 | 32.8334 | 27.0661 | 0.9649 | 0.6667 |
| SwinIR | 3 | Residual to cubic | 22 | 0.3670 | 0.1220 | 34.2311 | 31.3722 | 0.9649 | 0.6667 |

## 4. Baseline disagreement 方法对比表

| 排名 | 方法 | Cases | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall |
|---|---|---|---|---|---|---|---|---|
| 1 | I3Net | 22 | 0.4856 | 0.3555 | 32.8816 | 26.1346 | 0.9474 | 0.6667 |
| 2 | HAT | 22 | 0.4581 | 0.2671 | 30.4454 | 24.5532 | 0.9474 | 0.6667 |
| 3 | SwinIR | 22 | 0.4562 | 0.2758 | 30.2951 | 24.4725 | 0.9474 | 0.6667 |

## 5. Failure detection 表

| 方法 | Proxy | Cases | Failure cases | AUROC | AUPRC | Top-k recall |
|---|---|---|---|---|---|---|
| HAT | Residual to cubic | 22 | 3 | 0.9649 | 0.8667 | 0.6667 |
| SwinIR | Residual to cubic | 22 | 3 | 0.9649 | 0.8667 | 0.6667 |
| SwinIR | Residual to linear | 22 | 3 | 0.9649 | 0.8667 | 0.6667 |
| HAT | Baseline disagreement | 22 | 3 | 0.9474 | 0.8333 | 0.6667 |
| HAT | Residual to linear | 22 | 3 | 0.9474 | 0.8333 | 0.6667 |
| I3Net | Baseline disagreement | 22 | 3 | 0.9474 | 0.8333 | 0.6667 |
| I3Net | Residual to cubic | 22 | 3 | 0.9474 | 0.8333 | 0.6667 |
| SwinIR | Baseline disagreement | 22 | 3 | 0.9474 | 0.8333 | 0.6667 |
| I3Net | Residual to linear | 22 | 3 | 0.9298 | 0.8095 | 0.6667 |

## 6. Masked / nonzero 主表

| 方法 | Proxy | All pixel corr | Nonzero corr | Background corr | Nonzero-All | Background fraction |
|---|---|---|---|---|---|---|
| HAT | Baseline disagreement | 0.4581 | 0.2904 | 0.4116 | -0.1677 | 0.4094 |
| I3Net | Baseline disagreement | 0.4856 | 0.3137 | 0.5131 | -0.1718 | 0.4094 |
| SwinIR | Baseline disagreement | 0.4562 | 0.2886 | 0.3967 | -0.1676 | 0.4094 |
| HAT | Residual to cubic | 0.3692 | 0.2194 | 0.3456 | -0.1498 | 0.4094 |
| HAT | Residual to linear | 0.3818 | 0.2146 | 0.4130 | -0.1672 | 0.4094 |
| I3Net | Residual to cubic | 0.4101 | 0.2577 | 0.4320 | -0.1524 | 0.4094 |
| I3Net | Residual to linear | 0.4393 | 0.2722 | 0.4994 | -0.1671 | 0.4094 |
| SwinIR | Residual to cubic | 0.3670 | 0.2193 | 0.3302 | -0.1478 | 0.4094 |
| SwinIR | Residual to linear | 0.3812 | 0.2155 | 0.4001 | -0.1658 | 0.4094 |

## 7. 建议写法

当前更稳的表述是：在不重新训练模型的情况下，多个强插值模型之间的 baseline disagreement 可以作为低成本 failure-aware reliability signal；它与真实误差保持正相关，并能较好识别高误差 case。由于全像素结果受背景影响，主文应优先报告 nonzero/masked 版本，all-pixel 结果作为补充。
