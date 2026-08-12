# fastmri_full RASI post-hoc reliability 中文总结

说明：本页只汇总 post-hoc uncertainty 结果，不包含任何新 RASI-Net 训练结论。

## 1. 主结论

- `baseline_disagreement` 是当前最稳的 proxy：在 SwinIR、HAT、I3Net 上全像素 corr 约 `0.41-0.51`，非零脑区 corr 仍为正。
- 背景区域会抬高 pixel-level corr，因此论文表述中应优先报告 masked/nonzero 版本。
- residual-to-linear / residual-to-cubic 可以作为 sanity 或 ablation，不应作为主故事。

## 2. 全部 method/proxy 可靠性表

| 方法 | Proxy | Cases | MAE | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Failure AUPRC | Top-k recall |
|---|---|---|---|---|---|---|---|---|---|---|
| HAT | Baseline disagreement | 24 | 49.6702 | 0.4895 | 0.2850 | 15.4140 | 7.4665 | 1.0000 | 1.0000 | 1.0000 |
| HAT | Residual to cubic | 24 | 49.6702 | 0.3617 | 0.1491 | 18.8165 | 12.0459 | 0.9841 | 0.9167 | 0.6667 |
| HAT | Residual to linear | 24 | 49.6702 | 0.3728 | 0.0141 | 18.0516 | 10.2483 | 0.9841 | 0.9167 | 0.6667 |
| I3Net | Baseline disagreement | 24 | 41.0101 | 0.4138 | 0.3457 | 13.6226 | 7.1036 | 1.0000 | 1.0000 | 1.0000 |
| I3Net | Residual to cubic | 24 | 41.0101 | 0.3568 | 0.3229 | 15.4464 | 10.0887 | 1.0000 | 1.0000 | 1.0000 |
| I3Net | Residual to linear | 24 | 41.0101 | 0.3778 | 0.2456 | 14.7577 | 8.5864 | 1.0000 | 1.0000 | 1.0000 |
| SwinIR | Baseline disagreement | 24 | 52.0221 | 0.5122 | 0.2942 | 15.6157 | 7.3133 | 1.0000 | 1.0000 | 1.0000 |
| SwinIR | Residual to cubic | 24 | 52.0221 | 0.3487 | 0.1044 | 19.6383 | 12.5588 | 0.9683 | 0.8056 | 0.6667 |
| SwinIR | Residual to linear | 24 | 52.0221 | 0.3574 | -0.0204 | 18.7332 | 10.4821 | 0.9365 | 0.5889 | 0.6667 |

## 3. Proxy 对比表

| 方法 | 排名 | Proxy | Cases | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall |
|---|---|---|---|---|---|---|---|---|---|
| HAT | 1 | Baseline disagreement | 24 | 0.4895 | 0.2850 | 15.4140 | 7.4665 | 1.0000 | 1.0000 |
| HAT | 2 | Residual to linear | 24 | 0.3728 | 0.0141 | 18.0516 | 10.2483 | 0.9841 | 0.6667 |
| HAT | 3 | Residual to cubic | 24 | 0.3617 | 0.1491 | 18.8165 | 12.0459 | 0.9841 | 0.6667 |
| I3Net | 1 | Baseline disagreement | 24 | 0.4138 | 0.3457 | 13.6226 | 7.1036 | 1.0000 | 1.0000 |
| I3Net | 2 | Residual to linear | 24 | 0.3778 | 0.2456 | 14.7577 | 8.5864 | 1.0000 | 1.0000 |
| I3Net | 3 | Residual to cubic | 24 | 0.3568 | 0.3229 | 15.4464 | 10.0887 | 1.0000 | 1.0000 |
| SwinIR | 1 | Baseline disagreement | 24 | 0.5122 | 0.2942 | 15.6157 | 7.3133 | 1.0000 | 1.0000 |
| SwinIR | 2 | Residual to linear | 24 | 0.3574 | -0.0204 | 18.7332 | 10.4821 | 0.9365 | 0.6667 |
| SwinIR | 3 | Residual to cubic | 24 | 0.3487 | 0.1044 | 19.6383 | 12.5588 | 0.9683 | 0.6667 |

## 4. Baseline disagreement 方法对比表

| 排名 | 方法 | Cases | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall |
|---|---|---|---|---|---|---|---|---|
| 1 | SwinIR | 24 | 0.5122 | 0.2942 | 15.6157 | 7.3133 | 1.0000 | 1.0000 |
| 2 | HAT | 24 | 0.4895 | 0.2850 | 15.4140 | 7.4665 | 1.0000 | 1.0000 |
| 3 | I3Net | 24 | 0.4138 | 0.3457 | 13.6226 | 7.1036 | 1.0000 | 1.0000 |

## 5. Failure detection 表

| 方法 | Proxy | Cases | Failure cases | AUROC | AUPRC | Top-k recall |
|---|---|---|---|---|---|---|
| HAT | Baseline disagreement | 24 | 3 | 1.0000 | 1.0000 | 1.0000 |
| I3Net | Baseline disagreement | 24 | 3 | 1.0000 | 1.0000 | 1.0000 |
| I3Net | Residual to cubic | 24 | 3 | 1.0000 | 1.0000 | 1.0000 |
| I3Net | Residual to linear | 24 | 3 | 1.0000 | 1.0000 | 1.0000 |
| SwinIR | Baseline disagreement | 24 | 3 | 1.0000 | 1.0000 | 1.0000 |
| HAT | Residual to cubic | 24 | 3 | 0.9841 | 0.9167 | 0.6667 |
| HAT | Residual to linear | 24 | 3 | 0.9841 | 0.9167 | 0.6667 |
| SwinIR | Residual to cubic | 24 | 3 | 0.9683 | 0.8056 | 0.6667 |
| SwinIR | Residual to linear | 24 | 3 | 0.9365 | 0.5889 | 0.6667 |

## 6. Masked / nonzero 主表

| 方法 | Proxy | All pixel corr | Nonzero corr | Background corr | Nonzero-All | Background fraction |
|---|---|---|---|---|---|---|
| HAT | Baseline disagreement | 0.4895 | 0.3176 | 0.4574 | -0.1719 | 0.4324 |
| I3Net | Baseline disagreement | 0.4138 | 0.2347 | 0.3953 | -0.1791 | 0.4324 |
| SwinIR | Baseline disagreement | 0.5122 | 0.3500 | 0.4609 | -0.1622 | 0.4324 |
| HAT | Residual to cubic | 0.3617 | 0.1813 | 0.3753 | -0.1804 | 0.4324 |
| HAT | Residual to linear | 0.3728 | 0.1938 | 0.4320 | -0.1790 | 0.4324 |
| I3Net | Residual to cubic | 0.3568 | 0.1900 | 0.3380 | -0.1668 | 0.4324 |
| I3Net | Residual to linear | 0.3778 | 0.2101 | 0.3886 | -0.1677 | 0.4324 |
| SwinIR | Residual to cubic | 0.3487 | 0.1692 | 0.3621 | -0.1795 | 0.4324 |
| SwinIR | Residual to linear | 0.3574 | 0.1787 | 0.4158 | -0.1787 | 0.4324 |

## 7. 建议写法

当前更稳的表述是：在不重新训练模型的情况下，多个强插值模型之间的 baseline disagreement 可以作为低成本 failure-aware reliability signal；它与真实误差保持正相关，并能较好识别高误差 case。由于全像素结果受背景影响，主文应优先报告 nonzero/masked 版本，all-pixel 结果作为补充。
